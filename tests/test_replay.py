from pathlib import Path

import numpy as np

from functionsaver import function_saver, SerializeAsArrayPng
from functionsaver.function_saver import (
    replay_function,
    replay_and_check_function,
)
from utils_for_tests import count_function_saver_folders


@function_saver
def function_to_replay(a: int, b: int) -> int:
    assert function_to_replay.is_save_internal_enabled() is True
    return a + b


def test_replay_standard_io(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    res = function_to_replay(1, 2)

    assert count_function_saver_folders(temp_folder) == 1

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            output = replay_function(function_to_replay, dir_path)
            assert output == res
            break
    else:
        assert False, "Cannot find a folder for replay"

    # let's check the replay did not create a new folder
    assert count_function_saver_folders(temp_folder) == 1


def test_replay_and_check_standard_io(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    res = function_to_replay(1, 2)

    assert count_function_saver_folders(temp_folder) == 1

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            try:
                output = replay_and_check_function(function_to_replay, dir_path)
            except AssertionError as e:
                assert False, f"Replay failed: {e}"
            assert output == res
            break
    else:
        assert False, "Cannot find a folder for replay"

    # let's check the replay did not create a new folder
    assert count_function_saver_folders(temp_folder) == 1


def test_replay_np_array(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver
    def function_to_replay_np_array(image):
        assert function_to_replay_np_array.is_save_internal_enabled() is True
        assert isinstance(image, np.ndarray)
        return 255 - image

    temp_folder = fonctionsaver_in_tempfolder
    rainbow_image = np.zeros((100, 100, 3), dtype=np.uint8)
    rainbow_image[:, :, 0] = np.arange(100)
    rainbow_image[:, :, 1] = np.arange(100)
    rainbow_image[:, :, 2] = np.arange(100)
    res = function_to_replay_np_array(rainbow_image)

    assert count_function_saver_folders(temp_folder) == 1

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            output = replay_function(function_to_replay_np_array, dir_path)
            assert isinstance(output, np.ndarray)
            assert np.all(output == res)
            break
    else:
        assert False, "Cannot find a folder for replay"

    # let's check the replay did not create a new folder
    assert count_function_saver_folders(temp_folder) == 1


def test_replay_and_check_np_array(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver
    def function_to_replay_np_array(image):
        assert function_to_replay_np_array.is_save_internal_enabled() is True
        assert isinstance(image, np.ndarray)
        return 255 - image

    temp_folder = fonctionsaver_in_tempfolder
    rainbow_image = np.zeros((100, 100, 3), dtype=np.uint8)
    rainbow_image[:, :, 0] = np.arange(100)
    rainbow_image[:, :, 1] = np.arange(100)
    rainbow_image[:, :, 2] = np.arange(100)
    res = function_to_replay_np_array(rainbow_image)

    assert count_function_saver_folders(temp_folder) == 1

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            try:
                output = replay_and_check_function(
                    function_to_replay_np_array, dir_path, np.array_equal
                )
                assert isinstance(output, np.ndarray)
            except AssertionError as e:
                assert False, f"Replay failed: {e}"
            assert np.all(output == res)
            break
    else:
        assert False, "Cannot find a folder for replay"

    # let's check the replay did not create a new folder
    assert count_function_saver_folders(temp_folder) == 1


def test_replay_and_check_np_array_as_png(
    reset_environment, fonctionsaver_in_tempfolder
):
    @function_saver
    def function_to_replay_np_array(
        image: np.ndarray | SerializeAsArrayPng,
    ) -> np.ndarray | SerializeAsArrayPng:
        assert function_to_replay_np_array.is_save_internal_enabled() is True
        assert isinstance(image, np.ndarray)
        return 255 - image

    temp_folder = fonctionsaver_in_tempfolder
    rainbow_image = np.zeros((100, 100, 3), dtype=np.uint8)
    rainbow_image[:, :, 0] = np.arange(100)
    rainbow_image[:, :, 1] = np.arange(100)
    rainbow_image[:, :, 2] = np.arange(100)
    res = function_to_replay_np_array(rainbow_image)

    assert count_function_saver_folders(temp_folder) == 1

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            try:
                output = replay_and_check_function(
                    function_to_replay_np_array, dir_path, np.array_equal
                )
                assert isinstance(output, np.ndarray)
            except AssertionError as e:
                assert False, f"Replay failed: {e}"
            assert np.all(output == res)
            break
    else:
        assert False, "Cannot find a folder for replay"

    # let's check the replay did not create a new folder
    assert count_function_saver_folders(temp_folder) == 1


def test_replay_check_double(reset_environment, fonctionsaver_in_tempfolder):
    """
    This test tests the save of in out of a function with doubles, and replay and check the replay.
    """

    @function_saver
    def function_to_replay_double(a: float, b: float) -> float:
        assert function_to_replay_double.is_save_internal_enabled() is True
        assert isinstance(a, float)
        assert isinstance(b, float)
        return a / b

    temp_folder = fonctionsaver_in_tempfolder
    res = function_to_replay_double(1.1, 2.2)

    assert count_function_saver_folders(temp_folder) == 1

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            try:
                output = replay_and_check_function(function_to_replay_double, dir_path)
                assert isinstance(output, float)
            except AssertionError as e:
                assert False, f"Replay failed: {e}"
            assert output == res
            break
    else:
        assert False, "Cannot find a folder for replay"

    # let's check the replay did not create a new folder
    assert count_function_saver_folders(temp_folder) == 1
