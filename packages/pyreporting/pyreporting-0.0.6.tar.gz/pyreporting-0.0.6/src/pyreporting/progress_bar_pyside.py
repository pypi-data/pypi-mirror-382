"""Pyside implementation of ProgressBar"""

from PySide6 import QtCore
from PySide6.QtCore import QCoreApplication, QObject, Qt, Signal
from PySide6.QtWidgets import QProgressDialog, QWidget

from pyreporting.progress_bar import ProgressBar


class CancelState:
    """An object which can be passed between threads, holding the boolean
    status of whether a progress bar has been cancelled

    This deals with a specific issue where, because the gui and worker threads
    are asynchronous, an old progress dialog might still be in the process of
    being destroyed while the worker thread is creating or updating a new
    progress dialog. We don't want the cancel status of the previous dialog to
    affect computations which are controlled by the new dialog. To avoid this,
    the cancellation state object is created on the worker thread and passed
    to the gui thread to be used when the progress dialog is created. This
    means that each progress dialog will have its own cancellation state, but
    the cancel_clicked() method will only check the calcellation state which
    relates to the current worker progress
    """
    def __init__(self):
        self.cancelled = False


class PySideProgressBar(ProgressBar):
    """A Pyside implementation of ProgressBar"""

    class PySideProgressBarSignals(QObject):
        """Signals used to trigger an update of the progress bar. The trigger
        can be from a worker thread by the GUI is updated on the main thread"""
        update = Signal(object, object, object, object)
        destroy = Signal()

    class QProgressWrapper:
        """Wraps the creation of a QProgressDialog with cancellation callback"""
        def __init__(self,
                     parent: QWidget,
                     label: str or None,
                     title: str or None,
                     value: int or None,
                     cancel_state: CancelState
                     ):
            self.maximum = 100
            self.cancel_state = cancel_state
            self.dialog = QProgressDialog(
                parent=parent,
                labelText=label,
                minimum=0,
                maximum=self.maximum
            )
            self.dialog.setMinimumDuration(0)
            self.dialog.setAutoReset(False)
            self.dialog.setAutoClose(False)
            self.dialog.setWindowModality(Qt.WindowModal)
            self.dialog.setWindowTitle(title)
            self.cancel_connection = self.dialog.canceled.connect(
                self._cancel_signalled)
            if value is None or value == -1:
                self.dialog.setRange(0, 0)
                self.dialog.setValue(0)

        def close(self):
            """Destroy this progress dialog"""
            self.dialog.canceled.disconnect(self.cancel_connection)
            self.dialog.close()
            self.dialog.deleteLater()

        def update(self, value, label, title):
            """Update existing values in this progress dialog"""
            if label is not None:
                self.dialog.setLabelText(label)

            if title is not None:
                self.dialog.setWindowTitle(title)

            # Note: setValue() must be the last call, because it can trigger
            # QApplication.processEvents() which could start processing the next
            # event before this one has completed
            if value is not None:
                if value == -1:
                    self.dialog.setRange(0, 0)
                    self.dialog.setValue(0)
                else:
                    self.dialog.setRange(0, self.maximum)
                    self.dialog.setValue(value)

        def _cancel_signalled(self):
            self.cancel_state.cancelled = True

    def __init__(self, parent: QObject, **kwargs):
        self.cancel_state = None
        self.progress_wrapper = None
        self.signals = PySideProgressBar.PySideProgressBarSignals()
        self.signals.update.connect(self._update_signalled)
        self.signals.destroy.connect(self._destroy_signalled)
        super().__init__(parent=parent, **kwargs)

        # pylint:disable-next=c-extension-no-member
        if not QtCore.QThread.currentThread() == \
               QCoreApplication.instance().thread():
            raise RuntimeError("PySideProgressBar() should be created on the "
                               "main GUI thread")

    def update(self,
               label: str or None = None,
               value: int or None = None,
               title: str or None = None):
        """Trigger a signal to create or update the current progress dialog"""

        # No cancel state means there is no active progress, although existing
        # progress dialogs may still be present waiting to be destroyed on the
        # GUI thread. We create a new cancel state which will be linked to the
        # new progress dialog when it is created. This will ensure that only
        # a cancel form the new cancel dialog will be registered
        if self.cancel_state is None:
            self.cancel_state = CancelState()

        # Send signal to the GUI thread to create or update the progress bar
        self.signals.update.emit(label, value, title, self.cancel_state)

    def close(self):
        """Trigger a signal to destroy the current progress dialog"""

        # Invalidate current cancel state; ensures the calling application
        # will not receive any cancel notifications from the old progress
        # dialog while it is in the process of being destroyed
        self.cancel_state = None

        # Send signal to the GUI thread to destroy the progress bar
        self.signals.destroy.emit()

    def cancel_clicked(self) -> bool:
        """Check if the cancel button has been clicked"""

        # Only check the currently assigned cancel state. It's possible that
        # a previous progress dialog is still being destroyed on the GUI thread
        # and we don't want cancel signals from that
        if self.cancel_state:
            return self.cancel_state.cancelled
        else:
            return False

    def _update_signalled(self,
                          label: str or None,
                          value: int or None,
                          title: str or None,
                          cancel_state: CancelState
                          ):
        """Called on main thread to process an update request"""
        if not self.progress_wrapper:
            self.progress_wrapper = PySideProgressBar.QProgressWrapper(
                parent=self.parent,
                value=value,
                label=label,
                title=title,
                cancel_state=cancel_state
            )
        else:
            self.progress_wrapper.update(
                value=value,
                label=label,
                title=title
            )

    def _destroy_signalled(self):
        """Called on main thread to process a progress destroy request"""
        if self.progress_wrapper:
            self.progress_wrapper.close()
            self.progress_wrapper = None
