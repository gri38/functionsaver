import pytest

from functionsaver import register_serializer


def test_register_serializer_type():
    """
    This test checks the requirements of a serializer and deserializer
    are indeed checked and raises the correct errors

    !!!! WARNING !!!!:
        don't change this test unless you know what you are doing:
        for instance the fact the serializer must define a return type of str or bytes is a requirement of _do_serialize
    """
    with pytest.raises(AssertionError, match="Type must start with 'SerializeAs', it is"):
        register_serializer(str, lambda x: x, lambda x: x, "txt")

    class SerializeAsTest:
        pass

    with pytest.raises(AssertionError, match="File extension must not include a dot"):
        register_serializer(SerializeAsTest, lambda x: x, lambda x: x, ".txt")

    with pytest.raises(AssertionError, match="Serializer function must take one argument"):
        register_serializer(SerializeAsTest, lambda x, y: x, lambda x: x, "txt")

    def serializer_no_return(_x):
        pass

    with pytest.raises(AssertionError, match="Serializer function must return a string or bytes"):
        register_serializer(SerializeAsTest, serializer_no_return, lambda x: x, "txt")

    def serializer_return_int(_x) -> int:
        return 1

    with pytest.raises(AssertionError, match="Serializer function must return a string or bytes"):
        register_serializer(SerializeAsTest, serializer_return_int, lambda x: x, "txt")

    def good_serializer(_x) -> str:
        pass

    with pytest.raises(AssertionError, match="Deserializer function must take one argument"):
        register_serializer(SerializeAsTest, good_serializer, lambda x, y: x, "txt")

    with pytest.raises(AssertionError, match="Deserializer function must take a string or bytes"):
        register_serializer(SerializeAsTest, good_serializer, lambda x: x, "txt")

    def deserializer_with_int(_x: int):
        pass

    with pytest.raises(AssertionError, match="Deserializer function must take a string or bytes"):
        register_serializer(SerializeAsTest, good_serializer, deserializer_with_int, "txt")

    def good_deserializer(_x: str):
        pass

    register_serializer(SerializeAsTest, good_serializer, good_deserializer, "txt")
    with pytest.raises(ValueError, match="Serializer for type .*SerializeAsTest.* already registered"):
        register_serializer(SerializeAsTest, good_serializer, good_deserializer, "txt")
