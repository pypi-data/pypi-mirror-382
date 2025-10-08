"""Display progress to the user as a GUI or terminal progress bar.
This abstraction means the progress reporting is decided by the caller not the
function itself. Also supports nested progress updates"""

from dataclasses import dataclass

from pyreporting.progress_bar import ProgressBar, ProgressBarType
from pyreporting.util import UserCancelled


class Progress:
    """Handler for a progress bar supporting nested progress reporting

    The Reporting class uses this class to display and update_progress a
    progress bar and associated text. The actual progress bar is created
    using the ProgressBar object - this object is either passed in directly, or
    specified as a ProgressBarType enum which is used to construct a suitable
    ProgressBar object. This allows for a terminal-based or PySide QT dialog,
    or you can implement your own custom ProgressBar class.
    """

    def __init__(self,
                 progress_type: ProgressBarType or ProgressBar,
                 parent=None):
        """Create Progress object for handling progress bar

        Args:
            progress_type: Type of progress bar. Specify one of the
                           ProgressBarType enum to create a standard type of
                           progress bar, or implement your own by providing a
                           factory object implementing ProgressBarFactory
            parent: For GUI progress bar, the parent object
        """
        if not isinstance(progress_type, (ProgressBar, ProgressBarType)):
            raise ValueError("progress_type should be a ProgressBar or "
                             "ProgressBarType enum")

        if isinstance(progress_type, ProgressBarType):
            self.progress_bar = progress_type.make(parent=parent)
        else:
            self.progress_bar = progress_type
        self.stack = ProgressStack()
        self.last_label = None
        self.last_title = None
        self.last_value = None

    def __del__(self):
        self.reset_progress()

    def start_progress(self,
                       value: int or None = None,
                       step: int or None = None,
                       label: str or None = None,
                       title: str or None = None):
        """Initialise and show progress dialog reporting. If a progress
        dialog is already visible, creates a nested progress level.

        Each start_progress() call must be matched by exactly one
        complete_progress() call

        Args:
            value: Current progress bar value, or set to None for a continuous
                   progress bar (if supported)
            step:  Percentage difference between progress calls. This is used
                   when calling advance_progress() and for correctly updating
                   nested progress calls
            label: Text to display in progress bar, or None to keep current
                   or default label
            title: Title text for the progress dialog, or None to keep current
                   or default title
        """

        # Add another level of progress to the stack
        self.stack.push()

        self.update_progress(
            value=value,
            step=step,
            label=label,
            title=title
        )

    def complete_progress(self):
        """Complete the current progress dialog. If there are no other progress
        bars currently nested then hide the dialog, otherwise return to the
        parent progress and complete the current stage"""
        if not self.stack.is_empty():
            self.update_progress(value=100)
            self.stack.pop()
            if self.stack.is_empty():
                self._close_bar()
            else:
                self.stack.advance()
                self._update_bar()

    def update_progress(self,
                        value: int or None = None,
                        step: int or None = None,
                        label: str or None = None,
                        title: str or None = None):
        """Update values in the progress dialog

        Unspecified parameters for value, label or title will retain their
        previous value.

        If step is not specified, it will be computed automatically from the
        difference between previous value updates. The step is used with
        nested progress (push_progress and pop_progress) so that the range
        of the nested progress will run between value and value + step

        Args:
            value: Current progress bar value, or set to None for a continuous
                   progress bar (if supported)
            step:  Percentage difference between progress calls. Used
                   if using advance_progress() and for correctly updating
                   nested progress calls. Computed automatically when using
                   update_progress_stage
            label: Text to display in progress bar, or None to keep current
                   or default label
            title: Title text for the progress dialog, or None to keep current
                   or default title
        """

        # If the stack is empty it means that start_progress() was not called.
        # In this case we initialise the stack progress with default values
        if self.stack.is_empty():
            self.stack.push()

        # Update the current nested values in the progress stack
        self.stack.update(
            value=value,
            step=step,
            label=label,
            title=title
        )
        # Update the actual progress bar
        self._update_bar()

    def advance_progress(self,
                         step: int or None = None,
                         label: str or None = None,
                         title: str or None = None):
        """Move the progress bar along one stage

        Unspecified parameters for step, label or title will retain their
        previous value.

        If step has not been specified in this call or in any previous call
        for this nested progress bar, it will take an inferred value (if
        one could be computed), otherwise it will be the difference between
        the current value (0 if unspecified) and 100%

        Args:
            step:  Percentage difference between progress calls. None to keep
                   current step value
            label: Text to display in progress bar, or None to keep current
                   or default label
            title: Title text for the progress dialog, or None to keep current
                   or default title
        """

        # If the stack is empty it means that start_progress() was not called.
        # In this case we initialise the stack progress with default values
        if self.stack.is_empty():
            self.stack.push()

        # Update the current nested values in the progress stack
        self.stack.update(
            value=None,
            step=step,
            label=label,
            title=title
        )
        # Advance the progress by the step amount
        self.stack.advance()

        # Update the actual progress bar
        self._update_bar()

    def update_progress_stage(self,
                              stage: int,
                              num_stages: int,
                              label: str or None = None,
                              title: str or None = None):
        """Update progress for an operation consisting of a set number of stages

        Specify the total number of stages to be performed and the current
        stage number. The value and step will be computed automatically

        Unspecified parameters for label or title will retain their
        previous value

        Args:
            stage: The index of the current stage
            num_stages: Total number of stages
            label: The label text to display by the progress, or None to keep
                   current text
            title: The title of the progress dialog, or None to keep current
                   text
        """
        self.update_progress(
            value=round(100*stage/num_stages),
            step=round(100/num_stages),
            label=label,
            title=title
        )

    def has_been_cancelled(self) -> bool:
        """Return True if the user has clicked Cancel in the progress dialog"""
        return self.progress_bar.cancel_clicked()

    def check_for_cancel(self):
        """Raise Cancel exception if user has clicked Cancel in the progress
        dialog"""
        if self.has_been_cancelled():
            self.reset_progress()
            raise UserCancelled()

    def reset_progress(self):
        """Close all progress bars and clear all progress nesting"""
        self._close_bar()
        self.stack.reset()

    def set_progress_parent(self, parent):
        """Set the GUI parent window handle for progress dialogs"""
        self.progress_bar.set_parent(parent)

    def _update_bar(self):
        """Update existing progress bar or create a new one"""
        new_value = self.stack.current_value()
        new_title = self.stack.current_title()
        new_label = self.stack.current_label()
        # We only update values that have changed since last update call
        self.progress_bar.update(
            label=None if new_label == self.last_label else new_label,
            value=None if new_value == self.last_value else new_value,
            title=None if new_title == self.last_title else new_title
        )
        self.last_value = new_value
        self.last_label = new_label
        self.last_title = new_title
        self.check_for_cancel()

    def _close_bar(self):
        """Hide any existing progress dialog"""
        self.progress_bar.close()
        self.last_value = None
        self.last_label = None
        self.last_title = None


