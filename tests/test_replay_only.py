"""
This test file test a specific case: when we replay from a folder, but didn't run the function saved before, in the same runtime.
it reproduces a bug where the context data was not properly initialised.

To do so, we save with a function, but replay with another, with the same signature.
"""

from pathlib import Path

import pytest

from functionsaver import function_saver, replay_function
from functionsaver.function_saver import (
    replay_function_async,
    replay_and_check_function,
    replay_and_check_function_async,
)
from utils_for_tests import assert_replay_output, assert_replay_internal


@function_saver
def function_for_saving(a: int, b: int) -> int:
    assert function_for_saving.is_save_internal_enabled() is True
    function_for_saving.save_internal(a - b, "substracted")
    function_for_saving.save_internal(a + b, "added")
    return a + b


@function_saver
async def function_for_saving_async(a: int, b: int) -> int:
    assert function_for_saving_async.is_save_internal_enabled() is True
    function_for_saving.save_internal(a - b, "substracted")
    function_for_saving.save_internal(a + b, "added")
    return a + b


@function_saver
def function_for_replaying(a: int, b: int) -> int:
    assert function_for_replaying.is_save_internal_enabled() is True
    function_for_replaying.save_internal(a - b, "substracted")
    function_for_replaying.save_internal(a + b, "added")
    return a + b


@function_saver
async def function_for_replaying_async(a: int, b: int) -> int:
    assert function_for_replaying_async.is_save_internal_enabled() is True
    function_for_replaying.save_internal(a - b, "substracted")
    function_for_replaying.save_internal(a + b, "added")
    return a + b


def test_replay_only(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    function_for_saving(1, 2)

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            replay_function(function_for_replaying, dir_path)
            assert_replay_output(dir_path, True, 1, 2)
            assert_replay_internal(dir_path, True, 1, 2)
            break
    else:
        assert False, "Cannot find a folder for replay"


def test_replay_and_check_only(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    function_for_saving(1, 2)

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            try:
                replay_and_check_function(function_for_replaying, dir_path)
            except AssertionError as e:
                assert False, f"Replay failed: {e}"
            assert_replay_output(dir_path, True, 1, 2)
            assert_replay_internal(dir_path, True, 1, 2)
            break
    else:
        assert False, "Cannot find a folder for replay"


@pytest.mark.asyncio
async def test_replay_only_async(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    await function_for_saving_async(1, 2)

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            await replay_function_async(function_for_replaying_async, dir_path)
            assert_replay_output(dir_path, True, 1, 2)
            assert_replay_internal(dir_path, True, 1, 2)
            break
    else:
        assert False, "Cannot find a folder for replay"


@pytest.mark.asyncio
async def test_replay_and_check_only_async(
    reset_environment, fonctionsaver_in_tempfolder
):
    temp_folder = fonctionsaver_in_tempfolder
    await function_for_saving_async(1, 2)

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            try:
                await replay_and_check_function_async(
                    function_for_replaying_async, dir_path
                )
            except AssertionError as e:
                assert False, f"Replay failed: {e}"
            assert_replay_output(dir_path, True, 1, 2)
            assert_replay_internal(dir_path, True, 1, 2)
            break
    else:
        assert False, "Cannot find a folder for replay"
