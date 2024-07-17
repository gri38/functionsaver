import inspect
import io
from functools import partial
from types import UnionType
from typing import Tuple, get_args, Callable, get_origin, Union

import jsons
import numpy as np
from PIL import Image

from mycronic.functionsaver.numpy_types import NumpyTypes


def np_array_png_serializer(array) -> bytes:
    """
    Serialize a numpy array to PNG

    Raises:
        AssertionError: if the input is not a numpy array
    """
    if not isinstance(array, np.ndarray):
        raise AssertionError("Input must be a numpy array")
    img = Image.fromarray(array)
    byte_io = io.BytesIO()
    img.save(byte_io, format="PNG")
    png_data = byte_io.getvalue()
    return png_data


def np_array_png_deserializer(data: bytes) -> np.ndarray:
    """
    Deserialize a numpy array from PNG

    Raises:
        AssertionError: if the input is not bytes
    """
    if not isinstance(data, bytes):
        raise AssertionError("Input must be bytes")
    byte_io = io.BytesIO(data)
    img = Image.open(byte_io)
    return np.array(img)


class SerializeAsArrayPng:
    pass


def np_array_binary_dump(array: np.ndarray) -> bytes:
    """
    Dump a numpy array to bytes

    Raises:
        AssertionError: if the input is not a numpy array
    """
    if not isinstance(array, np.ndarray):
        raise AssertionError("Input must be a numpy array")
    mem_io = io.BytesIO()
    np.save(mem_io, array)  # noqa
    return mem_io.getvalue()


def np_array_binary_load(data: bytes) -> np.ndarray:
    """
    Load a numpy array from bytes

    Raises:
        AssertionError: if the input is not bytes
    """
    if not isinstance(data, bytes):
        raise AssertionError("Input must be bytes")
    mem_io = io.BytesIO(data)
    return np.load(mem_io)


def np_deserializer(cls: type) -> Callable[[str], type]:
    """This function is for factorizing the creation of numpy deserializers."""

    def deserializer(data: str) -> cls:
        return jsons.loads(data, cls=cls)

    return deserializer


_function_saver_serializers: dict[type, (Callable, str)] = {
    np.ndarray: (np_array_binary_dump, "npy"),
    **{
        np_type: (jsons.dumps, ext)
        for np_type, ext in NumpyTypes.types_and_extensions()
    },
}

_function_saver_deserializers: dict[str, Callable] = {
    "npy": np_array_binary_load,
    **{
        ext: np_deserializer(np_type)
        for np_type, ext in NumpyTypes.types_and_extensions()
    },
}


def _get_serializer(type_arg: type, dynamic_type: type) -> Tuple[callable, str]:
    if type_arg is None or type_arg == inspect.Signature.empty:
        type_arg = dynamic_type
    # if type_args is a union (int | float, or typing.Union[int, float]) we get the types in a list
    if get_origin(type_arg) is Union or isinstance(type_arg, UnionType):
        types = get_args(type_arg)
        # we order types so that SerializeAs... are first, to be preferred
        types = sorted(
            types, key=lambda x: not str(x.__name__).startswith("SerializeAs")
        )
    else:
        types = [type_arg]
    for type_ in types:
        if type_ in _function_saver_serializers:  # noqa
            serializer, extension = _function_saver_serializers[type_]  # noqa
            break
    else:
        serializer, extension = (
            lambda x: jsons.dumps(x, jdkwargs={"indent": 2}, verbose=True),
            "json",
        )
    return serializer, extension


def _get_deserializer(extension: str) -> Tuple[callable, str]:
    """
    Get the deserializer function and the mode to open the file

    Raises:
        AssertionError: if the deserializer function does not take a string or bytes
    """
    deserializer = partial(jsons.loads, strict=True)
    if extension in _function_saver_deserializers:
        deserializer = _function_saver_deserializers[extension]
    deserializer_signature = inspect.signature(deserializer)
    if len(deserializer_signature.parameters) == 0:
        raise AssertionError("Deserializer function must take at least one argument")
    first_parameter = next(iter(deserializer_signature.parameters.values()))
    if first_parameter.annotation not in (str, bytes):
        raise AssertionError("Deserializer function must take a string or bytes")
    if first_parameter.annotation == str:
        return deserializer, "r"
    return deserializer, "rb"


def register_serializer(
    type_arg: type, serializer: callable, deserializer: callable, file_extension: str
):
    """
    Register a serializer and deserializer for a type
    Raises:
        AssertionError: if the args doesn't meet requirements
        ValueError: if the serializer or the deserializer for the type is already registered
    """
    if not inspect.isclass(type_arg):
        raise AssertionError("First argument must be a type")
    if not str(type_arg.__name__).startswith("SerializeAs"):
        raise AssertionError(
            f"Type must start with 'SerializeAs', it is {type_arg.__name__}"
        )
    if not callable(serializer):
        raise AssertionError("Second argument must be a callable")
    if not callable(deserializer):
        raise AssertionError("Third argument must be a callable")
    if file_extension.startswith("."):
        raise AssertionError("File extension must not include a dot")
    serializer_signature = inspect.signature(serializer)
    if len(serializer_signature.parameters) != 1:
        raise AssertionError("Serializer function must take one argument")
    if serializer_signature.return_annotation not in (str, bytes):
        raise AssertionError("Serializer function must return a string or bytes")
    deserializer_signature = inspect.signature(deserializer)
    if len(deserializer_signature.parameters) != 1:
        raise AssertionError("Deserializer function must take one argument")
    deserializer_first_parameter = next(
        iter(deserializer_signature.parameters.values())
    )
    if deserializer_first_parameter.annotation not in (str, bytes):
        raise AssertionError("Deserializer function must take a string or bytes")

    if type_arg in _function_saver_serializers:
        raise ValueError(f"Serializer for type {type_arg} already registered")
    _function_saver_serializers[type_arg] = serializer, file_extension

    if file_extension in _function_saver_deserializers:
        raise ValueError(
            f"Deserializer for extension {file_extension} already registered"
        )
    _function_saver_deserializers[file_extension] = deserializer


register_serializer(
    SerializeAsArrayPng, np_array_png_serializer, np_array_png_deserializer, "png"
)
