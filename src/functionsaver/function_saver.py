"""
A word about sync / async functions:
A lot of code is duplicated between sync and async functions, but I chose to keep it that way
for better readability (having wrapper_part1, wrapper_part2, ...)

⚠ ⚠ ⚠ ⚠ ⚠ for maintenance, if you change something in the sync part, you should also change it in the async part

"""

import asyncio
import contextvars
import datetime
import functools
import inspect
import os
import shutil
import tempfile
from contextlib import contextmanager, asynccontextmanager
from functools import wraps
from pathlib import Path
from typing import Callable, Any

import aiofiles
import jsons

from .context_data import ContextData
from .exception import ReplayException
from .logger import get_logger
from .replay_compare_shortcut import produce_replay_compare_shortcuts
from .serializers import _get_serializer, _get_deserializer

logger = get_logger()

# Create a context variable to handle saving data when replaying a function
_function_saver_replaying = contextvars.ContextVar(
    "FUNCTION_SAVER_REPLAYING", default="0"
)
_function_saver_replaying_already_delete = contextvars.ContextVar(
    "FUNCTION_SAVER_REPLAYING_ALREADY_DELETE", default="0"
)
_function_saver_replaying_folder = contextvars.ContextVar(
    "FUNCTION_SAVER_REPLAYING_FOLDER", default=""
)


@contextmanager
def replaying(replaying_folder: Path):
    _function_saver_replaying.set("1")
    _function_saver_replaying_already_delete.set("0")
    _function_saver_replaying_folder.set(str(replaying_folder))
    try:
        produce_replay_compare_shortcuts(replaying_folder)
        yield
    finally:
        _function_saver_replaying.set("0")


@asynccontextmanager
async def replaying_async(replaying_folder: Path):
    _function_saver_replaying.set("1")
    _function_saver_replaying_already_delete.set("0")
    _function_saver_replaying_folder.set(str(replaying_folder))
    try:
        produce_replay_compare_shortcuts(replaying_folder)
        yield
    finally:
        _function_saver_replaying.set("0")


def _do_serialize(object_type: type, object_, folder: Path, file_name: str):
    object_dynamic_type = type(object_)
    serializer, extension = _get_serializer(object_type, object_dynamic_type)

    # let's check if the serializer returns a string or bytes to open accordingly the file:
    mode = "w"
    if inspect.signature(serializer).return_annotation == bytes:
        mode = "wb"
    with open(folder / f"{file_name}.{extension}", mode) as f:
        f.write(serializer(object_))


async def _do_serialize_async(object_type: type, object_, folder: Path, file_name: str):
    object_dynamic_type = type(object_)
    serializer, extension = _get_serializer(object_type, object_dynamic_type)

    # Let's check if the serializer returns a string or bytes to open accordingly the file:
    mode = "w"
    if inspect.signature(serializer).return_annotation == bytes:
        mode = "wb"

    async with aiofiles.open(folder / f"{file_name}.{extension}", mode) as f:
        await f.write(serializer(object_))


