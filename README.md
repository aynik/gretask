`gretask` 
====================

![gretask logo](https://github.com/aynik/gretask/blob/master/logo.png?raw=true)

This repository contains the source code for a task queue system that can manage and execute tasks. It consists of several modules:

*   `src/task_queue.py`: defines the `TaskQueue` class, which represents a task queue and provides methods to add tasks to the queue and acquire tasks from the queue.
*   `src/task.py`: defines the `Task` class, which represents a task to be executed and provides methods to convert the task to a dictionary.
*   `src/task_worker.py`: defines the `TaskWorker` class, which is responsible for executing tasks acquired from the task queue.
*   `src/exception.py`: defines custom exceptions used in the project.
*   `tests/test_task_queue.py`: contains unit tests for the `TaskQueue` class.
*   `tests/test_task_worker.py`: contains unit tests for the `TaskWorker` class.

Getting started
---------------

To use this task queue system, you need to have Python 3.6 or later installed on your system. You can clone this repository using the following command:

```shell
git clone https://github.com/aynik/gretask.git
```

Once you have cloned the repository, you can install the dependencies by running the following command in the root directory of the repository:

```shell
pip install -r requirements.txt
```

Or if you want to contribute to the project then install dev dependencies by running the following command:

```shell
pip install -r requirements_dev.txt
```

We recommend of course that you execute these commands on a virtual environment.

Usage
-----

To use the task queue system, you need to create an instance of the `TaskQueue` class and add tasks to the queue using the `add_task` method. You can then create an instance of the `TaskWorker` class and register task handlers for the different types of tasks using the `register_task_handler` method. Finally, you can run the task worker using the `run` method.

Here's an example usage of the task queue system:

```python
from src.task_queue import TaskQueue
from src.task_worker import TaskWorker
from src.task import Task

# Create a task queue
db_config = {
  'host': 'localhost',
  'dbname': 'testdb',
  'user': 'testuser',
  'password': 'testpass'
}
task_queue = TaskQueue(db_config)

# Add a task to the queue
task = Task('example_task', {'key': 'value'})
task_queue.add_task(task)

# Create a task worker
task_worker = TaskWorker(task_queue)

# Define a task handler
def example_task_handler(payload):
  print(payload)

# Register the task handler
task_worker.register_task_handler('example_task', example_task_handler)

# Run the task worker
task_worker.run()
```

In this example, we create a task queue using a PostgreSQL database, add a task to the queue, create a task worker, register a task handler for the `example_task` task type, and run the task worker.

Testing
-------

To run the unit tests for the `TaskQueue` class, you can run the following command in the root directory of the repository:

Copy code

`make test`

Roadmap
-------

- [x] Add more test cases to increase code coverage and ensure the correctness of the implementation.
- [ ] Implement a logging framework to provide more detailed feedback to users and developers.
- [ ] Add support for different database systems, not just PostgreSQL.
- [x] Implement a retry mechanism for failed tasks to increase task reliability.
- [x] Provide better error messages to users and developers when tasks fail.
- [ ] Implement a feature to allow users to monitor the status of their tasks.
- [ ] Add more documentation to make it easier for new developers to contribute to the project.
- [ ] Implement an API to allow users to interact with the task queue system from other applications.
- [ ] Improve the performance of the system by optimizing database queries or introducing caching mechanisms.
- [ ] Allow users to specify dependencies between tasks, so that certain tasks can only be executed after others have been completed.

Contributing
------------

If you would like to contribute to this project, you can fork the repository and submit a pull request. Before submitting a pull request, please make sure that your code follows the PEP

Copyright
------------
2023 © ChatGPT
