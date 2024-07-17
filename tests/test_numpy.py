from datetime import datetime
from pathlib import Path

import numpy as np

from functionsaver import function_saver, replay_function


def test_save_nested_numpy(reset_environment, fonctionsaver_in_tempfolder):
    class ClassWithNestedNumpy:
        def __init__(
            self,
            array: np.ndarray = np.zeros((10, 10), dtype=np.uint8),
            now: datetime = datetime.now(),
            f64: np.float64 = np.float64(1.23),
        ):
            self.array = array
            self.now = now
            self.f64 = f64

    @function_saver
    def function_to_be_saved(obj: ClassWithNestedNumpy):
        assert function_to_be_saved.is_save_internal_enabled() is True
        assert isinstance(obj, ClassWithNestedNumpy)
        assert isinstance(obj.now, datetime)
        assert isinstance(obj.f64, np.float64)
        return obj

    temp_folder = fonctionsaver_in_tempfolder

    res = function_to_be_saved(ClassWithNestedNumpy())

    # replay and check it is the same
    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            res2 = replay_function(function_to_be_saved, dir_path)
            assert type(res2) is type(res)
            assert type(res2.array) is type(res.array)
            assert np.all(res2.array == res.array)
            assert np.equal(res2.f64, res.f64)
            break
    else:
        assert False, "Cannot find a folder for replay"


