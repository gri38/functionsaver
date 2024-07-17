import threading
import time

from functionsaver import (
    function_saver,
    replay_function,
    replay_and_check_function,
)
from utils_for_tests import (
    count_function_saver_folders,
    get_data_folders_from_function_saver_root,
    check_function_saving_files,
)


class ClassWithFunctionToSave:

    @function_saver
    def function_to_save(self, a: int, b: int) -> int:
        assert self.function_to_save.is_save_internal_enabled() is True
        self.function_to_save.save_internal(a - b, "subtracted")
        return a + b


def test_functionsaver_in_class(reset_environment, fonctionsaver_in_tempfolder):
    temp_folder = fonctionsaver_in_tempfolder
    c = ClassWithFunctionToSave()
    c.function_to_save(1, 2)
    assert count_function_saver_folders(temp_folder) == 1

    for data_folders in get_data_folders_from_function_saver_root(temp_folder):
        assert (data_folders.input_path / "a.json").exists()
        assert (data_folders.input_path / "b.json").exists()
        assert not (data_folders.input_path / "self.json").exists()
        assert (data_folders.output_path / "output.json").exists()
        assert (data_folders.internals_path / "subtracted.json").exists()

        c2 = ClassWithFunctionToSave()
        out = replay_function(c2.function_to_save, data_folders.function_saver_path)
        assert out == 3
        replay_and_check_function(c2.function_to_save, data_folders.function_saver_path)


def test_functionsaver_in_class_multithread(
    reset_environment, fonctionsaver_in_tempfolder
):
    temp_folder = fonctionsaver_in_tempfolder
    c = ClassWithFunctionToSave()

    threads_count = 30
    threads = []
    for i in range(threads_count):
        t = threading.Thread(target=c.function_to_save, args=(1, (i + 1) * 10))
        t.start()
        threads.append(t)
        time.sleep(0.001)
    for t in threads:
        t.join()

    check_function_saving_files(temp_folder, expected_folders=threads_count)
