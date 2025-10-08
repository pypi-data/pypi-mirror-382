"""Example function for pyreporting progress"""
from time import sleep

from pyreporting.progress import Progress


def task_in_stages(progress: Progress):
    """Example function showing how to use Progress in a multi-stage task"""

    progress.start_progress(label="Executing task")
    num_stages = 5

    for stage in range(num_stages):
        # Update progress
        progress.update_progress_stage(
            stage=stage,
            num_stages=num_stages,
            label=f"Executing stage {stage + 1}"
        )

        # Do some work...
        sleep(0.5)

    progress.complete_progress()
