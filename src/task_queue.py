import json
import psycopg2
from datetime import datetime, timedelta
from textwrap import dedent
from typing import Optional, Any

from src.task import Task


class TaskQueue:
    def __init__(self, db_config: Any):
        self.conn = psycopg2.connect(**db_config)
        self.cur = self.conn.cursor()
        # fmt: off
        self.cur.execute(dedent("""
            CREATE TABLE IF NOT EXISTS gretask_tasks (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                payload JSON NOT NULL,
                reschedule BIGINT,
                acquire_at TIMESTAMP NOT NULL
            )
        """).strip("\n")) 
        # fmt: off
        self.cur.execute(dedent("""
            CREATE INDEX
            IF NOT EXISTS gretask_tasks_acquire_at_idx
            ON gretask_tasks (acquire_at)
        """).strip("\n"))
        # fmt: on
        self.conn.commit()

    def add_task(self, task: Task) -> None:
        """Add a task to the task queue.

        Args:
            task (Task): The task object to add to the task queue.
        """
        # fmt: off
        self.cur.execute(dedent("""
            INSERT INTO gretask_tasks (name, payload, reschedule, acquire_at)
            VALUES (%s, %s, %s, %s)
        """).strip("\n"), (task.name, json.dumps(task.payload), task.reschedule, task.acquire_at))
        # fmt: on
        self.conn.commit()

    def acquire_task(self) -> Optional[Task]:
        """Acquire a task from the task queue.

        Returns:
            Optional[Task]: The next task to process if available, otherwise None.
        """
        # fmt: off
        self.cur.execute(dedent("""
            SELECT *
            FROM gretask_tasks
            WHERE acquire_at <= NOW()
            ORDER BY acquire_at, id
            LIMIT 1
        """).strip("\n"))
        # fmt: on
        task_row = self.cur.fetchone()

        if not task_row or len(task_row) == 0:
            return None

        id_, name, payload, reschedule, acquire_at = task_row
        task = Task(
            id_=id_,
            name=name,
            payload=payload,
            reschedule=reschedule,
            acquire_at=datetime.strptime(acquire_at, "%Y-%m-%dT%H:%M:%S.%f%z"),
        )
        next_acquire_at = task.acquire_at + timedelta(seconds=10)
        # fmt: off
        self.cur.execute(dedent("""
            UPDATE gretask_tasks
            SET acquire_at = %s
            WHERE id = %s AND acquire_at = %s
        """).strip("\n"), (next_acquire_at, task.id, task.acquire_at))
        # fmt: on
        self.conn.commit()
        if self.cur.rowcount == 1:
            task.acquire_at = next_acquire_at
            return task

        return None
