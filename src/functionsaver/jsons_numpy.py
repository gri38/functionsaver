"""
This file allows to define a custom json serialization for numpy arrays for jsons package.
"""

from base64 import b64encode, b64decode

import numpy as np
from jsons import DeserializationError, set_serializer, set_deserializer
from numpy.lib.format import dtype_to_descr, descr_to_dtype

from mycronic.functionsaver.numpy_types import NumpyTypes


def default_np_array_serializer(obj: np.ndarray, **_) -> dict:
    return {
        "__numpy__": b64encode(
            obj.data if obj.flags.c_contiguous else obj.tobytes()
        ).decode(),
        "dtype": dtype_to_descr(obj.dtype),
        "shape": obj.shape,
    }


def default_np_array_deserializer(obj: dict, cls: type = np.ndarray, **_) -> np.ndarray:
    if "__numpy__" in obj:
        np_obj = np.frombuffer(
            b64decode(obj["__numpy__"]), descr_to_dtype(obj["dtype"])
        )
        return np_obj.reshape(shape) if (shape := obj["shape"]) else np_obj[0]
    raise DeserializationError(
        message="The given object is not a numpy array.", source=obj, target=cls
    )


def create_np_serializer(cls):
    """
    This function is meant to factorize the creation of numpy serializers:
    simply stringify.
    """

    def np_serializer(obj: cls, **_) -> str:
        return str(obj)

    return np_serializer


def create_np_deserializer(cls):
    """
    This function is meant to factorize the creation of numpy deserializers:
    simply type and build from str.
    """

    def np_deserializer(obj: str, cls_: type = cls, **_) -> cls:
        return cls_(obj)

    return np_deserializer


set_serializer(default_np_array_serializer, np.ndarray)
set_deserializer(default_np_array_deserializer, np.ndarray)


for np_type in NumpyTypes().types():
    set_serializer(create_np_serializer(np_type), np_type)
    set_deserializer(create_np_deserializer(np_type), np_type)
