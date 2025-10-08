"""Implementation of progress dialog handling for pyreporting package"""
from enum import StrEnum, auto


class ProgressBar:
    """Interface for progress bar implementations"""

    def __init__(self,
                 parent=None,
                 **kwargs  # pylint: disable=unused-argument
                 ):
        """Initialise progress bar

        Args:
            parent: when using a GUI, the parent object to whicih the progress
                    bar should be attached
        """
        self.parent = parent

    def __del__(self):
        """Progress bar destructor"""
        self.close()

    def set_parent(self, parent):
        """Set the parent object for GUI progress bars"""
        self.parent = parent

    def close(self):
        """Destroy progress bar"""
        raise NotImplementedError

    def update(self,
               label: str or None = None,
               value: int or None = None,
               title: str or None = None):
        """Update progress bar

        Args:
            label: If defined, change the text label for the progress bar
            value: If defined, change the progress completion value
            title: If defined, change the progress window title
        """
        raise NotImplementedError

    def cancel_clicked(self) -> bool:
        """Return True if the cancel button was clicked by the user"""
        raise NotImplementedError


class NoProgressBar(ProgressBar):
    """A do-nothing implementation of ProgressBar

    Used when you want to use the pyreporting Reporting class but don't
    actually want a visible progress bar"""

    def update(self,
               label: str or None = None,
               value: int or None = None,
               title: str or None = None):
        pass

    def close(self):
        pass

    def cancel_clicked(self) -> bool:
        return False


class TerminalProgressBar(ProgressBar):
    """A terminal dialog used to report progress information using enlighten"""

    def __init__(self, **kwargs):
        self.terminal_bar = None
        super().__init__(**kwargs)

    def close(self):
        if self.terminal_bar:
            self.terminal_bar.close(clear=True)
            self.terminal_bar = None

    def update(self,
               label: str or None = None,
               value: int or None = None,
               title: str or None = None):
        if not self.terminal_bar:
            # pylint:disable-next=import-outside-toplevel
            import enlighten
            manager = enlighten.get_manager()
            bar_format = '{desc}{desc_pad}{percentage:3.0f}%|{bar}|' \
                         ' {count:{len_total}d}/{total:d}'
            self.terminal_bar = manager.counter(
                total=100,
                desc=label,
                leave=False,
                bar_format=bar_format
            )

        if label is not None:
            self.terminal_bar.desc = label
        if value is not None:
            self.terminal_bar.count = value
        if value is not None or label is not None:
            self.terminal_bar.update(incr=0)

    def cancel_clicked(self):
        return False


class ProgressBarType(StrEnum):
    """Enum/factory for creating progress bars"""
    NONE = auto()
    QT = auto()
    TERMINAL = auto()

    def make(self, **kwargs) -> ProgressBar:
        """Factory method to create a ProgressBar of this type"""
        if self == ProgressBarType.QT:
            # Local import ensures pyside dependency only if required
            # pylint:disable-next=import-outside-toplevel,cyclic-import
            from pyreporting.progress_bar_pyside import PySideProgressBar
            return PySideProgressBar(**kwargs)
        elif self == ProgressBarType.TERMINAL:
            return TerminalProgressBar(**kwargs)
        elif self == ProgressBarType.NONE:
            return NoProgressBar(**kwargs)
        else:
            raise ValueError("Unknown ProgressBarType")
