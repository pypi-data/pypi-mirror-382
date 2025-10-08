import pytest
import sws
from sws import Config


def test_simple():
    c = Config(lr=0.1)
    c.wd = lambda: c.lr * 0.5
    f = c.finalize()
    assert f.wd == pytest.approx(0.05)

    f2 = c.finalize(["c.lr=10"])  # override lr
    assert f2.lr == 10
    assert f2.wd == 5

    f3 = c.finalize(["c.lr=10", "c.wd=0.2"])  # explicit wd suppresses computed
    assert f3.lr == 10
    assert f3.wd == pytest.approx(0.2)


def test_suffix():
    c = Config()
    c.simple = 33
    c.thingy.lr = 0.1
    c.model.head.lr = 10
    c.model.head.params.voc = 15

    assert c.finalize(["c.simple=99"]).simple == 99
    assert c.finalize(["simple=99"]).simple == 99
    assert c.finalize(["voc=99"]).model.head.params.voc == 99

    with pytest.raises(AttributeError) as e:
        c.finalize(["ple=99"])
    msg = str(e.value)
    assert "ple" in msg
    assert "simple" in msg

    with pytest.raises(AttributeError) as e:
        c.finalize(["lrr=10"])
    msg = str(e.value)
    assert "model.head.lr" in msg
    assert "thingy.lr" in msg

    f = c.finalize(["head.lr=99"])
    assert f.thingy.lr == 0.1
    assert f.model.head.lr == 99

    with pytest.raises(AttributeError) as e:
        c.finalize(["lr=10"])
    msg = str(e.value)
    assert "model.head.lr" in msg
    assert "thingy.lr" in msg


def test_computed_nested_and_root():
    c = Config()
    c.model = {"lr": 1e-3, "wd": lambda: c.model.lr * 0.5}
    c.optim = {"wd": lambda: c.model.lr * 0.1}
    f = c.finalize()
    assert f.model.wd == pytest.approx(5e-4)
    assert f.optim.wd == pytest.approx(1e-4)


def test_computed_containers_and_freeze():
    c = Config(lr=3)
    c.aug = lambda: [1, c.lr * 2]
    f = c.finalize()
    assert f.aug == [1, 6]
    with pytest.raises(TypeError):
        f["new"] = 1
    with pytest.raises(TypeError):
        del f["lr"]
    # Subview is also frozen
    fm = sws.FinalConfig(f.to_flat_dict())
    with pytest.raises(TypeError):
        fm["lr"] = 1


def test_cycle_detection():
    c = Config()
    c.a = lambda: c.b
    c.b = lambda: c.a
    with pytest.raises(sws.CycleError):
        c.finalize()

    c = Config()
    c.a = lambda: c.b
    c.b = lambda: c.c
    c.c = lambda: c.a
    with pytest.raises(sws.CycleError):
        c.finalize()

    c = Config()
    c.foo.a = lambda: c.bar.b
    c.bar.b = lambda: c.baz.c
    c.baz.c = lambda: c.foo.a
    with pytest.raises(sws.CycleError):
        c.finalize()


# --- Override parsing and behavior tests ---

def test_overrides_notypes():
    c = Config(
        an_int=1,
        a_string="hi",
        a_float=0.3,
    )
    f1 = c.finalize(["an_int='hello shapeshifter'"])
    assert f1.an_int == "hello shapeshifter"


def test_overrides_nested():
    c = Config(lr=0.1, model=dict(width=128, depth=4))
    f1 = c.finalize(["lr=0.001", "model.width=64", "model.depth=8"])
    assert f1.lr == 0.001
    assert f1.model.width == 64
    assert f1.model.depth == 8


def test_overrides_inexistent():
    c = Config(lr=0.1, model=dict(width=128, depth=4))
    with pytest.raises(AttributeError):
        c.finalize(["lol=0.001"])
    with pytest.raises(AttributeError):
        c.finalize(["model.expand=2"])


def test_overrides_suggestion():
    c = Config(lr=0.1, model=dict(width=128, depth=4))
    with pytest.raises(AttributeError) as e:
        c.finalize(["model.widht=64"])
    assert "model.width" in str(e.value)


def test_overrides_expressions():
    c = Config(
        an_int=1,
        a_string="hi",
        a_float=0.3,
    )
    f1 = c.finalize(["an_int=3 * 2", "a_string=','.join('abc')"])
    assert f1.an_int == 6
    assert f1.a_string == "a,b,c"


def test_overrides_unquoted_string():
    c = Config(name="hello", nested=dict(label="x"))
    f = c.finalize(["name=bar", "nested.label=qux"])  # unquoted strings
    assert f.name == "bar"
    assert f.nested.label == "qux"


def test_overrides_expressions_with_c_view():
    base = Config(lr=1.0, model={"width": 128}, foo=0, bar=0)
    # Reference current config state via c
    f1 = base.finalize(["foo=c.lr", "bar=c.model.width"])
    assert f1.foo == 1.0 and f1.bar == 128
    # Expressions referencing c are evaluated against the finalized values
    f2 = base.finalize(["foo=c.lr", "lr=3", "bar=c.lr"])
    assert f2.foo == 3 and f2.bar == 3


def test_create_or_set_with_walrus_top_level_and_nested():
    c = Config(lr=0.1)
    # Create new top-level key
    f1 = c.finalize(["foobar:=32"])
    assert f1.foobar == 32 and f1.lr == 0.1

    # Create nested key path
    f2 = c.finalize(["notes.expid:=\"t42\""])
    assert f2.notes.expid == "t42"

    # Override existing with := behaves like =
    f3 = c.finalize(["lr:=0.2"])
    assert f3.lr == 0.2

    # No suffix matching for :=, creates exact key 'width' even if model.width exists
    c2 = Config(model=dict(width=128))
    f4 = c2.finalize(["width:=64"])  # exact new top-level key
    assert f4.model.width == 128 and f4.width == 64

    # Shadowing conflict: cannot set leaf where group exists
    import pytest
    with pytest.raises(ValueError):
        c2.finalize(["model:=0"])  # group exists under 'model', cannot assign leaf


def test_override_prefers_exact_key_when_using_c_prefix():
    c = Config()
    c.foo = 1
    c.bar.baz.foo = 2
    with pytest.raises(AttributeError):
        c.finalize(["foo=32"])

    f = c.finalize(["c.foo=32"])
    assert f.foo == 32
    assert f.bar.baz.foo == 2


def test_override_c_reference_tracks_late_assignments():
    c = Config(lr=0.1, ratio=0.0)
    f = c.finalize(["ratio=c.lr", "lr=0.2"])
    assert f.lr == pytest.approx(0.2)
    assert f.ratio == pytest.approx(0.2)


def test_order_independent_new_keys_with_c_reference():
    c = Config()
    f = c.finalize(["name:=f'hi-{c.xid}-{c.wid}'", "xid:=32", "wid:=11"])
    assert f.name == "hi-32-11"
    assert f.xid == 32 and f.wid == 11


def test_override_c_reference_missing_key_keeps_string():
    c = Config()
    f = c.finalize(["name:=f'hi-{c.xid}'"])
    assert f.name == "f'hi-{c.xid}'"
