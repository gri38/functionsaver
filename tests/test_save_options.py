from functionsaver import function_saver
from utils_for_tests import get_data_folders_from_function_saver_root


def test_saving_options_all(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver(
        save_in=True, save_out=True, save_internals=True
    )  # noqa: yes the values are the default one, it's expected
    def function_to_save(a: int, b: int) -> int:
        assert function_to_save.is_save_internal_enabled() is True
        function_to_save.save_internal(a - b, "subtracted")
        return a + b

    temp_folder = fonctionsaver_in_tempfolder
    function_to_save(1, 2)

    for data_folders in get_data_folders_from_function_saver_root(temp_folder):
        assert (data_folders.input_path / "a.json").exists()
        assert (data_folders.input_path / "b.json").exists()
        assert (data_folders.output_path / "output.json").exists()
        assert (data_folders.internals_path / "subtracted.json").exists()


def test_saving_options_no_input(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver(save_in=False)
    def function_to_save(a: int, b: int) -> int:
        assert function_to_save.is_save_internal_enabled() is True
        function_to_save.save_internal(a - b, "subtracted")
        return a + b

    temp_folder = fonctionsaver_in_tempfolder
    function_to_save(1, 2)

    for data_folders in get_data_folders_from_function_saver_root(temp_folder):
        assert not data_folders.input_path.exists()
        assert (data_folders.output_path / "output.json").exists()
        assert (data_folders.internals_path / "subtracted.json").exists()


def test_saving_options_no_output(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver(save_out=False)
    def function_to_save(a: int, b: int) -> int:
        assert function_to_save.is_save_internal_enabled() is True
        function_to_save.save_internal(a - b, "subtracted")
        return a + b

    temp_folder = fonctionsaver_in_tempfolder
    function_to_save(1, 2)

    for data_folders in get_data_folders_from_function_saver_root(temp_folder):
        assert (data_folders.input_path / "a.json").exists()
        assert (data_folders.input_path / "b.json").exists()
        assert not data_folders.output_path.exists()
        assert (data_folders.internals_path / "subtracted.json").exists()


def test_saving_options_no_internal(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver(save_internals=False)
    def function_to_save(a: int, b: int) -> int:
        function_to_save.save_internal(a - b, "subtracted")
        return a + b

    temp_folder = fonctionsaver_in_tempfolder
    function_to_save(1, 2)

    assert function_to_save.is_save_internal_enabled() is False

    for data_folders in get_data_folders_from_function_saver_root(temp_folder):
        assert (data_folders.input_path / "a.json").exists()
        assert (data_folders.input_path / "b.json").exists()
        assert (data_folders.output_path / "output.json").exists()
        assert not data_folders.internals_path.exists()


def test_saving_options_nothing(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver(save_in=False, save_out=False, save_internals=False)
    def function_to_save(a: int, b: int) -> int:
        assert function_to_save.is_save_internal_enabled() is False
        function_to_save.save_internal(a - b, "subtracted")
        return a + b

    temp_folder = fonctionsaver_in_tempfolder
    function_to_save(1, 2)

    for data_folders in get_data_folders_from_function_saver_root(temp_folder):
        assert not data_folders.input_path.exists()
        assert not data_folders.output_path.exists()
        assert not data_folders.internals_path.exists()
