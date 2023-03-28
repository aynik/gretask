import unittest
from datetime import datetime, timezone
from textwrap import dedent
from unittest.mock import patch, MagicMock

from src.exception import TaskException
from src.task_worker import TaskWorker
from src.task_queue import TaskQueue
from src.task import Task


class TestTaskWorker(unittest.TestCase):
    def setUp(self):
        self.task_queue = MagicMock(spec=TaskQueue)
        self.task_queue.conn = MagicMock()
        self.task_worker = TaskWorker(self.task_queue)

    def test_register_task_handler(self):
        # Test the registration of a task handler
        def test_task_handler(_payload: dict) -> None:
            pass

        self.task_worker.register_task_handler("test_task", test_task_handler)
        self.assertIn("test_task", self.task_worker.task_handlers)
        self.assertEqual(self.task_worker.task_handlers["test_task"], test_task_handler)

    def test_run_success(self):
        # Test the successful execution of a task handler
        self.task_queue.acquire_task = MagicMock(
            return_value=Task(
                id_=1,
                name="test_task",
                payload={"key": "value"},
                reschedule=None,
                acquire_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            )
        )

        self.task_queue.cur = MagicMock()
        self.task_queue.conn = MagicMock()

        def succeeding_task_handler(_payload: dict) -> None:
            self.task_queue.acquire_task = MagicMock(return_value=None)
            self.task_worker.stop = True

        self.task_worker.register_task_handler("test_task", succeeding_task_handler)
        self.task_worker.run()
        # fmt: off
        self.task_queue.cur.execute.assert_called_once_with(dedent("""
            DELETE FROM gretask_tasks
            WHERE id = %s
        """).strip("\n"), (1,))
        # fmt: on
        self.task_queue.conn.commit.assert_called_once()

    def test_run_exception(self):
        # Test the handling of a task failure
        self.task_queue.acquire_task = MagicMock(
            return_value=Task(
                id_=1,
                name="test_task",
                payload={"key": "value"},
                reschedule=None,
                acquire_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            )
        )

        self.task_queue.cur = MagicMock()
        self.task_queue.conn = MagicMock()

        def failing_task_handler(_payload: dict) -> None:
            self.task_queue.acquire_task = MagicMock(return_value=None)
            self.task_worker.stop = True
            raise TaskException("Task failed")

        self.task_worker.register_task_handler("test_task", failing_task_handler)
        with patch("logging.error") as _mock_logging_error:
            self.task_worker.run()

        # fmt: off
        self.task_queue.cur.execute.assert_called_once_with(dedent("""
            DELETE FROM gretask_tasks
            WHERE id = %s
        """).strip("\n"), (1,))
        # fmt: on
        self.task_queue.conn.commit.assert_called_once()

    def test_run_wait(self):
        # Test the successful execution of a task handler
        self.task_queue.acquire_task.return_value = None

        def stopper():
            self.task_worker.stop = True

        self.task_queue.acquire_task.side_effect = stopper
        self.task_queue.cur = MagicMock()
        self.task_queue.conn = MagicMock()
        self.task_worker.run()


if __name__ == "__main__":
    unittest.main()
