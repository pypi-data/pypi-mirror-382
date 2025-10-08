import json
import types

import pytest

import sws


def test_to_json():
    c = sws.Config()
    c.a = 1
    c.b = "str"
    c.c = {"x": 3}
    # Non-JSONable values: store a callable as a value using Fn wrapper
    c.fn = sws.Fn(lambda: None)
    c.s = {1, 2, 3}  # set

    data = json.loads(c.finalize().to_json())
    assert data["a"] == 1
    assert data["b"] == "str"
    assert data["c"] == {"x": 3}
    # Check placeholders
    assert data["fn"].startswith("<non-jsonable object of type ")
    assert data["s"].startswith("<non-jsonable object of type ")


def test_to_json_with_custom_default():
    c = sws.Config()
    c.x = {1, 2}
    c.f = sws.Fn(lambda: 0)

    def my_default(o):
        if isinstance(o, set):
            return sorted(list(o))
        if isinstance(o, types.FunctionType):
            return "<fn>"
        raise TypeError()

    data = json.loads(c.finalize().to_json(default=my_default))
    assert data["x"] == [1, 2]
    assert data["f"] == "<fn>"


def test_to_flat_json():
    c = sws.Config()
    c.a.b.c = 1
    c.b = "str"

    data = json.loads(c.finalize().to_flat_json())
    assert data["a.b.c"] == 1
    assert data["b"] == "str"


def test_from_json():
    js = '{"a": 1, "b": {"c": 2}}'
    fc = sws.from_json(js)

    assert isinstance(fc, sws.FinalConfig)
    assert fc.a == 1
    assert fc.b.c == 2
    assert fc.to_dict() == {"a": 1, "b": {"c": 2}}


def test_from_flat_json():
    js = '{"a": 1, "b.c": 2}'
    fc = sws.from_flat_json(js)

    assert isinstance(fc, sws.FinalConfig)
    assert fc.a == 1
    assert fc.b.c == 2


def test_json_round_trip():
    c = sws.Config()
    c.a = 123
    c.n = {"x": 7}
    # Non-JSONable values
    c.s = {1, 2}
    c.f = sws.Fn(lambda: None)

    fc = c.finalize()
    js = fc.to_json()
    fc2 = sws.from_json(js)
    fjs = fc.to_flat_json()
    ffc2 = sws.from_flat_json(fjs)

    assert fc2.a == ffc2.a == 123
    assert fc2.n.to_dict() == ffc2.n.to_dict() == {"x": 7}
