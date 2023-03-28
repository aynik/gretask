import time
import logging
from textwrap import dedent
from typing import Callable, Dict, Any

from src.exception import TaskException
from src.task_queue import TaskQueue


class TaskWorker:
    def __init__(self, task_queue: TaskQueue):
        self.task_queue = task_queue
        self.task_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        self.stop = False

    def register_task_handler(
        self, name: str, task_handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Register a task handler function for a given task name.

        Args:
            name (str): The name of the task.
            task_handler (Callable[[Dict[str, Any]], None]): The function to handle the task.
        """
        self.task_handlers[name] = task_handler

    def run(self) -> None:
        """Run the task worker, acquiring and processing tasks from the task queue."""
        while not self.stop:
            task = self.task_queue.acquire_task()
            if task:
                name, payload, reschedule, acquire_at, id_ = task.__dict__.values()
                # fmt: off
                task_info = (
                    "id=%s, name=%s, payload=%s, reschedule=%s, acquire_at=%s"
                    % (id_, name, payload, reschedule, acquire_at,)
                )
                # fmt: on
                try:
                    logging.info("Running task: %s", task_info)
                    self.task_handlers[task.name](task.payload)
                    logging.info("Task succeeded: %s", task_info)
                except TaskException as e:
                    logging.error("Task failed: %s, error=%s", task_info, e)
                # fmt: off
                self.task_queue.cur.execute(dedent("""
                    DELETE FROM gretask_tasks
                    WHERE id = %s
                """).strip("\n"), (task.id,))
                # fmt: on
                self.task_queue.conn.commit()
            else:
                time.sleep(1)
