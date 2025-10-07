from ordeq_common import Print


def test_it_saves(capsys):
    Print().save("Hello, world!")
    captured = capsys.readouterr()
    assert "Hello, world!" in captured.out
