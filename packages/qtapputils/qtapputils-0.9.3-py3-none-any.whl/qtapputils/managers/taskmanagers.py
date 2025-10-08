# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © QtAppUtils Project Contributors
# https://github.com/jnsebgosselin/apputils
#
# This file is part of QtAppUtils.
# Licensed under the terms of the MIT License.
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any
if TYPE_CHECKING:
    from uuid import UUID

# ---- Standard imports
from collections import OrderedDict
import uuid
from time import sleep

# ---- Third party imports
from qtpy.QtCore import QObject, QThread, Signal, Qt

# ---- Local imports
from qtapputils.qthelpers import qtwait


class WorkerBase(QObject):
    """
    A worker to execute tasks without blocking the GUI.
    """
    sig_task_completed = Signal(object, object)

    def __init__(self):
        super().__init__()
        self._tasks: OrderedDict[Any, tuple[str, tuple, dict]] = OrderedDict()

    def _get_method(self, task: str):
        # Try direct, then fallback to underscore-prefixed (for backward
        # compatibility with older version of qtapputils).
        try:
            method = getattr(self, task)
        except AttributeError:
            method = getattr(self, '_' + task)
        return method

    def add_task(self, task_uuid4: Any, task: str, *args, **kargs):
        """
        Add a task to the stack.
        Parameters
        ----------
        task_uuid4 : UUID or any hashable
            Unique ID for the task.
        task : str
            The name of the method to execute.
        *args, **kargs :
            Arguments for the task.
        """
        self._tasks[task_uuid4] = (task, args, kargs)

    def run_tasks(self):
        """Execute the tasks that were added to the stack."""
        for task_uuid4, (task, args, kargs) in self._tasks.items():
            if task is not None:
                method_to_exec = self._get_method(task)
                returned_values = method_to_exec(*args, **kargs)
            else:
                returned_values = args
            self.sig_task_completed.emit(task_uuid4, returned_values)

        self._tasks.clear()