def function_saver(*args, save_in=True, save_out=True, save_internals=True):
    def decorator(func_: Callable) -> Callable:
        """
        Decorator to save inputs and output of a function to a folder.
        Also save internal variables if requested.

        Some env variables can be set to control the behavior of the decorator:

          - Variables for def one_function(...):
            - FUNCTION_SAVER_ONE_FUNCTION=1 to enable saving
            - FUNCTION_SAVER_INTERNALS_ONE_FUNCTION=1 to enable saving internal variables

        - Global variables (for all decorated functions):
            - FUNCTION_SAVER_ROOT_PATH to set the root path where to save the data.
                Default is the system temp folder / function_saver
            - FUNCTION_SAVER_ALL=1 to enable saving
            - FUNCTION_SAVER_INTERNALS_ALL=1 to enable saving internal variables
            - FUNCTION_SAVER_LOG=1 to enable logging (global for all functions)

        Usage exemple:
        ```python
        @function_saver
        def a_function(a: int, b: int) -> int:
            image = compute_image(a, b)
            a_function.save_internal(image, "image")
            return a + b
        ```

        """
        thread_data = ContextData()

        def log(message: str):
            if thread_data.verbose:
                separator = " "
                if message and message[0] == ">":
                    separator = ""
                logger.debug(">>>>>>>>>>>>>" + separator + message)

        def is_save_internal_enabled() -> bool:
            if _function_saver_replaying.get() == "1":
                internal_folder = (
                    Path(_function_saver_replaying_folder.get()) / "internal"
                )
                # if internal data were saved:
                if internal_folder.exists():
                    return True
                return False
            return thread_data.option_save_internals and thread_data.save_internals

        def save_internal(var_value, var_name, serializer_type=None):
            """
            Save an internal variable to the internal folder of the function.

            Args:
                var_value: the variable to save
                var_name: the name of the variable, used as file name.
                    It cannot be deduced from the variable value itself because you may call save_internal with
                    a variable that is not a variable in the function (i.e. a + b, etc.)
                serializer_type: Optional. The Serializer type to use.
                                 If not provided, it will be deduced from the variable.
            """
            destination_folder = thread_data.internal_folder
            if _function_saver_replaying.get() == "1":
                destination_folder = (
                    Path(_function_saver_replaying_folder.get()) / "internal"
                )
                # if internal data were saved, we save also when replaying.
                if not destination_folder.exists():
                    return
                thread_data.option_save_internals = True
                thread_data.save_internals = True
                destination_folder /= "../internal_replay"
                if _function_saver_replaying_already_delete.get() == "0":
                    shutil.rmtree(destination_folder, ignore_errors=True)
                    _function_saver_replaying_already_delete.set("1")
                    destination_folder.mkdir(parents=True)
            if not thread_data.option_save_internals:
                return
            if not thread_data.save_internals:
                return
            log(f">>>>>>>> Saving internal variable {var_name}")
            if serializer_type is None:
                serializer_type = type(var_value)
            try:
                _do_serialize(serializer_type, var_value, destination_folder, var_name)
            except Exception as e:
                logger.error(
                    f"Error while saving internal variable {var_name} for function {func_.__name__}. {e}"
                )

        async def save_internal_async(var_value, var_name, serializer_type=None):
            """
            Save an internal variable to the internal folder of the function.

            Args:
                var_value: the variable to save
                var_name: the name of the variable, used as file name.
                    It cannot be deduced from the variable value itself because you may call save_internal with
                    a variable that is not a variable in the function (i.e. a + b, etc.)
                serializer_type: Optional. The Serializer type to use.
                                 If not provided, it will be deduced from the variable.
            """
            destination_folder = thread_data.internal_folder
            if _function_saver_replaying.get() == "1":
                destination_folder = (
                    Path(_function_saver_replaying_folder.get()) / "internal"
                )
                # if internal data were saved, we save also when replaying.
                if not destination_folder.exists():
                    return
                thread_data.option_save_internals = True
                thread_data.save_internals = True
                destination_folder /= "../internal_replay"
                if _function_saver_replaying_already_delete.get() == "0":
                    shutil.rmtree(destination_folder, ignore_errors=True)
                    _function_saver_replaying_already_delete.set("1")
                    destination_folder.mkdir(parents=True)
            if not thread_data.option_save_internals:
                return
            if not thread_data.save_internals:
                return
            log(f">>>>>>>> Saving internal variable {var_name}")
            if serializer_type is None:
                serializer_type = type(var_value)
            try:
                await _do_serialize_async(
                    serializer_type, var_value, destination_folder, var_name
                )
            except Exception as e:
                logger.error(
                    f"Error while saving internal variable {var_name} for function {func_.__name__}. {e}"
                )

        @wraps(func_)
        def wrapper_sync(*args_, **kwargs) -> Any:
            if _function_saver_replaying.get() == "1":
                return func_(*args_, **kwargs)
            function_name = func_.__name__
            if os.getenv("FUNCTION_SAVER_ALL", "0") == "1":
                save = True
            else:
                save = os.getenv(f"FUNCTION_SAVER_{function_name.upper()}", "0") == "1"
            if os.getenv("FUNCTION_SAVER_INTERNALS_ALL", "0") == "1":
                thread_data.save_internals = True
            else:
                thread_data.save_internals = (
                    os.getenv(f"FUNCTION_SAVER_INTERNALS_{function_name.upper()}", "0")
                    == "1"
                )
            thread_data.verbose = os.getenv("FUNCTION_SAVER_LOG", "0") == "1"
            log(
                f"Function saver for {function_name}: save={save}, save_internals={thread_data.save_internals},"
                f"verbose={thread_data.verbose}"
            )

            if not save:
                return func_(*args_, **kwargs)

            thread_data.option_save_in = save_in
            thread_data.option_save_out = save_out
            thread_data.option_save_internals = save_internals

            function_saver_root_path = os.getenv(
                "FUNCTION_SAVER_ROOT_PATH", tempfile.gettempdir() + "/function_saver"
            )
            log(f"Function saver for {function_name}")
            folder = function_name + datetime.datetime.now().strftime(
                "_%Y_%m_%d__%Hh%Mm%S.%f"
            )
            save_folder = Path(function_saver_root_path) / folder
            save_folder_filesystem_link = save_folder.resolve().as_uri()
            input_folder = save_folder / "inputs"
            output_folder = save_folder / "output"
            if thread_data.option_save_internals:
                thread_data.internal_folder = save_folder / "internal"
                thread_data.internal_folder.mkdir(parents=True, exist_ok=True)
            try:
                if thread_data.option_save_in:
                    input_folder.mkdir(parents=True, exist_ok=True)
                if thread_data.option_save_out:
                    output_folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(
                    f"Error while creating folders for saving in out of function {func_.__name__}. {e}. "
                    f"Let's skip the saving and just call the function."
                )
                return func_(*args_, **kwargs)
            log(f">>>>>>>> Saving inputs and output to {save_folder_filesystem_link}")
            output = func_(*args_, **kwargs)
            try:
                signature = inspect.signature(func_)
                output_arg_type = signature.return_annotation
                bound_args = signature.bind_partial(*args_, **kwargs)
                bound_args.apply_defaults()
                if thread_data.option_save_in:
                    for arg_name, value in bound_args.arguments.items():
                        # Skip serializing 'self'
                        if arg_name == "self":
                            continue
                        arg_type = signature.parameters[arg_name].annotation
                        _do_serialize(arg_type, value, input_folder, arg_name)
                if thread_data.option_save_out:
                    _do_serialize(output_arg_type, output, output_folder, "output")
                logger.debug(
                    f"Data of function {function_name} saved to: {save_folder_filesystem_link}"
                )
            except Exception as e:
                logger.error(
                    f"Error while saving in out of function {func_.__name__}. {e}."
                )
            finally:
                return output

        @wraps(func_)
        async def wrapper_async(*args_, **kwargs) -> Any:
            if _function_saver_replaying.get() == "1":
                return await func_(*args_, **kwargs)
            function_name = func_.__name__
            if os.getenv("FUNCTION_SAVER_ALL", "0") == "1":
                save = True
            else:
                save = os.getenv(f"FUNCTION_SAVER_{function_name.upper()}", "0") == "1"
            if os.getenv("FUNCTION_SAVER_INTERNALS_ALL", "0") == "1":
                thread_data.save_internals = True
            else:
                thread_data.save_internals = (
                    os.getenv(f"FUNCTION_SAVER_INTERNALS_{function_name.upper()}", "0")
                    == "1"
                )
            thread_data.verbose = os.getenv("FUNCTION_SAVER_LOG", "0") == "1"
            log(
                f"Function saver for {function_name}: save={save}, save_internals={thread_data.save_internals},"
                f"verbose={thread_data.verbose}"
            )

            if not save:
                return await func_(*args_, **kwargs)

            thread_data.option_save_in = save_in
            thread_data.option_save_out = save_out
            thread_data.option_save_internals = save_internals

            function_saver_root_path = os.getenv(
                "FUNCTION_SAVER_ROOT_PATH", tempfile.gettempdir() + "/function_saver"
            )
            log(f"Function saver for {function_name}")
            folder = function_name + datetime.datetime.now().strftime(
                "_%Y_%m_%d__%Hh%Mm%S.%f"
            )
            save_folder = Path(function_saver_root_path) / folder
            save_folder_filesystem_link = save_folder.resolve().as_uri()
            input_folder = save_folder / "inputs"
            output_folder = save_folder / "output"
            if thread_data.option_save_internals:
                thread_data.internal_folder = save_folder / "internal"
                thread_data.internal_folder.mkdir(parents=True, exist_ok=True)
            try:
                if thread_data.option_save_in:
                    input_folder.mkdir(parents=True, exist_ok=True)
                if thread_data.option_save_out:
                    output_folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(
                    f"Error while creating folders for saving in out of function {func_.__name__}. {e}. "
                    f"Let's skip the saving and just call the function."
                )
                return await func_(*args_, **kwargs)
            log(f">>>>>>>> Saving inputs and output to {save_folder_filesystem_link}")
            output = await func_(*args_, **kwargs)
            try:
                signature = inspect.signature(func_)
                output_arg_type = signature.return_annotation
                bound_args = signature.bind_partial(*args_, **kwargs)
                bound_args.apply_defaults()
                if thread_data.option_save_in:
                    for arg_name, value in bound_args.arguments.items():
                        # Skip serializing 'self'
                        if arg_name == "self":
                            continue
                        arg_type = signature.parameters[arg_name].annotation
                        await _do_serialize_async(
                            arg_type, value, input_folder, arg_name
                        )
                if thread_data.option_save_out:
                    await _do_serialize_async(
                        output_arg_type, output, output_folder, "output"
                    )
                logger.debug(
                    f"Data of function {function_name} saved to: {save_folder_filesystem_link}"
                )
            except Exception as e:
                logger.error(
                    f"Error while saving in out of function {func_.__name__}. {e}."
                )
            finally:
                return output

        def is_coroutine_function(a_function):
            while isinstance(a_function, functools.partial):
                a_function = a_function.func
            return asyncio.iscoroutinefunction(a_function)

        wrapper_sync.save_internal = save_internal
        wrapper_sync.is_save_internal_enabled = is_save_internal_enabled
        wrapper_async.is_save_internal_enabled = is_save_internal_enabled
        wrapper_async.save_internal = save_internal
        wrapper_async.save_internal_async = save_internal_async
        if is_coroutine_function(func_):
            return wrapper_async
        return wrapper_sync

    # this piece of code is to handle the case where the decorator is used with or without parenthesis
    if args and callable(args[0]):  # if the decorator is used without parenthesis
        func = args[0]
        return decorator(func)

    return decorator


