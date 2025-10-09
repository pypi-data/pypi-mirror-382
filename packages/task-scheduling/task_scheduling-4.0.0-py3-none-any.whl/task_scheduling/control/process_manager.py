# -*- coding: utf-8 -*-
# Author: fallingmeteorite
import os
import threading
import time
from typing import Dict, Any
from multiprocessing.managers import DictProxy

from ..common import logger
from ..config import config


class ProcessTaskManager:
    __slots__ = ['_tasks',
                 '_operation_lock',  # Lock for dictionary operations
                 '_task_queue',
                 '_start',
                 '_main_task_id'
                 ]

    def __init__(self, task_queue: DictProxy) -> None:
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._operation_lock = threading.Lock()  # Lock for thread-safe dictionary operations
        self._task_queue = task_queue
        self._start: bool = True
        self._start_monitor_thread()  # Start the monitor thread
        self._main_task_id = None  # Main thread

    def add(self, terminate_obj: Any, pause_ctx: Any, task_id: str) -> None:
        """
        Add task control objects to the dictionary.
        :param terminate_obj: An object that has a terminate method.
          :param pause_ctx: An object that has a pause method.
        :param task_id: Task ID, used as the key in the dictionary.
        """
        with self._operation_lock:  # Lock for thread-safe dictionary access
            if task_id in self._tasks:
                if pause_ctx is not None:
                    self._tasks[task_id]['terminate'] = terminate_obj
                if pause_ctx is not None:
                    self._tasks[task_id]['pause'] = pause_ctx
            else:
                self._tasks[task_id] = {
                    'terminate': terminate_obj,
                    'pause': pause_ctx
                }
                if self._main_task_id is None:
                    self._main_task_id = task_id

    def remove(self, task_id: str) -> None:
        """
        Remove the task and its associated data from the dictionary based on task_id.
        :param task_id: Task ID.
        """
        with self._operation_lock:  # Lock for thread-safe dictionary access
            if task_id in self._tasks:
                del self._tasks[task_id]
                if not self._tasks:  # Check if the tasks dictionary is empty
                    logger.debug(f"Worker {os.getpid()} no tasks remaining, stopping the monitor thread")
                    self._start = False  # If tasks dictionary is empty, stop the loop

    def check(self, task_id: str) -> bool:
        """
        Check if the given task_id exists in the dictionary.
        :param task_id: Task ID.
        :return: True if the task_id exists, otherwise False.
        """
        with self._operation_lock:  # Lock for thread-safe dictionary access
            return task_id in self._tasks

    def wait(self) -> None:
        """
        Blocking the main thread from ending while a child thread has not finished leads to errors.
        """
        # Prevent errors caused by branch threads still running after the main thread ends
        while True:
            if threading.active_count() <= 2:
                break
            time.sleep(0.1)

    def terminate_task(self, task_id: str) -> None:
        """
        Terminate the task based on task_id.
        :param task_id: Task ID.
        """
        with self._operation_lock:  # Lock for thread-safe dictionary access
            if task_id in self._tasks:
                try:
                    self._tasks[task_id]['terminate'].terminate()  # Perform the terminate operation outside the lock
                except Exception as error:
                    logger.error(f"Error terminating task '{task_id}': {error}")

            else:
                logger.warning(f"No task found with task_id '{task_id}', operation invalid")

    def terminate_branch_task(self) -> None:
        """
        Terminate the all tasks based on task_id.
        """
        with self._operation_lock:  # Lock for thread-safe dictionary access
            _tasks_copy = self._tasks.copy()  # Copy the dictionary for modification
            for task_id in self._tasks:
                if not task_id == self._main_task_id:
                    try:
                        # First check whether the task is paused, then send the termination signal.
                        if config["thread_management"]:
                            try:
                                self._tasks[task_id]['pause'].resume()
                            except RuntimeError:
                                pass
                            self._tasks[task_id]['terminate'].terminate()

                        del _tasks_copy[task_id]
                    except Exception as error:
                        logger.error(f"Error terminating task '{task_id}': {error}")

            # Replace the processed dictionary
            self._tasks = _tasks_copy

    def pause_task(self, task_id: str) -> None:
        """
        Pause the task based on task_id.
        :param task_id: Task ID.
        """
        with self._operation_lock:  # Lock for thread-safe dictionary access
            if task_id in self._tasks:
                try:
                    self._tasks[task_id]['pause'].pause()
                    logger.warning(f"task | {task_id} | paused")
                except Exception as error:
                    logger.error(error)

            else:
                logger.warning(f"No task found with task_id '{task_id}', operation invalid")

    def resume_task(self, task_id: str) -> None:
        """
        Resume the task based on task_id.

        :param task_id: Task ID.
        """
        with self._operation_lock:  # Lock for thread-safe dictionary access
            if task_id in self._tasks:
                try:
                    self._tasks[task_id]['pause'].resume()
                    logger.warning(f"task | {task_id} | resumed")
                except RuntimeError:
                    pass
                except Exception as error:
                    logger.error(error)
            else:
                logger.warning(f"No task found with task_id '{task_id}', operation invalid")

    def _start_monitor_thread(self) -> None:
        """
        Start a thread to monitor the task queue and inject exceptions into task threads if the task_id matches.
        """
        threading.Thread(target=self._monitor_task_queue, daemon=True).start()

    def _monitor_task_queue(self) -> None:
        while self._start:
            try:
                # Determine whether it is empty
                if self._task_queue.items():

                    # Make a copy to test
                    task_id, target = self._task_queue.items()[0]

                    if self.check(task_id):  # Check if the task_id exists in the dictionary

                        # Delete parameters that passed the check
                        del self._task_queue[task_id]

                        # Perform operations in order to prevent mistakes in the steps.
                        for action in target:
                            if action == "kill":
                                self.terminate_task(task_id)  # Terminate the task if it exists
                            if action == "pause":
                                self.pause_task(task_id)  # Pause the task if it exists
                            if action == "resume":
                                self.resume_task(task_id)  # Resume the task if it exists

                            with self._operation_lock:  # Lock for thread-safe dictionary access
                                if not self._tasks:  # Check if the tasks dictionary is empty
                                    logger.debug(
                                        f"Worker {os.getpid()} no tasks remaining, stopping the monitor thread")
                                    break  # Stop the loop if tasks dictionary is empty

            # Prevent race conditions between processes from causing the dictionary to become empty
            except IndexError:
                pass
            except Exception as error:
                logger.error(f"Error in monitor thread: {error}")
            finally:
                time.sleep(0.1)