class TaskManagerBase(QObject):
    """
    A basic FIFO (First-In, First-Out) task manager.
    """
    sig_run_tasks_started = Signal()
    sig_run_tasks_finished = Signal()

    def __init__(self, verbose: bool = False):
        super().__init__()
        self.verbose = verbose

        self._worker = None
        self._thread_is_quitting = False

        self._task_callbacks: dict[uuid.UUID, Callable] = {}
        self._task_data: dict[uuid.UUID, tuple[str, tuple, dict]] = {}

        self._running_tasks = []
        self._queued_tasks = []
        self._pending_tasks = []
        # Queued tasks are tasks whose execution has not been requested yet.
        # This happens when we want the Worker to execute a list of tasks
        # in a single run. All queued tasks are dumped in the list of pending
        # tasks when `run_task` is called.
        #
        # Pending tasks are tasks whose execution was postponed due to
        # the fact that the worker was busy. These tasks are run as soon
        # as the worker becomes available.
        #
        # Running tasks are tasks that are being executed by the worker.

    @property
    def is_running(self):
        return len(self._running_tasks + self._pending_tasks) > 0

    def wait(self):
        """
        Waits for completion of all running and pending tasks, and for the
        worker thread to fully exit its event loop.

        Note: This does not block the main GUI event loop, allowing the UI to
        remain responsive while waiting.
        """
        qtwait(lambda: not self.is_running and not self._thread.isRunning())

    def run_tasks(
            self, callback: Callable = None, returned_values: tuple = None):
        """
        Execute all the tasks that were added to the stack.

        Parameters
        ----------
        callback : Callable, optional
            A callback that will be called with the provided returned_values
            after the current queued tasks have been all executed.
        returned_values : tuple, optional
            A list of values that will be passed to the callback function when
            it is called.
        """
        if callback is not None:
            self.add_task(None, callback, returned_values)
        self._run_tasks()

    def add_task(self, task: str, callback: Callable, *args, **kargs):
        """Add a new task at the end of the queued tasks stack."""
        self._add_task(task, callback, *args, **kargs)

    def worker(self) -> WorkerBase:
        """Return the worker that is installed on this manager."""
        return self._worker

    def set_worker(self, worker: WorkerBase):
        """"Install the provided worker on this manager"""
        self._thread = QThread()
        self._worker = worker

        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run_tasks)
        self._thread.finished.connect(self._handle_thread_finished)

        self._worker.sig_task_completed.connect(self._handle_task_completed)

    # ---- Private API
    def _handle_task_completed(
            self, task_uuid4: uuid.UUID, returned_values: tuple) -> None:
        """
        Handle when a task has been completed by the worker.

        This is the ONLY slot that should be called after a task is
        completed by the worker.
        """
        # Execute the callback associated with this task (if one exists).
        callback = self._task_callbacks.get(task_uuid4)
        if callback is not None:
            try:
                callback(*returned_values)
            except TypeError:
                # This means there is 'returned_values' is None.
                callback()

        # Remove references to the completed task from internal structures.
        self._cleanup_task(task_uuid4)

        # When all running task are completed, we quit the thread to ensure
        # all resources are cleaned up and to prevent issues with lingering
        # events or stale object references. This makes the worker lifecycle
        # more robust, especially in PyQt/PySide, and avoids subtle bugs that
        # can arise from reusing threads across multiple batches.
        if len(self._running_tasks) == 0:
            self._thread_is_quitting = True
            self._thread.quit()
            # NOTE: After 'quit()' is called, the thread's event loop exits
            # after processing pending events, and the 'QThread.finished'
            # signal is emitted. This triggers '_handle_thread_finished()',
            # which manages pending tasks or signals that all work is done.

    def _handle_thread_finished(self):
        """
        Handle when the thread event loop is shut down.
        """
        self._thread_is_quitting = False

        # If there are pending tasks, begin processing them.
        if len(self._pending_tasks) > 0:
            self._run_pending_tasks()
        else:
            # No pending tasks remain; notify listeners that
            # all tasks are finished.
            if self.verbose:
                print('All pending tasks were executed.')
            self.sig_run_tasks_finished.emit()

    def _cleanup_task(self, task_uuid4: uuid.UUID):
        """Cleanup task associated with the specified UUID."""
        del self._task_callbacks[task_uuid4]
        del self._task_data[task_uuid4]
        if task_uuid4 in self._running_tasks:
            self._running_tasks.remove(task_uuid4)

    def _add_task(self, task: str, callback: Callable, *args, **kargs):
        """Add a new task at the end of the stack of queued tasks."""
        task_uuid4 = uuid.uuid4()
        self._task_callbacks[task_uuid4] = callback
        self._queued_tasks.append(task_uuid4)
        self._task_data[task_uuid4] = (task, args, kargs)

    def _run_tasks(self):
        """
        Execute all the tasks that were added to the stack of queued tasks.
        """
        self._pending_tasks.extend(self._queued_tasks)
        self._queued_tasks = []
        if len(self._running_tasks) == 0:
            self.sig_run_tasks_started.emit()
        self._run_pending_tasks()

    def _run_pending_tasks(self):
        """Execute all pending tasks."""
        # If the worker is currently processing tasks, defer execution of
        # pending tasks.
        if len(self._running_tasks) > 0:
            return

        # If there are no pending tasks, nothing to do.
        if len(self._pending_tasks) == 0:
            return

        if self._thread_is_quitting:
            return

        if self.verbose:
            print(f'Executing {len(self._pending_tasks)} pending tasks...')

        # Move all pending tasks to the running tasks queue.
        self._running_tasks = self._pending_tasks.copy()
        self._pending_tasks = []

        # Add each running task to the worker's queue.
        for task_uuid4 in self._running_tasks:
            task, args, kargs = self._task_data[task_uuid4]
            self._worker.add_task(task_uuid4, task, *args, **kargs)

        # Start the thread so the worker can process the tasks.
        self._thread.start()


class LIFOTaskManager(TaskManagerBase):
    """
    A last-in, first out (LIFO) task manager manager, where there's always
    at most one task in the queue, and if a new task is added, it overrides
    or replaces the existing task.
    """

    def _add_task(self, task: Callable, callback, *args, **kargs):
        """
        Override method so that the tasks are managed as a LIFO
        stack (Last-in, First out) instead of FIFO (First-In, First-Out).
        """
        for task_uuid4 in self._pending_tasks:
            self._cleanup_task(task_uuid4)
        self._queued_tasks = []
        self._pending_tasks = []
        super()._add_task(task, callback, *args, **kargs)
