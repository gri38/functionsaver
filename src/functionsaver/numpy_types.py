import numpy as np


class NumpyTypes:
    _types_with_extensions = [
        (np.float64, "f64.json"),
        (np.float32, "f32.json"),
        (np.float16, "f16.json"),
        (np.half, "half.json"),
        (np.int64, "i64.json"),
        (np.int32, "i32.json"),
        (np.int16, "i16.json"),
        (np.int8, "i8.json"),
        (np.uint64, "ui64.json"),
        (np.uint32, "ui32.json"),
        (np.uint16, "ui16.json"),
        (np.uint8, "ui8.json"),
        (np.intp, "ip.json"),
        (np.uintp, "uip.json"),
        (np.datetime64, "npdt.json"),
    ]

    @staticmethod
    def types():
        """Returns an iterator on numpy types"""
        for np_type, _ in NumpyTypes._types_with_extensions:
            yield np_type

    @staticmethod
    def types_and_extensions():
        """Returns an iterator on numpy types and their extensions"""
        yield from NumpyTypes._types_with_extensions
