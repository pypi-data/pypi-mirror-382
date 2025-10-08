"""Error, message and progress reporting"""

from dataclasses import dataclass
from logging import DEBUG, ERROR, INFO, WARNING
from typing import Callable, Optional

from pyreporting.logger import Logger
from pyreporting.progress import Progress
from pyreporting.progress_bar import ProgressBar, ProgressBarType
from pyreporting.util import open_path, throw_exception


class Reporting:
    """Provides error, message and progress reporting.

    Reporting is a class used to process errors, warnings, messages,
    logging information and progress bars. This means that warnings,
    errors and progress are handled via a callback instead of
    directly bringing up message boxes and progress boxes or writing to the
    command window. This allows applications to choose how they
    process error, warning and progress information.

    Typically, a single Reporting object is created during application startup,
    and passed into the classes and functions that use it. This means that
    logging and progress reporting are handled in a single place, allowing for
    consistent behaviour across the application and more advanced features such
    as nested progress dialogs.

    The default Reporting implementation uses the standard python logging
    library, so standard logging calls should also work.

    Progress can be provided via a console progress bar (TerminalProgress) for
    terminal applications, or a windowed progress bar for GUI applications.

    You can create your own implementation of the Reporting interface to get
    customised message and progress behaviour; for example, if you are running
    a batch script you may wish it to run silently, whereas for a GUI
    application you may wish to display error, warning and progress dialogs
    to the user.
    """

    CancelErrorId = 'CoreReporting:UserCancel'

    USE_TERMINAL_PROGRESS = "USER_TERMINAL_PROGRESS"

    def __init__(
            self,
            app_name: str = "pyreporting_default",
            progress_type: ProgressBarType or ProgressBar =
            ProgressBarType.TERMINAL,
            log_file_name=None,
            debug=False,
            parent=None,
            interactive: bool = True):
        """

        Args:
            app_name: Application name to use when creating log file directory
            progress_type: Either an object implementing the Progress
                 interface, None for no progress, or a ProgressBarType enum
                 which will be used to determine which progress bar to create
            log_file_name: Specify log filename instead of using default
                application log file directory based on app_name
            debug: set to True to log debug messages
            interactive: set to True if used in an interactive environment,
                         allowing for example windows to be opened
        """
        if not isinstance(progress_type, (ProgressBar, ProgressBarType)):
            raise ValueError("progress_type should be a ProgressBar or "
                             "ProgressBarType enum")

        self.progress = Progress(progress_type=progress_type, parent=parent)
        self.logger = Logger(
            app_name=app_name,
            debug=debug,
            log_filename=log_file_name
        )
        self.app_name = app_name
        self.cache = RecordCache(log_function=self.logger.log)
        self.enabled_cache_types = []
        self.interactive = interactive

    def __del__(self):
        self.end_message_caching()

    def debug(self,
              message: str,
              identifier: str = None,
              supplementary_info: str = None,
              exception=None):
        """Write debugging information to the console and log file"""
        self.logger.log(
            level=DEBUG,
            prefix="Debug info",
            identifier=identifier,
            message=message,
            supplementary_info=supplementary_info,
            exception=exception
        )

    def info(self,
             message: str,
             identifier: str = None,
             supplementary_info: str = None,
             exception=None):
        """Write an information message to the console and log file"""
        if INFO in self.enabled_cache_types:
            self.cache.add(
                level=INFO,
                prefix="Info",
                identifier=identifier,
                message=message,
                supplementary_info=supplementary_info,
                exception=exception
            )
        else:
            self.logger.log(
                level=INFO,
                prefix="Info",
                identifier=identifier,
                message=message,
                supplementary_info=supplementary_info,
                exception=exception
            )

    def warning(self,
                message: str,
                identifier: str = None,
                supplementary_info: str = None,
                exception=None):
        """Write a warning message to the console and log file"""
        if WARNING in self.enabled_cache_types:
            self.cache.add(
                level=WARNING,
                prefix="Warning",
                identifier=identifier,
                message=message,
                supplementary_info=supplementary_info,
                exception=exception
            )
        else:
            self.logger.log(
                level=WARNING,
                prefix="Warning",
                identifier=identifier,
                message=message,
                supplementary_info=supplementary_info,
                exception=exception
            )

    def error(self,
              message: str,
              identifier: str = None,
              supplementary_info=None,
              exception=None,
              throw: bool = True):
        """Write an error message to the console and log file.
        If throw is True, this will also raise an exception. Where appropriate,
        the application should catch this exception and present the message to
        the user e.g. using a modal error dialog"""
        self.logger.log(
            level=ERROR,
            prefix="Error",
            identifier=identifier,
            message=message,
            supplementary_info=supplementary_info,
            exception=exception
        )
        if throw:
            throw_exception(message=message, identifier=identifier,
                            exception=exception)

    @staticmethod
    def default_error(message: str,
                      identifier: str = None,
                      supplementary_info=None,
                      exception=None,
                      throw: bool = True):
        """Write an error message to the console and log file.
        If throw is True, this will also raise an exception. Where appropriate,
        the application should catch this exception and present the message to
        the user e.g. using a modal error dialog"""
        Logger.default_log(
            level=ERROR,
            prefix="Error",
            identifier=identifier,
            message=message,
            supplementary_info=supplementary_info,
            exception=exception
        )
        if throw:
            throw_exception(message=message, identifier=identifier,
                            exception=exception)

    @staticmethod
    def default_warning(message: str,
                        identifier: str = None,
                        supplementary_info=None,
                        exception=None):
        """Write a warning message to the console and log file"""
        Logger.default_log(
            level=WARNING,
            prefix="Warning",
            identifier=identifier,
            message=message,
            supplementary_info=supplementary_info,
            exception=exception
        )

    def start_message_caching(self, cache_types: Optional[list[int]] = None):
        """Enable message caching to prevent duplicate log messages

        This typically is used with WARNING and INFO messages.

        When caching is on, messages will not be displayed or logged but will
        be added to the cache.

        When show_and_clear_pending_messages() is called, the messages in the
        cache will be displayed, but messages with the same identifier will
        only be shown once, with the message modified to show how many times
        the message was generated.

        This helps to stop the command window or log file being overwhelmed
        with duplicate warning or info messages

        Start caching messages of specified types (typically WARNING and
        INFO). Instead of immediately displaying/logging these messages, they
        will be grouped to prevent multiple messages of the same type from

        Args:
            cache_types: list of warning levels to cache. Currently supports
                WARNING and INFO.
        """
        self.enabled_cache_types = cache_types if cache_types is not None \
            else [INFO, WARNING]

    def end_message_caching(self):
        """End the message caching started by end_message_caching()

        This will show any pending error or warning log messages, with adjusted
        message text to show the number of repetitions of duplicate messages.
        """
        self.cache.show_and_clear()
        self.enabled_cache_types = []

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
        self.progress.start_progress(
            value=value, step=step, label=label, title=title
        )

    def complete_progress(self):
        """Complete the current progress dialog. If there are no other progress
        bars currently nested then hide the dialog, otherwise return to the
        parent progress and complete the current stage"""
        self.progress.complete_progress()

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
        self.progress.update_progress(
            value=value,
            step=step,
            label=label,
            title=title
        )

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
        self.progress.advance_progress(
            step=step,
            label=label,
            title=title
        )

    def update_progress_stage(self,
                              stage: int,
                              num_stages: int,
                              label: Optional[str] = None,
                              title: Optional[str] = None):
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
        self.progress.update_progress_stage(
            stage=stage,
            num_stages=num_stages,
            label=label,
            title=title
        )

    def has_been_cancelled(self) -> bool:
        """Return True if the user has clicked Cancel in the progress dialog"""
        return self.progress.has_been_cancelled()

    def check_for_cancel(self):
        """Raise Cancel exception if user has clicked Cancel in the progress
        dialog"""
        self.progress.check_for_cancel()

    def reset_progress(self):
        """Close all progress bars and clear all progress nesting"""
        self.progress.reset_progress()

    def set_progress_parent(self, parent):
        """Set the GUI parent window handle for progress dialogs"""
        self.progress.set_progress_parent(parent)

    def open_path(self, file_path, message):
        """Open an OS window to the specified file path"""
        if self.interactive:
            open_path(file_path)
        else:
            print(message)


