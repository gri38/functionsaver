""" This test file is dedicated to check if the replay of a function saved internals and outputs as expected """

from pathlib import Path

import pytest

from functionsaver import function_saver
from functionsaver.function_saver import replay_and_check_function
from utils_for_tests import assert_replay_output, assert_replay_internal


@function_saver
def function_to_replay_without_internal(a: int, b: int) -> int:
    assert function_to_replay_without_internal.is_save_internal_enabled() is True
    return a + b


@function_saver(save_internals=False, save_out=False)
def function_to_replay_without_internal_not_output(a: int, b: int) -> int:
    assert (
        function_to_replay_without_internal_not_output.is_save_internal_enabled()
        is False
    )
    function_to_replay_without_internal_not_output.save_internal(a - b, "substracted")
    function_to_replay_without_internal_not_output.save_internal(a + b, "added")
    return a + b


@function_saver(save_out=False)
def function_to_replay_without_output(a: int, b: int) -> int:
    assert function_to_replay_without_output.is_save_internal_enabled() is True
    function_to_replay_without_output.save_internal(a - b, "substracted")
    function_to_replay_without_output.save_internal(a + b, "added")
    return a + b


@function_saver(save_out=False)
def function_to_replay_without_output_10times(a: int, b: int) -> int:
    """this function saves different internal to test replaying twice, and the good erase of replay folder."""
    assert function_to_replay_without_output_10times.is_save_internal_enabled() is True
    function_to_replay_without_output.save_internal(10 * (a - b), "substracted")
    function_to_replay_without_output.save_internal(10 * (a + b), "added")
    return 10 * (a + b)


@function_saver
def function_to_replay(a: int, b: int) -> int:
    assert function_to_replay.is_save_internal_enabled() is True
    function_to_replay.save_internal(a - b, "substracted")
    function_to_replay.save_internal(a + b, "added")
    return a + b


@function_saver
def function_to_replay_10times(a: int, b: int) -> int:
    """this function saves different internal to test replaying twice, and the good erase of replay folder."""
    assert function_to_replay_10times.is_save_internal_enabled() is True
    function_to_replay.save_internal(10 * (a - b), "substracted")
    function_to_replay.save_internal(10 * (a + b), "added")
    return 10 * (a + b)


def test_replay_with_output(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    function_to_replay_without_internal(1, 2)

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            try:
                replay_and_check_function(function_to_replay_without_internal, dir_path)
            except Exception as e:
                assert False, f"Replay failed: {e}"
            assert_replay_output(dir_path, True, 1, 2)
            assert_replay_internal(dir_path, False, 1, 2)
            break
    else:
        assert False, "Cannot find a folder for replay"


def test_replay(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    function_to_replay(1, 2)

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            try:
                replay_and_check_function(function_to_replay, dir_path)
            except Exception as e:
                assert False, f"Replay failed: {e}"
            assert_replay_output(dir_path, True, 1, 2)
            assert_replay_internal(dir_path, True, 1, 2)
            with pytest.raises(AssertionError):
                replay_and_check_function(function_to_replay_10times, dir_path)
            assert_replay_output(dir_path, True, 10, 20)
            assert_replay_internal(dir_path, True, 10, 20)
            break
    else:
        assert False, "Cannot find a folder for replay"
