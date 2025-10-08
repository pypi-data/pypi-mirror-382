"""Example function for pyreporting progress"""
from time import sleep

from examples.single_task import single_task
from pyreporting.progress import Progress


def nested_tasks(progress: Progress):
    """Example function showing how to use Progress with a number of nested
    tasks"""
    progress.start_progress(label="Executing task", title="Nested tasks")

    for stage in range(5):
        progress.update_progress_stage(
            stage=stage,
            num_stages=5,
            label=f"Starting stage {stage + 1}",
            title=f"Stage {stage + 1}"
        )
        sleep(0.5)
        single_task(progress=progress)
        progress.update_progress(
            label=f"Completing stage {stage + 1}",
        )
        sleep(0.5)
    progress.complete_progress()
