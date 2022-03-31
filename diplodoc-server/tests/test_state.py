from pytest import raises

from diplodoc.state import TextState


def test_push_empty() -> None:
    state = TextState()
    assert str(state) == ""
    state.push(0, "d")
    assert str(state) == "d"


def test_push_empty_out_of_range() -> None:
    state = TextState()
    assert str(state) == ""
    with raises(ValueError):
        state.push(2, "d")


def test_push_empty_raises() -> None:
    state = TextState()
    assert str(state) == ""
    with raises(ValueError):
        state.push(0, "")


def test_push_many_raises() -> None:
    state = TextState("diplodoc")
    assert str(state) == "diplodoc"
    with raises(ValueError):
        state.push(0, "")


def test_push_many_out_of_range() -> None:
    state = TextState("diplodoc")
    assert str(state) == "diplodoc"
    with raises(ValueError):
        state.push(420, "x")


def test_push_many() -> None:
    state = TextState()
    assert str(state) == ""
    state.push(0, "l")
    assert str(state) == "l"
    state.push(0, "p")
    assert str(state) == "pl"
    state.push(2, "o")
    assert str(state) == "plo"
    state.push(0, "di")
    assert str(state) == "diplo"
    state.push(5, "doc")
    assert str(state) == "diplodoc"


def test_pop_empty() -> None:
    state = TextState()
    with raises(ValueError):
        state.pop(0)


def test_pop_many1() -> None:
    state = TextState()
    state.push(0, "d")
    with raises(ValueError):
        state.pop(1)
    state.pop(0)
    assert str(state) == ""


def test_pop_out_of_range() -> None:
    state = TextState()
    state.push(0, "diplodoc")
    with raises(ValueError):
        state.pop(420)