DEFAULT_REPORTING: Optional['Reporting'] = None


def get_reporting(error_if_not_configured: bool = False) -> Reporting:
    """Return the current default reporting object"""
    if DEFAULT_REPORTING is not None:
        return DEFAULT_REPORTING
    if error_if_not_configured:
        raise RuntimeError("Default Reporting object has not been configured")
    return configure_reporting()


def configure_reporting(
        app_name: str = "pyreporting_default",
        progress_type: ProgressBarType or ProgressBar
                       or None = ProgressBarType.TERMINAL,
        log_file_name=None,
        debug=False
) -> Reporting:
    """Configure the default reporting object

    Args:
        app_name: Application name
        progress_type: enum of type ProgressBarType specifying the type of
                       progress bar, or a custom ProgressBar implementation
        log_file_name: Log to specified file instead of default
        debug:         set to True if running in debug mode
    """
    global DEFAULT_REPORTING  # pylint:disable=global-statement
    if DEFAULT_REPORTING is not None:
        DEFAULT_REPORTING.error(
            identifier='Reporting:DefaultAlreadyConfigured',
            message='Reporting.configure_default() was called but the '
                    'default Reporting object has already been configured',
            throw=True
        )
    DEFAULT_REPORTING = Reporting(
        app_name=app_name,
        progress_type=progress_type,
        log_file_name=log_file_name,
        debug=debug
    )
    return DEFAULT_REPORTING


class RecordCache:
    """Keeps track of cached messages"""

    @dataclass
    class PendingRecord:
        """Record of specific cached messages"""
        level: int
        prefix: str
        identifier: str
        text: str
        supplementary_info: str
        exception: Exception
        count: int = 1

    def __init__(self, log_function: Callable):
        self.log_function = log_function
        self.cache = {}

    def add(self, level, prefix, identifier, message, supplementary_info,
            exception):
        """Add message to cache"""
        key = f"{level}.{identifier}"
        if key in self.cache:
            self.cache[key].count += 1
        else:
            self.cache[key] = RecordCache.PendingRecord(
                level=level,
                prefix=prefix,
                identifier=identifier,
                text=message,
                supplementary_info=supplementary_info,
                exception=exception
            )

    def show_and_clear(self):
        """Clear the message cache and report all messages"""
        for _, record in self.cache.items():
            message = record.text
            if record.count > 1:
                message = f'(repeated x{record.count}) {record.text}'
            self.log_function(
                level=record.level,
                prefix=record.prefix,
                identifier=record.identifier,
                message=message,
                supplementary_info=record.supplementary_info,
                exception=record.exception
            )
        self.cache.clear()
