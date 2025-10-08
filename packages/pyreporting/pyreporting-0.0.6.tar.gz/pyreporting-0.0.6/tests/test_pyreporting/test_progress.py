import pytest

from pyreporting.util import UserCancelled


def test_start_complete(mock_progress):
    assert not mock_progress.progress_bar.visible
    mock_progress.start_progress()
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Please wait"
    assert mock_progress.progress_bar.title == ""
    assert mock_progress.progress_bar.value is None
    mock_progress.complete_progress()
    assert not mock_progress.progress_bar.visible


def test_complete(mock_progress):
    mock_progress.start_progress(label="Foo 2", value=49, title='Bar Title 2')
    assert mock_progress.progress_bar.label == "Foo 2"
    assert mock_progress.progress_bar.value == 49
    assert mock_progress.progress_bar.title == 'Bar Title 2'
    mock_progress.complete_progress()
    assert not mock_progress.progress_bar.visible


def test_update(mock_progress):
    assert not mock_progress.progress_bar.visible
    mock_progress.update_progress()
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Please wait"
    assert mock_progress.progress_bar.value == None
    assert mock_progress.progress_bar.title == ''
    mock_progress.update_progress(label="Foo")
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Foo"
    assert mock_progress.progress_bar.value == None
    assert mock_progress.progress_bar.title == ''
    mock_progress.update_progress(value=25)
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Foo"
    assert mock_progress.progress_bar.value == 25
    assert mock_progress.progress_bar.title == ''
    mock_progress.update_progress(title='Bar Title')
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Foo"
    assert mock_progress.progress_bar.value == 25
    assert mock_progress.progress_bar.title == 'Bar Title'
    mock_progress.update_progress(label="Foo 2", value=49, title='Bar Title 2')
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Foo 2"
    assert mock_progress.progress_bar.value == 49
    assert mock_progress.progress_bar.title == 'Bar Title 2'


def test_start_update_complete(mock_progress):
    assert not mock_progress.progress_bar.visible
    mock_progress.start_progress()
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Please wait"
    assert mock_progress.progress_bar.value == None
    assert mock_progress.progress_bar.title == ''
    mock_progress.update_progress(label="Foo")
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Foo"
    assert mock_progress.progress_bar.value == None
    assert mock_progress.progress_bar.title == ''
    mock_progress.update_progress(value=25)
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Foo"
    assert mock_progress.progress_bar.value == 25
    assert mock_progress.progress_bar.title == ''
    mock_progress.update_progress(title='Bar Title')
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Foo"
    assert mock_progress.progress_bar.value == 25
    assert mock_progress.progress_bar.title == 'Bar Title'
    mock_progress.update_progress(label="Foo 2", value=49, title='Bar Title 2')
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Foo 2"
    assert mock_progress.progress_bar.value == 49
    assert mock_progress.progress_bar.title == 'Bar Title 2'
    mock_progress.complete_progress()
    assert not mock_progress.progress_bar.visible


def test_stages(mock_progress):
    assert not mock_progress.progress_bar.visible
    mock_progress.start_progress(title="My Title")
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == 'Please wait'
    assert mock_progress.progress_bar.title == "My Title"
    assert mock_progress.progress_bar.value is None
    for stage in range(5):
        mock_progress.update_progress_stage(stage=0, num_stages=5, label=f"Stage {stage}", title=f"Title {stage}")
        assert mock_progress.progress_bar.visible
        assert mock_progress.progress_bar.label == f"Stage {stage}"
        assert mock_progress.progress_bar.title == f"Title {stage}"
        assert mock_progress.progress_bar.value == 0*stage

    mock_progress.complete_progress()
    assert not mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label is None
    assert mock_progress.progress_bar.title is None
    assert mock_progress.progress_bar.value is None


def test_advance(mock_progress):
    assert not mock_progress.progress_bar.visible
    mock_progress.start_progress(title="My Title", label="My label", step=10)
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "My label"
    assert mock_progress.progress_bar.title == "My Title"
    assert mock_progress.progress_bar.value is None
    for stage in range(10):
        mock_progress.advance_progress()
        assert mock_progress.progress_bar.visible
        assert mock_progress.progress_bar.label == "My label"
        assert mock_progress.progress_bar.title == "My Title"
        assert mock_progress.progress_bar.value == 10*(stage + 1)
    mock_progress.complete_progress()
    assert not mock_progress.progress_bar.visible


def test_progress_is_reset_after_complete(mock_progress):
    assert not mock_progress.progress_bar.visible
    mock_progress.start_progress(title="My title", label="My label", value=50)
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "My label"
    assert mock_progress.progress_bar.title == "My title"
    assert mock_progress.progress_bar.value == 50
    mock_progress.complete_progress()
    assert not mock_progress.progress_bar.visible
    mock_progress.start_progress()
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == "Please wait"
    assert mock_progress.progress_bar.title == ""
    assert mock_progress.progress_bar.value is None


def test_nesting(mock_progress):
    assert not mock_progress.progress_bar.visible
    mock_progress.start_progress(label="Wait", value=5, title="My Title")
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == 'Wait'
    assert mock_progress.progress_bar.title == "My Title"
    assert mock_progress.progress_bar.value == 5
    # Note step not specified so will be automatically be set to 5
    mock_progress.start_progress(label="Nested Wait", value=5, title="Nested Title")
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == 'Nested Wait'
    assert mock_progress.progress_bar.title == "Nested Title"
    assert mock_progress.progress_bar.value == 5
    mock_progress.complete_progress()
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.label == 'Wait'
    assert mock_progress.progress_bar.title == "My Title"
    assert mock_progress.progress_bar.value == 10
    mock_progress.update_progress(value=75)
    assert mock_progress.progress_bar.value == 75
    mock_progress.complete_progress()
    assert not mock_progress.progress_bar.visible


