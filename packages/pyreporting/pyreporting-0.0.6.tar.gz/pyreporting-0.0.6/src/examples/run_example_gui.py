"""Example showing how to use Progress-enabled functions with a QT progress
bar"""

from typing import Callable

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

from examples.nested_tasks import nested_tasks
from examples.single_task import single_task
from examples.task_in_stages import task_in_stages
from examples.variable_length_task import variable_length_task
from pyreporting.progress import Progress
from pyreporting.progress_bar import ProgressBarType
from pyreporting.util import UserCancelled


class WorkerButton(QPushButton):
    """PySide button for running a worker function on a thread"""

    class Worker(QRunnable):
        """Example PySide application for illustrating progress dialogs"""

        class WorkerSignals(QObject):
            """Signals to process on main thread"""
            started = Signal()
            finished = Signal()

        def __init__(self, worker_function: Callable, *args, **kwargs):
            super().__init__()
            self.signals = WorkerButton.Worker.WorkerSignals()
            self.worker_function = worker_function
            self.args = args
            self.kwargs = kwargs

        def run(self):
            """Run the worker function"""
            self.signals.started.emit()
            try:
                self.worker_function(*self.args, **self.kwargs)
            except UserCancelled:
                pass
            finally:
                self.signals.finished.emit()

    def __init__(self, label: str, callback: Callable,
                 thread_pool: QThreadPool):
        super().__init__(label)
        self.callback = callback
        self.thread_pool = thread_pool
        self.pressed.connect(self.button_clicked)

    def button_clicked(self):
        """Respond on main thread to button press"""
        self.setEnabled(False)
        worker = WorkerButton.Worker(
            worker_function=self.callback,
        )
        worker.signals.finished.connect(self.worker_finished)
        self.thread_pool.start(worker)

    def worker_finished(self):
        """Respond on main thread to worker thread completion"""
        self.setEnabled(True)


class MainWindow(QMainWindow):
    """Example PySide application main window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Progress bar example")
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        self.thread_pool = QThreadPool()

        self.progress = Progress(progress_type=ProgressBarType.QT)

        self.layout.addWidget(WorkerButton(
            label="Single task",
            callback=lambda: single_task(progress=self.progress),
            thread_pool=self.thread_pool
        ))
        self.layout.addWidget(WorkerButton(
            label="Task with unknown length",
            callback=lambda: variable_length_task(self.progress),
            thread_pool=self.thread_pool
        ))
        self.layout.addWidget(WorkerButton(
            label="Task in stages",
            callback=lambda: task_in_stages(self.progress),
            thread_pool=self.thread_pool
        ))
        self.layout.addWidget(WorkerButton(
            label="Nested tasks",
            callback=lambda: nested_tasks(self.progress),
            thread_pool=self.thread_pool
        ))


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
