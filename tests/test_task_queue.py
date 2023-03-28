import unittest
from textwrap import dedent
from datetime import datetime, timezone, timedelta
from unittest.mock import call, patch, MagicMock

from src.task_queue import TaskQueue
from src.task import Task


class TestTaskQueue(unittest.TestCase):
    def setUp(self):
        self.db_config = {
            "host": "localhost",
            "dbname": "testdb",
            "user": "testuser",
            "password": "testpass",
        }
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.mock_psycopg2 = MagicMock()
        self.mock_psycopg2.connect.return_value = self.mock_conn
        self.patcher = patch("src.task_queue.psycopg2", self.mock_psycopg2)
        self.patcher.start()
        self.task_queue = TaskQueue(self.db_config)

    def tearDown(self):
        self.task_queue.cur.close()
        self.task_queue.conn.close()
        self.patcher.stop()

    def test_add_task(self):
        # Test adding a task to the task queue
        task = Task(
            "example_task",
            {"key": "value"},
            acquire_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        self.task_queue.add_task(task)
        self.assertEqual(len(self.task_queue.cur.mock_calls), 3)
        self.assertEqual(
            self.task_queue.cur.mock_calls[2],
            # fmt: off
            call.execute(dedent("""
                INSERT INTO gretask_tasks (name, payload, reschedule, acquire_at)
                VALUES (%s, %s, %s, %s)
            """).strip("\n"), (
                "example_task",
                '{"key": "value"}',
                None,
                datetime(2023, 1, 1, tzinfo=timezone.utc),
            )),
            # fmt: on
        )

    def test_acquire_task(self):
        # Test acquiring a task from the task queue
        next_acquire_at = datetime(2023, 1, 1, tzinfo=timezone.utc) + timedelta(
            seconds=10
        )
        self.mock_cursor.reset_mock()
        self.mock_cursor.rowcount = 1
        self.mock_cursor.fetchone.return_value = (
            1,
            "example_task",
            '{"key": "value"}',
            None,
            "2023-01-01T00:00:00.000Z",
        )
        task = self.task_queue.acquire_task()
        self.mock_cursor.execute.assert_has_calls(
            [
                # fmt: off
                call(dedent("""
                    SELECT *
                    FROM gretask_tasks
                    WHERE acquire_at <= NOW()
                    ORDER BY acquire_at, id
                    LIMIT 1
                """).strip("\n")),
                call(dedent("""
                    UPDATE gretask_tasks
                    SET acquire_at = %s
                    WHERE id = %s AND acquire_at = %s
                """).strip("\n"), (
                    next_acquire_at,
                    1,
                    datetime(2023, 1, 1, tzinfo=timezone.utc),
                )),
                # fmt: on
            ]
        )
        self.task_queue.conn.commit.assert_called()
        self.assertEqual(task.acquire_at, next_acquire_at)

    def test_select_no_task(self):
        # Test acquiring no task from the task queue
        self.mock_cursor.reset_mock()
        self.task_queue.conn.commit.reset_mock()
        task = self.task_queue.acquire_task()
        self.assertEqual(len(self.mock_cursor.execute.mock_calls), 1)
        self.mock_cursor.execute.assert_has_calls(
            [
                # fmt: off
                call(dedent("""
                    SELECT *
                    FROM gretask_tasks
                    WHERE acquire_at <= NOW()
                    ORDER BY acquire_at, id
                    LIMIT 1
                """).strip("\n")),
                # fmt: on
            ]
        )
        self.task_queue.conn.commit.assert_not_called()
        self.assertEqual(task, None)

    def test_acquire_no_task(self):
        # Test acquiring no task from the task queue
        self.mock_cursor.reset_mock()
        self.task_queue.conn.commit.reset_mock()
        self.mock_cursor.rowcount = 0
        self.mock_cursor.fetchone.return_value = (
            1,
            "example_task",
            '{"key": "value"}',
            None,
            "2023-01-01T00:00:00.000Z",
        )
        task = self.task_queue.acquire_task()
        self.assertEqual(len(self.mock_cursor.execute.mock_calls), 2)
        self.mock_cursor.execute.assert_has_calls(
            [
                # fmt: off
                call(dedent("""
                    SELECT *
                    FROM gretask_tasks
                    WHERE acquire_at <= NOW()
                    ORDER BY acquire_at, id
                    LIMIT 1
                """).strip("\n")),
                # fmt: on
            ]
        )
        self.task_queue.conn.commit.assert_called()
        self.assertEqual(task, None)


if __name__ == "__main__":
    unittest.main()