def test_reset(mock_progress):
    # Check no exception if hiding non-existent progress bar
    mock_progress.reset_progress()

    mock_progress.start_progress(label="Foo 2", value=49, title="Bar Title 2")
    assert mock_progress.progress_bar.visible
    mock_progress.reset_progress()
    assert not mock_progress.progress_bar.visible

    # Make sure the progress is properly reset after hiding
    mock_progress.start_progress()
    assert mock_progress.progress_bar.label == "Please wait"
    assert mock_progress.progress_bar.value is None
    assert mock_progress.progress_bar.title == ""
    mock_progress.reset_progress()

    # Check no exception if reset twice
    mock_progress.reset_progress()


def test_has_been_cancelled(mock_progress):
    assert not mock_progress.has_been_cancelled()
    mock_progress.start_progress()
    assert not mock_progress.has_been_cancelled()
    mock_progress.progress_bar.cancelled = True
    assert mock_progress.has_been_cancelled()


def test_check_for_cancel(mock_progress):
    mock_progress.check_for_cancel()
    assert not mock_progress.progress_bar.visible
    mock_progress.start_progress()
    mock_progress.check_for_cancel()
    assert mock_progress.progress_bar.visible
    mock_progress.progress_bar.cancelled = True
    with pytest.raises(UserCancelled):
        mock_progress.check_for_cancel()
    assert not mock_progress.progress_bar.visible


def test_update_stage(mock_progress):
    mock_progress.start_progress()
    mock_progress.update_progress_stage(1, 5)
    assert mock_progress.progress_bar.label == "Please wait"
    assert mock_progress.progress_bar.value == 20
    assert mock_progress.progress_bar.title == ''

    mock_progress.update_progress_stage(2, 5, label="Stage 1", title="Foo")
    assert mock_progress.progress_bar.label == "Stage 1"
    assert mock_progress.progress_bar.value == 40
    assert mock_progress.progress_bar.title == "Foo"

    mock_progress.complete_progress()
    assert not mock_progress.progress_bar.visible


def test_push_pop_step(mock_progress):
    mock_progress.start_progress()  # 1: Progress range is 0-100
    mock_progress.update_progress_stage(1, 10)
    assert mock_progress.progress_bar.label == "Please wait"
    assert mock_progress.progress_bar.value == 10
    assert mock_progress.progress_bar.title == ''

    mock_progress.start_progress()  # 2: Progress range is 10-20
    assert mock_progress.progress_bar.value == 10
    mock_progress.update_progress(value=20)
    assert mock_progress.progress_bar.value == 12
    mock_progress.update_progress(value=40, step=20)
    assert mock_progress.progress_bar.value == 14

    mock_progress.start_progress()  # 3: Progress range is 14-16
    assert mock_progress.progress_bar.value == 14
    mock_progress.update_progress(value=50)
    assert mock_progress.progress_bar.value == 15
    mock_progress.complete_progress()  # 2: Progress range is 10-20
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.value == 16

    mock_progress.update_progress(value=90)
    assert mock_progress.progress_bar.value == 19
    mock_progress.complete_progress()  # 1: Progress range is 0-100
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.value == 20

    mock_progress.start_progress()  # 2: Progress range is 20-30
    mock_progress.update_progress_stage(8, 10)
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.value == 28

    mock_progress.complete_progress()  # 1: Progress range is 0-100
    assert mock_progress.progress_bar.visible
    assert mock_progress.progress_bar.value == 30
    mock_progress.complete_progress()  # 0: No progress
    assert not mock_progress.progress_bar.visible


def test_push_pop_stage(mock_progress):
    mock_progress.start_progress()  # 1: Progress range is 0-100
    mock_progress.update_progress_stage(stage=2, num_stages=5)
    assert mock_progress.progress_bar.value == 40
    mock_progress.start_progress()  # 2: Progress range is 40-60
    assert mock_progress.progress_bar.value == 40
    mock_progress.update_progress_stage(stage=0, num_stages=4)
    assert mock_progress.progress_bar.value == 40
    mock_progress.update_progress_stage(stage=1, num_stages=4)
    assert mock_progress.progress_bar.value == 45
    mock_progress.start_progress()  # 3: Progress range is 45-50
    assert mock_progress.progress_bar.value == 45
    mock_progress.update_progress_stage(stage=2, num_stages=5)
    assert mock_progress.progress_bar.value == 47
    mock_progress.update_progress_stage(stage=4, num_stages=5)
    assert mock_progress.progress_bar.value == 49
    mock_progress.complete_progress()  # 2: Progress range is 40-60
    assert mock_progress.progress_bar.value == 50
    mock_progress.update_progress_stage(stage=3, num_stages=4)
    assert mock_progress.progress_bar.value == 55
    mock_progress.update_progress_stage(stage=4, num_stages=4)
    assert mock_progress.progress_bar.value == 60

    mock_progress.complete_progress()  # 1: Progress range is 0-100
    assert mock_progress.progress_bar.value == 60
    mock_progress.update_progress_stage(stage=4, num_stages=5)
    assert mock_progress.progress_bar.value == 80
    mock_progress.update_progress_stage(stage=5, num_stages=5)
    assert mock_progress.progress_bar.value == 100
    mock_progress.complete_progress()
    assert not mock_progress.progress_bar.visible


def test_set_parent(mock_progress):
    parent = object()
    mock_progress.set_progress_parent(parent)
    mock_progress.start_progress()
    assert mock_progress.progress_bar.parent == parent