def replay_function(function: callable, folder_path: str | Path):
    """
    Replay the function saved data from a folder.

    Raises:
        FileNotFoundError: if the input file is not found or if multiple files are found
        ReplayException: if an error occurs while deserializing the arguments

    Args:
        function: the function to replay
        folder_path: the path to the folder where the data have been saved
    """
    if isinstance(folder_path, str):
        folder_path = Path(folder_path)
    logger.info(f"Replaying function {function.__name__} from {folder_path}")
    input_folder = folder_path / "inputs"
    if not input_folder.exists():
        raise FileNotFoundError(f"Folder {input_folder} does not exist")
    arg_names = inspect.signature(function).parameters
    args = []
    all_args_deserialized = True
    for arg_name in arg_names:
        input_files = list(input_folder.glob(f"{arg_name}.*"))
        if not input_files:
            raise FileNotFoundError(f"No file found for argument {arg_name}")
        if len(input_files) > 1:
            raise ValueError(f"Multiple files found for argument {arg_name}")
        extension = "".join(input_files[0].suffixes)
        if extension.startswith("."):
            extension = extension[1:]
        deserialize, read_mode = _get_deserializer(extension)
        with open(input_files[0], read_mode) as f:
            try:
                arg = deserialize(f.read())
                args.append(arg)
            except jsons.exceptions.SignatureMismatchError as e:
                logger.error(
                    f"Error while deserializing argument {arg_name} for function {function.__name__}.\n"
                    f"You probably didn't provide {e.argument} in __init__ of {e.target.__name__}.\n"
                    f"Exception message: {e}"
                )
                all_args_deserialized = False
    if all_args_deserialized:
        with replaying(folder_path):
            output = function(*args)
            output_folder = folder_path / "output"
            # if output was saved, we also save at replay
            try:
                if not output_folder.exists():
                    return output
                output_replay_folder = output_folder / "../output_replay"
                shutil.rmtree(output_replay_folder, ignore_errors=True)
                output_replay_folder.mkdir(parents=True)
                signature = inspect.signature(function)
                output_arg_type = signature.return_annotation
                _do_serialize(output_arg_type, output, output_replay_folder, "output")
            finally:
                return output
    else:
        raise ReplayException("Error while deserializing arguments. Read the logs.")