class ProgressStack:
    """Used for handling a nested progress bar

    ProgressStack holds a stack of nested progress bar statuses,
    so that for example, if an operation is performed 4 times,
    the progress bar will not go from 0% to 100% 4 times, but instead go
    from 0% to 25% for the first operation, etc."""

    @dataclass
    class ProgressStackItem:
        """Stores status for one of a stack of nested progress bars"""

        bar_min: int = 0
        bar_step: int = 100
        label: str = 'Please wait'
        title: str = ''
        value: int or None = None
        step: int or None = None

        def global_value(self) -> int or None:
            """Return the progress value as it will appear on the bar, i.e.
            adjusted to include all the progress nesting"""
            if self.value is None:
                return None
            else:
                return round(self.bar_min + self.value * self.bar_step / 100)

        def child_value(self) -> int or None:
            """Return the initial value that a nested child progress bar should
            take. This is normally zero, but if no parent value was specified
            it could be None to allow for an unspecified progress value
            """
            return None if self.value is None else 0

        def child_bar_min(self) -> int:
            """When creating a nested child progress bar, return the global
            minimum bar position for this child progress bar"""
            if self.value is None:
                return self.bar_min
            else:
                return round(self.bar_min + self.value * self.bar_step / 100)

        def child_bar_step(self) -> int or None:
            """When creating a nested child progress bar, return the global
            bar width for this child progress bar"""
            if self.step is None:
                return self.bar_step
            else:
                return round(self.step * self.bar_step / 100)

        def next_value(self) -> int or None:
            """Return the value that results from incrementing this progress.
            Generally this is the value plus the step; if no step has been
            specified or inferred then we assume the next value will be 100%
            """
            if self.step is None:
                return 100
            elif self.value is None:
                return min(100, self.step)
            else:
                return min(100, self.value + self.step)

    def __init__(self):
        self.stack = []

    def is_empty(self) -> bool:
        """Return True if the is no progress currently reported"""
        return len(self.stack) == 0

    def reset(self):
        """Remove all nested progress bars"""
        self.stack = []

    def current_label(self) -> str:
        """Return the label that should be displayed"""
        return self.stack[-1].label

    def current_title(self) -> str:
        """Return the title that should be displayed"""
        return self.stack[-1].title

    def current_value(self) -> int or None:
        """Return the global value that should be displayed"""
        return self.stack[-1].global_value()

    def update(self,
               value: int or None,
               step: int or None,
               label: str or None,
               title: str or None):
        """Update the values of the current progress bar

        Args:
            value: The progress percentage, or None to display a non-ending
                   progress bar, if supported
            step: Percentage difference between progress calls.
            label: The label text to display by the progress
            title: The title of the progress dialog
        """
        # Update step
        if step is None:
            if value is not None and value > 0:
                # If step not specified, we guess it as being the difference
                # between the current and last specified value
                if self.stack[-1].value is None:
                    step = value
                else:
                    step = value - self.stack[-1].value
                # Ensure the step guess does not go beyond the progress limit
                if value + step > 100:
                    step = 100 - value
                self.stack[-1].step = step
        else:
            self.stack[-1].step = step

        # Update current progress value
        if value is not None:
            self.stack[-1].value = value

        # Update current progress label
        if label is not None:
            self.stack[-1].label = label

        # Update current dialog title
        if title is not None:
            self.stack[-1].title = title

    def push(self):
        """Nest progress reporting. After calling this function, subsequent
        progress updates will modify the progress bar between the current
        value and the current value plus the last step
        """
        if len(self.stack) == 0:
            self.stack.append(ProgressStack.ProgressStackItem())
        else:
            self.stack.append(
                ProgressStack.ProgressStackItem(
                    bar_min=self.stack[-1].child_bar_min(),
                    bar_step=self.stack[-1].child_bar_step(),
                    label=self.stack[-1].label,
                    title=self.stack[-1].title,
                    value=self.stack[-1].child_value()
                )
            )

    def pop(self):
        """Remove the last nested progress bar from the stack"""
        self.stack.pop()

    def advance(self):
        """Increment the current progress value by one step"""
        self.stack[-1].value = self.stack[-1].next_value()