def test_numpy_temp(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver
    def f(lf64: list[np.float64]) -> None:
        pass  # ici ça va pas on a au replay une list de str au lieu d'une liste de np.float64.

    # il faudrait un test d'une fonction avec une liste de différents types.

    temp_folder = fonctionsaver_in_tempfolder

    lf64_ = np.float64(1.234567890123456)
    f([lf64_])

    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            replay_function(f, dir_path)


def test_numpy_types(reset_environment, fonctionsaver_in_tempfolder):
    @function_saver
    def in_out_internal_numpy(
        f64: np.float64,
        f32: np.float32,
        f16: np.float16,
        h: np.half,
        i64: np.int64,
        i32: np.int32,
        i16: np.int16,
        i8: np.int8,
        ui64: np.uint64,
        ui32: np.uint32,
        ui16: np.uint16,
        ui8: np.uint8,
        intp: np.intp,
        uintp: np.uintp,
        npdt: np.datetime64,
        lf64: list[np.float64],
        lf32: list[np.float32],
        lf16: list[np.float16],
        lh: list[np.half],
        li64: list[np.int64],
        li32: list[np.int32],
        li16: list[np.int16],
        li8: list[np.int8],
        lui64: list[np.uint64],
        lui32: list[np.uint32],
        lui16: list[np.uint16],
        lui8: list[np.uint8],
        lintp: list[np.intp],
        luintp: list[np.uintp],
        lnpdt: list[np.datetime64],
    ) -> tuple[
        np.float64,
        np.float32,
        np.float16,
        np.half,
        np.int64,
        np.int32,
        np.int16,
        np.int8,
        np.uint64,
        np.uint32,
        np.uint16,
        np.uint8,
        np.intp,
        np.uintp,
        np.datetime64,
        list[np.float64],
        list[np.float32],
        list[np.float16],
        list[np.half],
        list[np.int64],
        list[np.int32],
        list[np.int16],
        list[np.int8],
        list[np.uint64],
        list[np.uint32],
        list[np.uint16],
        list[np.uint8],
        list[np.intp],
        list[np.uintp],
        list[np.datetime64],
    ]:
        assert in_out_internal_numpy.is_save_internal_enabled() is True
        assert isinstance(f64, np.float64)
        assert isinstance(f32, np.float32)
        assert isinstance(f16, np.float16)
        assert isinstance(h, np.half)
        assert isinstance(i64, np.int64)
        assert isinstance(i32, np.int32)
        assert isinstance(i16, np.int16)
        assert isinstance(i8, np.int8)
        assert isinstance(ui64, np.uint64)
        assert isinstance(ui32, np.uint32)
        assert isinstance(ui16, np.uint16)
        assert isinstance(ui8, np.uint8)
        assert isinstance(intp, np.intp)
        assert isinstance(uintp, np.uintp)
        assert isinstance(npdt, np.datetime64)

        assert isinstance(lf64, list)
        assert isinstance(lf32, list)
        assert isinstance(lf16, list)
        assert isinstance(lh, list)
        assert isinstance(li64, list)
        assert isinstance(li32, list)
        assert isinstance(li16, list)
        assert isinstance(li8, list)
        assert isinstance(lui64, list)
        assert isinstance(lui32, list)
        assert isinstance(lui16, list)
        assert isinstance(lui8, list)
        assert isinstance(lintp, list)
        assert isinstance(luintp, list)
        assert isinstance(lnpdt, list)

        assert isinstance(lf64[0], np.float64)
        assert isinstance(lf32[0], np.float32)
        assert isinstance(lf16[0], np.float16)
        assert isinstance(lh[0], np.half)
        assert isinstance(li64[0], np.int64)
        assert isinstance(li32[0], np.int32)
        assert isinstance(li16[0], np.int16)
        assert isinstance(li8[0], np.int8)
        assert isinstance(lui64[0], np.uint64)
        assert isinstance(lui32[0], np.uint32)
        assert isinstance(lui16[0], np.uint16)
        assert isinstance(lui8[0], np.uint8)
        assert isinstance(lintp[0], np.intp)
        assert isinstance(luintp[0], np.uintp)
        assert isinstance(lnpdt[0], np.datetime64)

        assert np.equal(f64, np.float64(1.234567890123456))
        assert np.equal(f32, np.float32(1.2345678))
        assert np.equal(f16, np.float16(1.234))
        assert np.equal(h, np.half(1.234))
        assert np.equal(i64, np.int64(-1234567890123456789))
        assert np.equal(i32, np.int32(-123456789))
        assert np.equal(i16, np.int16(-12345))
        assert np.equal(i8, np.int8(-123))
        assert np.equal(ui64, np.uint64(1234567890123456789))
        assert np.equal(ui32, np.uint32(123456789))
        assert np.equal(ui16, np.uint16(12345))
        assert np.equal(ui8, np.uint8(123))
        assert np.equal(intp, np.intp(-1234567890123456789))
        assert np.equal(uintp, np.uintp(1234567890123456789))
        assert np.equal(npdt, np.datetime64("1979-11-28T12:31:33+0000"))

        assert np.equal(lf64[0], np.float64(1.234567890123456))
        assert np.equal(lf32[0], np.float32(1.2345678))
        assert np.equal(lf16[0], np.float16(1.234))
        assert np.equal(lh[0], np.half(1.234))
        assert np.equal(li64[0], np.int64(-1234567890123456789))
        assert np.equal(li32[0], np.int32(-123456789))
        assert np.equal(li16[0], np.int16(-12345))
        assert np.equal(li8[0], np.int8(-123))
        assert np.equal(lui64[0], np.uint64(1234567890123456789))
        assert np.equal(lui32[0], np.uint32(123456789))
        assert np.equal(lui16[0], np.uint16(12345))
        assert np.equal(lui8[0], np.uint8(123))
        assert np.equal(lintp[0], np.intp(-1234567890123456789))
        assert np.equal(luintp[0], np.uintp(1234567890123456789))
        assert np.equal(lnpdt[0], np.datetime64("1979-11-28T12:31:33+0000"))

        in_out_internal_numpy.save_internal(f64, "f64")
        in_out_internal_numpy.save_internal(f32, "f32")
        in_out_internal_numpy.save_internal(f16, "f16")
        in_out_internal_numpy.save_internal(h, "half")
        in_out_internal_numpy.save_internal(i64, "i64")
        in_out_internal_numpy.save_internal(i32, "i32")
        in_out_internal_numpy.save_internal(i16, "i16")
        in_out_internal_numpy.save_internal(i8, "i8")
        in_out_internal_numpy.save_internal(ui64, "ui64")
        in_out_internal_numpy.save_internal(ui32, "ui32")
        in_out_internal_numpy.save_internal(ui16, "ui16")
        in_out_internal_numpy.save_internal(ui8, "ui8")
        in_out_internal_numpy.save_internal(intp, "ip")
        in_out_internal_numpy.save_internal(uintp, "uip")
        in_out_internal_numpy.save_internal(npdt, "npdt")

        in_out_internal_numpy.save_internal(lf64, "lf64")
        in_out_internal_numpy.save_internal(lf32, "lf32")
        in_out_internal_numpy.save_internal(lf16, "lf16")
        in_out_internal_numpy.save_internal(lh, "lhalf")
        in_out_internal_numpy.save_internal(li64, "li64")
        in_out_internal_numpy.save_internal(li32, "li32")
        in_out_internal_numpy.save_internal(li16, "li16")
        in_out_internal_numpy.save_internal(li8, "li8")
        in_out_internal_numpy.save_internal(lui64, "lui64")
        in_out_internal_numpy.save_internal(lui32, "lui32")
        in_out_internal_numpy.save_internal(lui16, "lui16")
        in_out_internal_numpy.save_internal(lui8, "lui8")
        in_out_internal_numpy.save_internal(lintp, "lip")
        in_out_internal_numpy.save_internal(luintp, "luip")
        in_out_internal_numpy.save_internal(lnpdt, "lnpdt")

        return (
            f64,
            f32,
            f16,
            h,
            i64,
            i32,
            i16,
            i8,
            ui64,
            ui32,
            ui16,
            ui8,
            intp,
            uintp,
            npdt,
            lf64,
            lf32,
            lf16,
            lh,
            li64,
            li32,
            li16,
            li8,
            lui64,
            lui32,
            lui16,
            lui8,
            lintp,
            luintp,
            lnpdt,
        )

    temp_folder = fonctionsaver_in_tempfolder
    f64_ = np.float64(1.234567890123456)
    f32_ = np.float32(1.2345678)
    f16_ = np.float16(1.234)
    h_ = np.half(1.234)
    i64_ = np.int64(-1234567890123456789)
    i32_ = np.int32(-123456789)
    i16_ = np.int16(-12345)
    i8_ = np.int8(-123)
    ui64_ = np.uint64(1234567890123456789)
    ui32_ = np.uint32(123456789)
    ui16_ = np.uint16(12345)
    ui8_ = np.uint8(123)
    intp_ = np.intp(-1234567890123456789)
    uintp_ = np.uintp(1234567890123456789)
    npdt_ = np.datetime64("1979-11-28T12:31:33+0000")

    lf64_ = [np.float64(1.234567890123456)]
    lf32_ = [np.float32(1.2345678)]
    lf16_ = [np.float16(1.234)]
    lh_ = [np.half(1.234)]
    li64_ = [np.int64(-1234567890123456789)]
    li32_ = [np.int32(-123456789)]
    li16_ = [np.int16(-12345)]
    li8_ = [np.int8(-123)]
    lui64_ = [np.uint64(1234567890123456789)]
    lui32_ = [np.uint32(123456789)]
    lui16_ = [np.uint16(12345)]
    lui8_ = [np.uint8(123)]
    lintp_ = [np.intp(-1234567890123456789)]
    luintp_ = [np.uintp(1234567890123456789)]
    lnpdt_ = [np.datetime64("1979-11-28T12:31:33+0000")]

    res = in_out_internal_numpy(
        f64_,
        f32_,
        f16_,
        h_,
        i64_,
        i32_,
        i16_,
        i8_,
        ui64_,
        ui32_,
        ui16_,
        ui8_,
        intp_,
        uintp_,
        npdt_,
        lf64_,
        lf32_,
        lf16_,
        lh_,
        li64_,
        li32_,
        li16_,
        li8_,
        lui64_,
        lui32_,
        lui16_,
        lui8_,
        lintp_,
        luintp_,
        lnpdt_,
    )

    # replay and check it is the same
    for dir_path in Path(temp_folder).iterdir():
        if dir_path.is_dir():
            res2 = replay_function(in_out_internal_numpy, dir_path)
            for ref, replay in zip(res, res2):
                assert type(ref) is type(replay)
                if isinstance(ref, list):
                    assert type(ref[0]) is type(replay[0])
                    assert np.equal(ref[0], replay[0])
                else:
                    assert np.equal(ref, replay)
            break
    else:
        assert False, "Cannot find a folder for replay"