async def replay_function_async(function: callable, folder_path: str | Path):
    """The async version of replay_function"""
    if isinstance(folder_path, str):
        folder_path = Path(folder_path)
    logger.info(f"Replaying function {function.__name__} from {folder_path}")
    input_folder = folder_path / "inputs"
    if not input_folder.exists():
        raise FileNotFoundError(f"Folder {input_folder} does not exist")
    arg_names = inspect.signature(function).parameters
    args = []
    all_args_deserialized = True
    for arg_name in arg_names:
        input_files = list(input_folder.glob(f"{arg_name}.*"))
        if not input_files:
            raise FileNotFoundError(f"No file found for argument {arg_name}")
        if len(input_files) > 1:
            raise ValueError(f"Multiple files found for argument {arg_name}")
        extension = input_files[0].suffix
        if extension.startswith("."):
            extension = extension[1:]
        deserialize, read_mode = _get_deserializer(extension)
        async with aiofiles.open(input_files[0], read_mode) as f:
            try:
                arg = deserialize(await f.read())
                args.append(arg)
            except jsons.exceptions.SignatureMismatchError as e:
                logger.error(
                    f"Error while deserializing argument {arg_name} for function {function.__name__}.\n"
                    f"You probably didn't provide {e.argument} in __init__ of {e.target.__name__}.\n"
                    f"Exception message: {e}"
                )
                all_args_deserialized = False
    if all_args_deserialized:
        async with replaying_async(folder_path):
            output = await function(*args)
            output_folder = folder_path / "output"
            # if output was saved, we also save at replay
            try:
                if not output_folder.exists():
                    return output
                output_replay_folder = output_folder / "../output_replay"
                shutil.rmtree(output_replay_folder, ignore_errors=True)
                output_replay_folder.mkdir(parents=True)
                signature = inspect.signature(function)
                output_arg_type = signature.return_annotation
                await _do_serialize_async(
                    output_arg_type, output, output_replay_folder, "output"
                )
            finally:
                return output
    else:
        raise ReplayException("Error while deserializing arguments. Read the logs.")


