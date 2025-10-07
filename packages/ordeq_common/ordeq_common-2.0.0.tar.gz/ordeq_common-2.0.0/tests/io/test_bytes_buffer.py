from ordeq_common import BytesBuffer


def test_it_loads():
    buffer = BytesBuffer()
    buffer.save(b"x + ")
    assert buffer.load() == b"x + "
    buffer.save(b"y = 2")
    assert buffer.load() == b"x + y = 2"


def test_it_loads_with_initial_value():
    buffer = BytesBuffer(value=b"initial value")
    assert buffer.load() == b"initial value"
    buffer.save(b" + additional")
    assert buffer.load() == b"initial value + additional"


def test_it_is_unique():
    a, b = BytesBuffer(b""), BytesBuffer(b"")
    assert a is not b
    assert a != b
    assert hash(a) != hash(b)
