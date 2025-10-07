from ordeq_common import StringBuffer


def test_it_loads():
    buffer = StringBuffer()
    assert not buffer.load()
    buffer.save("x + ")
    assert buffer.load() == "x + "
    buffer.save("y = 2")
    assert buffer.load() == "x + y = 2"


def test_it_loads_with_initial_value():
    buffer = StringBuffer(value="initial value")
    assert buffer.load() == "initial value"
    buffer.save(" + additional")
    assert buffer.load() == "initial value + additional"


def test_it_is_unique():
    a, b = StringBuffer(""), StringBuffer("")
    assert a is not b
    assert a != b
    assert hash(a) != hash(b)