def replay_and_check_function(
    function: callable,
    folder_path: str | Path,
    compare_function: callable = lambda x, y: x == y,
):
    """
    Replay the function saved data from a folder and check the output.

    Args:
        function: the function to replay
        folder_path: the path to the folder where the data have been saved
        compare_function: the function to compare the output with the expected output
            default is a simple equality check

    Returns:
        The output of the function

    Raises:
        AssertionError: if the output does not match the expected output
        FileNotFoundError: if the output file is not found or if multiple files are found
    """
    output_folder = folder_path / "output"
    if not output_folder.exists():
        raise FileNotFoundError(f"Folder {output_folder} does not exist")
    output_files = list(output_folder.glob("output.*"))
    output_files_count = len(output_files)
    if output_files_count == 0:
        raise FileNotFoundError(
            f"No file found for output in {output_folder}. We expect one file named 'output.*'"
        )
    if output_files_count > 1:
        raise FileNotFoundError(
            f"Multiple files found for output in {output_folder}. We expect one file named 'output.*'"
        )
    output_file = output_files[0]
    extension = output_file.suffix
    if extension.startswith("."):
        extension = extension[1:]
    deserialize, read_mode = _get_deserializer(extension)
    with open(output_file, read_mode) as f:
        expected_output = deserialize(f.read())
    output = replay_function(function, folder_path)
    if not compare_function(output, expected_output):
        raise AssertionError(
            f"Output does not match the expected output: {output} != {expected_output}"
        )
    return output


async def replay_and_check_function_async(
    function: callable,
    folder_path: str | Path,
    compare_function: callable = lambda x, y: x == y,
):
    """The async version of replay_and_check_function"""
    output_folder = folder_path / "output"
    if not output_folder.exists():
        raise FileNotFoundError(f"Folder {output_folder} does not exist")
    output_files = list(output_folder.glob("output.*"))
    output_files_count = len(output_files)
    if output_files_count == 0:
        raise FileNotFoundError(
            f"No file found for output in {output_folder}. We expect one file named 'output.*'"
        )
    if output_files_count > 1:
        raise FileNotFoundError(
            f"Multiple files found for output in {output_folder}. We expect one file named 'output.*'"
        )
    output_file = output_files[0]
    extension = output_file.suffix
    if extension.startswith("."):
        extension = extension[1:]
    deserialize, read_mode = _get_deserializer(extension)
    async with aiofiles.open(output_file, read_mode) as f:
        expected_output = deserialize(await f.read())
    output = await replay_function_async(function, folder_path)
    if not compare_function(output, expected_output):
        raise AssertionError(
            f"Output does not match the expected output: {output} != {expected_output}"
        )
    return output
