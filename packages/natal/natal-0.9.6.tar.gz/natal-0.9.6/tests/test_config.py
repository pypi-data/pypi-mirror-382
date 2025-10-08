from natal.config import Config, DotDict, Orb
from pytest import fixture


class Foo(DotDict):
    a: str


@fixture(scope="module")
def foo() -> Foo:
    return Foo(a="bar")


config = {
    "light_theme": {
        "fire": "#ff0000",
        "earth": "#ffff00",
        "air": "#00ff00",
        "water": "#0000ff",
        "points": "#00ffff",
    },
    "display": {
        "asc_node": False,
        "chiron": True,
    },
    "orb": {
        "conjunction": 8,
        "opposition": 7,
        "trine": 6,
        "square": 6,
        "sextile": 8,
    },
}


def test_load_config_from_dict() -> None:
    cfg = Config(**config)
    assert cfg.light_theme.fire == "#ff0000"
    assert cfg.display.asc_node is False
    assert cfg.orb.opposition == 7


def test_mono_theme() -> None:
    cfg = Config(theme_type="mono")
    assert cfg.theme_type == "mono"
    assert cfg.theme.foreground == cfg.theme.fire
    assert cfg.theme.background == "#FFFFFF"
    assert cfg.theme.transparency == 0


def test_dot_notation(foo):
    assert foo.a == "bar"


def test_subscription(foo):
    assert foo["a"] == "bar"


def test_update(foo):
    foo.update(a="baz")
    foo.update({"b": "qux"})
    assert foo.a == "baz"
    assert foo.b == "qux"


def test_unpacked_dict(foo):
    foo.update(**{"c": "qux"})
    assert foo.c == "qux"


def test_model_dict_iter():
    # iter of original pydantic model returns key value pairs, not keys
    orb_keys = [key for key in Orb()]
    assert orb_keys == ["conjunction", "opposition", "trine", "square", "sextile", "quincunx"]
