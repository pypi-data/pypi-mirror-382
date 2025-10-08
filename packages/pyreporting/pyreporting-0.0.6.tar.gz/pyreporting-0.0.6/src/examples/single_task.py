"""Example function for pyreporting progress"""
from time import sleep

from pyreporting.progress import Progress


def single_task(progress: Progress):
    """Example function showing how to use Progress in a simple loop"""

    progress.start_progress(label="Executing task")

    for value in range(100):
        # Update progress
        progress.update_progress(value=value)

        # Do some work...
        sleep(0.01)

    progress.complete_progress()
