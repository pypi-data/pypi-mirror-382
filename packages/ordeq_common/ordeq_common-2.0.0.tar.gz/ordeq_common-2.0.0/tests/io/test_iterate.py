from dataclasses import dataclass
from pathlib import Path

from ordeq import IO
from ordeq_common import Iterate


@dataclass(frozen=True, kw_only=True)
class Text(IO[str]):
    path: Path

    def load(self) -> str:
        return self.path.read_text()

    def save(self, data: str) -> None:
        self.path.write_text(data)


def test_wraps():
    t1 = Text(path=Path("hello.txt"))
    t2 = Text(path=Path("world.txt"))
    example = Iterate(t1, t2)
    assert example.references == {"ios": [t1, t2]}


def test_lazy(tmp_path: Path):
    paths = [tmp_path / "hello.txt", tmp_path / "world.txt"]
    for path in paths:
        path.write_text(path.stem)

    ds = Iterate(*[Text(path=path) for path in paths])

    # test loading
    assert list(ds.load()) == ["hello", "world"]

    # test that generator is properly used
    gen = ds.load()
    first = next(gen)
    assert first == "hello"
    paths[1].write_text("foo bar")
    second = next(gen)
    assert second == "foo bar"

    # test that list is accepted
    ds.save(["foo", "bar"])
    assert paths[0].read_text() == "foo"
    assert paths[1].read_text() == "bar"

    # test that generator node is accepted
    def generator():
        for i in range(2):
            yield f"{i**2}"

    ds.save(generator())
    assert paths[0].read_text() == "0"
    assert paths[1].read_text() == "1"
