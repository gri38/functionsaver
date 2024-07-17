import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DataFolders:
    input_path: Path
    output_path: Path
    internals_path: Path
    function_saver_path: Path


def count_function_saver_folders(root_path: str | Path) -> int:
    if isinstance(root_path, str):
        root_path = Path(root_path)
    return len([f for f in root_path.iterdir() if f.is_dir()])


def get_data_folders_from_function_saver_root(
    root_path: str | Path,
) -> list[DataFolders]:
    if isinstance(root_path, str):
        root_path = Path(root_path)
    return [
        DataFolders(
            input_path=dir_path / "inputs",
            output_path=dir_path / "output",
            internals_path=dir_path / "internal",
            function_saver_path=dir_path,
        )
        for dir_path in root_path.iterdir()
        if dir_path.is_dir()
    ]


def check_function_saving_files(temp_folder, expected_folders):
    tmpdir_path = Path(temp_folder)
    function_saver_folders = 0
    for dir_path in tmpdir_path.iterdir():
        if dir_path.is_dir():
            function_saver_folders += 1
            input_path = dir_path / "inputs"
            output_path = dir_path / "output"
            internals_path = dir_path / "internal"

            input_file_a = input_path / "a.json"
            input_file_b = input_path / "b.json"
            output_file = output_path / "output.json"
            internal_file = internals_path / "subtracted.json"

            assert (
                input_file_a.exists()
            ), f"Input file a does not exist in {dir_path.name}"
            assert (
                input_file_b.exists()
            ), f"Input file b does not exist in {dir_path.name}"
            assert (
                output_file.exists()
            ), f"Output file does not exist in {dir_path.name}"
            assert (
                internal_file.exists()
            ), f"Internals file does not exist in {dir_path.name}"

            with open(input_file_a) as f:
                a = json.load(f)
            with open(input_file_b) as f:
                b = json.load(f)
            with open(output_file) as f:
                ab_sum = json.load(f)
            with open(internal_file) as f:
                ab_sub = json.load(f)

            assert a + b == ab_sum, "Output does not match the sum of inputs"
            assert a - b == ab_sub, "Internals do not match the subtraction of inputs"
    assert function_saver_folders == expected_folders, (
        f"Expected {expected_folders} folders, " f"got {function_saver_folders}"
    )


def assert_replay_output(save_root_folder: Path, should_exist: bool, a: int, b: int):
    """
    Assert the output file of a replayed function is as expected, for a function that takes two arguments and returns their sum.
    """
    replay_output_file = save_root_folder / "output_replay" / "output.json"
    assert replay_output_file.exists() == should_exist
    if should_exist:
        with open(replay_output_file) as f:
            assert f.read() == str(a + b)


def assert_replay_internal(save_root_folder: Path, should_exist: bool, a: int, b: int):
    """
    Assert the internal files of a replayed function are as expected, for a function that takes two arguments
    and saves internals: a - b and a + b in the replay folder in substrated.json and added.json respectively.
    """
    replay_output_file_minus = save_root_folder / "internal_replay" / "substracted.json"
    replay_output_file_add = save_root_folder / "internal_replay" / "added.json"
    assert replay_output_file_minus.exists() == should_exist
    assert replay_output_file_add.exists() == should_exist
    if should_exist:
        with open(replay_output_file_minus) as f:
            assert f.read() == str(a - b)
        with open(replay_output_file_add) as f:
            assert f.read() == str(a + b)
