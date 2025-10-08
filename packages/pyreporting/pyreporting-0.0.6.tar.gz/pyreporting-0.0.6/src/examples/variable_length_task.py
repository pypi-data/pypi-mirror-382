"""Example function for pyreporting progress"""
from time import sleep

from pyreporting.progress import Progress


def variable_length_task(progress: Progress):
    """Example function showing how to use Progress where the number of steps
    is unknown"""

    progress.start_progress(label="Executing task")

    for _ in range(154):
        # Do some work...
        sleep(0.01)

    progress.complete_progress()
