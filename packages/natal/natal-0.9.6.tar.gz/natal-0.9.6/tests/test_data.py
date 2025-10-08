from natal.data import Data
from natal.config import Orb, Config
from datetime import datetime
from pytest import fixture
from . import data1, data2


@fixture(scope="module")
def planets() -> dict[str, str]:
    return dict(
        sun="00° ♉ 26'",
        moon="19° ♑ 47'",
        mercury="18° ♉ 30'",
        venus="14° ♈ 49'",
        mars="15° ♋ 54'",
        jupiter="05° ♉ 52'",
        saturn="26° ♋ 31'",
        uranus="05° ♏ 19' ℞",
        neptune="13° ♐ 38' ℞",
        pluto="09° ♎ 47' ℞",
        asc_node="13° ♏ 25' ℞",
    )


@fixture(scope="module")
def houses() -> dict[str, str]:
    return dict(
        one="20° ♎ 32'",
        two="19° ♏ 43'",
        three="19° ♐ 49'",
        four="20° ♑ 36'",
        five="21° ♒ 53'",
        six="22° ♓ 29'",
        seven="20° ♈ 32'",
        eight="19° ♉ 43'",
        nine="19° ♊ 49'",
        ten="20° ♋ 36'",
        eleven="21° ♌ 54'",
        twelve="22° ♍ 29'",
    )


@fixture(scope="module")
def others() -> dict[str, str]:
    return dict(
        chiron="27° ♈ 49'",
        asc_node="13° ♏ 25' ℞",
        asc="20° ♎ 32'",
        mc="20° ♋ 36'",
        house_sys="P",
    )


@fixture(scope="module")
def signs() -> dict:
    return dict(
        aries=(0, "mars", "fire", "cardinal", "fire", "positive"),
        taurus=(30, "venus", "earth", "fixed", "earth", "negative"),
        gemini=(60, "mercury", "air", "mutable", "air", "positive"),
        cancer=(90, "moon", "water", "cardinal", "water", "negative"),
        leo=(120, "sun", "fire", "fixed", "fire", "positive"),
        virgo=(150, "mercury", "earth", "mutable", "earth", "negative"),
        libra=(180, "venus", "air", "cardinal", "air", "positive"),
        scorpio=(210, "pluto", "water", "fixed", "water", "negative"),
        sagittarius=(240, "jupiter", "fire", "mutable", "fire", "positive"),
        capricorn=(270, "saturn", "earth", "cardinal", "earth", "negative"),
        aquarius=(300, "uranus", "air", "fixed", "air", "positive"),
        pisces=(330, "neptune", "water", "mutable", "water", "negative"),
    )


@fixture(scope="module")
def aspects_pairs(data1: Data, data2: Data):
    return list(data1.composite_aspects_pairs(data2))


@fixture(scope="module")
def aspects_pair_names_sample():
    return [
        "sun sun",
        "moon uranus",
        "venus moon",
        "mars neptune",
        "saturn mercury",
        "uranus pluto",
        "pluto venus",
        "asc_node asc_node",
        "mc mars",
    ]


def test_lat_lon(data1: Data) -> None:
    assert round(data1.lat, 2) == 22.28
    assert round(data1.lon, 2) == 114.17


def test_data_input(data1: Data) -> None:
    assert data1.name == "shing"
    assert data1.lat == 22.2783
    assert data1.lon == 114.175
    assert data1.utc_dt == datetime(1976, 4, 20, 9, 58, 0)


def test_planet(data1: Data, planets: dict[str, str]) -> None:
    for planet in data1.planets:
        assert planet.name in planets
        assert planet.signed_dms == planets[planet.name]


def test_houses(data1: Data, houses: dict[str, str]) -> None:
    for house in data1.houses:
        assert house.name in houses
        assert house.signed_dms == houses[house.name]


def test_asc_mc(data1: Data, others: dict[str, str]) -> None:
    assert data1.asc.signed_dms == others["asc"]
    assert data1.mc.signed_dms == others["mc"]
    assert data1.chiron.signed_dms == others["chiron"]
    assert data1.asc_node.signed_dms == others["asc_node"]
    assert data1.house_sys == others["house_sys"]


def test_signs(data1: Data, signs: dict) -> None:
    for sign in data1.signs:
        assert sign.name in signs
        assert round(sign.degree, 2) == signs[sign.name][0]
        assert sign.ruler == signs[sign.name][1]
        assert sign.color == signs[sign.name][2]
        assert sign.modality == signs[sign.name][3]
        assert sign.element == signs[sign.name][4]
        assert sign.polarity == signs[sign.name][5]


def test_normalized_bodies(data1: Data) -> None:
    for body in data1.aspectables:
        assert body.normalized_degree == data1.normalize(body.degree)


def test_composite_aspects_pairs(aspects_pairs, aspects_pair_names_sample):
    assert len(aspects_pairs) == 169
    name_pairs = [f"{a.name} {b.name}" for a, b in aspects_pairs]
    assert name_pairs[::20] == aspects_pair_names_sample


def test_normalize(data1: Data) -> None:
    # create a new Data object
    data = Data(data1.name, data1.lat, data1.lon, data1.utc_dt)
    data.asc.degree = 0
    assert data.normalize(10) == 10
    assert data.normalize(350) == 350
    data.asc.degree = 10
    assert data.normalize(10) == 0
    assert data.normalize(350) == 340
    assert data.normalize(30) == 20


def test_fix_orb_eq_0(data1: Data) -> None:
    orb = Orb(conjunction=0, opposition=0)
    data = Data(data1.name, data1.lat, data1.lon, data1.utc_dt, config=Config(orb=orb))
    assert len(data1.aspects) == 24
    assert len(data.aspects) == 14


def test_house_sys(data1: Data) -> None:
    data = Data(
        data1.name, data1.lat, data1.lon, data1.utc_dt, config=Config(house_sys="W")
    )
    assert data.house_sys == "W"
    assert data.house_of(data.sun) == 8


def test_moshier(data1: Data) -> None:
    data = Data(data1.name, data1.lat, data1.lon, data1.utc_dt, moshier=True)
    assert data.moshier
    assert data.extras == []
