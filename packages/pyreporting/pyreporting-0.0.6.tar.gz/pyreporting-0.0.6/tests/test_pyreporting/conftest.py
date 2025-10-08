import pytest as pytest

from pyreporting.progress import Progress
from pyreporting.progress_bar import ProgressBar


class MockProgressBar(ProgressBar):
    """A mock implementation of ProgressBar for testing

    Used for testing what the progress stat ewould be without using a visible
    progress bar
    """
    def __init__(self, parent: object = None):
        self.title = None
        self.value = None
        self.label = None
        self.cancelled = False
        self.visible = False
        self.parent = parent
        super().__init__()

    def update(self,
               label: str or None = None,
               value: int or None = None,
               title: str or None = None):
        self.visible = True
        if label is not None:
            self.label = label
        if title is not None:
            self.title = title
        if value is not None:
            self.value = value

    def close(self):
        self.value = None
        self.title = None
        self.label = None
        self.cancelled = False
        self.visible = False

    def cancel_clicked(self) -> bool:
        return self.cancelled


@pytest.fixture
def mock_progress() -> Progress:
    return Progress(MockProgressBar())
