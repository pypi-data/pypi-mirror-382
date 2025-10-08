"""Example showing how to use Progress-enabled functions with a terminal
progress bar"""
from examples.nested_tasks import nested_tasks
from examples.single_task import single_task
from examples.task_in_stages import task_in_stages
from examples.variable_length_task import variable_length_task
from pyreporting.progress import Progress
from pyreporting.progress_bar import ProgressBarType


def run_terminal_input():
    """Example showing how to use Progress-enabled functions with a terminal
    progress bar"""
    progress = Progress(progress_type=ProgressBarType.TERMINAL)
    key = None
    while key != 'q':
        print("Enter example number:")
        print("[1]: Single Task")
        print("[2]: Task with unknown length")
        print("[3]: Task in stages")
        print("[4]: Nested tasks")
        print("[q]: Quit")
        key = input()
        if key == "1":
            single_task(progress)
        elif key == "2":
            variable_length_task(progress)
        elif key == "3":
            task_in_stages(progress)
        elif key == "4":
            nested_tasks(progress)


if __name__ == "__main__":
    run_terminal_input()
