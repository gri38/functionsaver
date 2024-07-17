import asyncio
import logging
import time

import pytest

from functionsaver import function_saver
from functionsaver.function_saver import (
    replay_function_async,
    replay_and_check_function_async,
)
from utils_for_tests import (
    check_function_saving_files,
    get_data_folders_from_function_saver_root,
)


@function_saver
async def function_for_test(a: int, b: int) -> int:
    assert function_for_test.is_save_internal_enabled() is True
    try:
        start_time = time.time()
        logging.info(f"Task {a} started at {start_time}")
        await asyncio.sleep(
            0.5
        )  # to be sure all async tasks are started, and possibly detect a bug in the decorator
        function_for_test.save_internal(a - b, "subtracted")  # noqa
        end_time = time.time()
        logging.info(f"Task {a} ended at {end_time}")
        return a + b
    except:  # noqa
        logging.critical("Error in function_for_test", exc_info=True)


@pytest.mark.asyncio
async def test_async_function_saver(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder

    res1 = await function_for_test(1, 2)

    check_function_saving_files(temp_folder, expected_folders=1)

    for data_folders in get_data_folders_from_function_saver_root(temp_folder):
        res2 = await replay_function_async(
            function_for_test, data_folders.function_saver_path
        )
        assert res1 == res2
        await replay_and_check_function_async(
            function_for_test, data_folders.function_saver_path
        )

        @function_saver
        async def function_for_test_modified(a: int, b: int) -> int:
            assert function_for_test_modified.is_save_internal_enabled() is True
            await asyncio.sleep(0.1)
            return a + b + 1

        with pytest.raises(
            AssertionError, match="Output does not match the expected output: 4 != 3"
        ):
            await replay_and_check_function_async(
                function_for_test_modified, data_folders.function_saver_path
            )
        break
    else:
        assert False, "Cannot find a folder for replay"


async def test_async_function_saver_multi_tasks(
    reset_environment, fonctionsaver_in_tempfolder
):
    temp_folder = fonctionsaver_in_tempfolder

    task_count = 30  # warning too much tasks overloads the system and
    # the test may fail because of 2 tasks running at the same time => same folder name
    tasks = []
    for i in range(task_count):
        task = asyncio.create_task(function_for_test(i, i + 1))
        tasks.append(task)
        await asyncio.sleep(
            0.01
        )  # I don't understand why, but the tasks seems to start every 1 ms instead of 10 ...
    await asyncio.gather(*tasks)

    check_function_saving_files(temp_folder, expected_folders=task_count)


async def test_async_save_internals(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder

    @function_saver
    async def function_for_test(a: int, b: int) -> int:
        assert function_for_test.is_save_internal_enabled() is True
        await function_for_test.save_internal_async(a - b, "subtracted")
        return a + b

    res1 = await function_for_test(1, 2)

    check_function_saving_files(temp_folder, expected_folders=1)
