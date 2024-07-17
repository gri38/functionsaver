import logging
import threading
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from functionsaver import function_saver, replay_function
from functionsaver.exception import ReplayException
from functionsaver.serializers import SerializeAsArrayPng
from utils_for_tests import check_function_saving_files


@function_saver
def function_for_test(a: int, b: int) -> int:
    assert function_for_test.is_save_internal_enabled() is True
    time.sleep(
        0.1
    )  # to be sure all threads are started, and possibly detect a bug in the decorator
    logging.info(f"function_for_test called with {a} and {b}")
    function_for_test.save_internal(a - b, "subtracted")  # noqa
    return a + b


def test_function_for_test_mono_thread(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    function_for_test(1, 2)
    function_for_test(3, 4)
    check_function_saving_files(temp_folder, expected_folders=2)


def test_function_for_test_multi_thread(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    threads = []
    threads_count = 30
    for i in range(threads_count):
        t = threading.Thread(target=function_for_test, args=(1, (i + 1) * 10))
        t.start()
        threads.append(t)
        time.sleep(0.001)
    for t in threads:
        t.join()
    check_function_saving_files(temp_folder, expected_folders=threads_count)


def test_png_nparray_serializer(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver
    def function_with_array_npy_serializer(image):
        assert function_with_array_npy_serializer.is_save_internal_enabled() is True
        assert isinstance(image, np.ndarray)
        # let's compute the mirror image:
        mirror_image = np.flip(image, axis=1)
        function_with_array_npy_serializer.save_internal(mirror_image, "mirror_image")
        return 255 - image

    temp_folder = fonctionsaver_in_tempfolder
    rainbow_image = np.zeros((100, 100, 3), dtype=np.uint8)
    rainbow_image[:, :, 0] = np.arange(100)
    rainbow_image[:, :, 1] = np.arange(100)
    rainbow_image[:, :, 2] = np.arange(100)
    res = function_with_array_npy_serializer(rainbow_image)

    function_saver_folders = 0
    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            function_saver_folders += 1
            input_path = dir_path / "inputs"
            output_path = dir_path / "output"
            internals_path = dir_path / "internal"

            input_file = input_path / "image.npy"
            output_file = output_path / "output.npy"
            internal_file = internals_path / "mirror_image.npy"

            assert (
                input_file.exists()
            ), f"Input file a does not exist in {dir_path.name}"
            assert (
                output_file.exists()
            ), f"Output file does not exist in {dir_path.name}"
            assert (
                internal_file.exists()
            ), f"Internal file does not exist in {dir_path.name}"

            replay_res = replay_function(function_with_array_npy_serializer, dir_path)
            assert isinstance(replay_res, np.ndarray)
            assert np.all(replay_res == res)
    assert (
        function_saver_folders == 1
    ), f"Expected 1 folder, got {function_saver_folders}"


def test_png_nparray_png_serializer(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver
    def function_with_array_png_serializer(
        image: np.ndarray | SerializeAsArrayPng,
    ) -> np.ndarray | SerializeAsArrayPng:
        assert function_with_array_png_serializer.is_save_internal_enabled() is True
        # let's compute the mirror image:
        mirror_image = np.flip(image, axis=1)
        function_with_array_png_serializer.save_internal(
            mirror_image, "mirror_image", SerializeAsArrayPng
        )
        return 255 - image

    temp_folder = fonctionsaver_in_tempfolder
    rainbow_image = np.zeros((100, 100, 3), dtype=np.uint8)
    rainbow_image[:, :, 0] = np.arange(100)
    rainbow_image[:, :, 1] = np.arange(100)
    rainbow_image[:, :, 2] = np.arange(100)
    res = function_with_array_png_serializer(rainbow_image)

    function_saver_folders = 0
    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            function_saver_folders += 1
            input_path = dir_path / "inputs"
            output_path = dir_path / "output"
            internals_path = dir_path / "internal"

            input_file = input_path / "image.png"
            output_file = output_path / "output.png"
            internal_file = internals_path / "mirror_image.png"

            assert (
                input_file.exists()
            ), f"Input file a does not exist in {dir_path.name}"
            assert (
                output_file.exists()
            ), f"Output file does not exist in {dir_path.name}"
            assert (
                internal_file.exists()
            ), f"Internal file does not exist in {dir_path.name}"

            replay_res = replay_function(function_with_array_png_serializer, dir_path)
            assert isinstance(replay_res, np.ndarray)
            assert np.all(replay_res == res)

    assert (
        function_saver_folders == 1
    ), f"Expected 1 folder, got {function_saver_folders}"


def test_function_saver_with_kwargs(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver
    def function_with_kwargs(a: int = 1, b: int = 2) -> int:
        assert function_with_kwargs.is_save_internal_enabled() is True
        function_with_kwargs.save_internal(a - b, "subtracted")  # noqa
        return a + b

    temp_folder = fonctionsaver_in_tempfolder
    function_with_kwargs()
    function_with_kwargs(2, 3)
    function_with_kwargs(a=3, b=4)
    check_function_saving_files(temp_folder, expected_folders=3)


def test_input_without_all_args_in_constructor(
    reset_environment, fonctionsaver_in_tempfolder
):
    """
    When a class doesn't define all its serialized args in the constructor, jsons will raise an exception at load.
    This test checks the program doesn't fail because of that (only the deserialization should fail).
    """

    class ClassWithIncompleteConstructor:
        def __init__(self, a: int = 1):
            self.a = a
            self.b = 2

    @function_saver
    def function_with_incomplete_constructor(
        obj: ClassWithIncompleteConstructor, _now: datetime = datetime.now()
    ):
        assert function_with_incomplete_constructor.is_save_internal_enabled() is True
        return obj.a + obj.b

    temp_folder = fonctionsaver_in_tempfolder
    function_with_incomplete_constructor(ClassWithIncompleteConstructor())
    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            with pytest.raises(ReplayException):
                replay_function(function_with_incomplete_constructor, dir_path)
            break
    else:
        assert False, "Cannot find a folder for replay"
