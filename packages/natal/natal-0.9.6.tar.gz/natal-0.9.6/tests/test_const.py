from natal.const import (
    PLANET_MEMBERS,
    ASPECT_MEMBERS,
    ELEMENT_MEMBERS,
    MODALITY_MEMBERS,
    POLARITY_MEMBERS,
    SIGN_MEMBERS,
    HOUSE_MEMBERS,
    EXTRA_MEMBERS,
    VERTEX_MEMBERS,
)


def test_const():
    assert len(PLANET_MEMBERS) == 11
    assert len(ASPECT_MEMBERS) == 6
    assert len(ELEMENT_MEMBERS) == 4
    assert len(MODALITY_MEMBERS) == 3
    assert len(POLARITY_MEMBERS) == 2
    assert len(SIGN_MEMBERS) == 12
    assert len(HOUSE_MEMBERS) == 12
    assert len(EXTRA_MEMBERS) == 5
    assert len(VERTEX_MEMBERS) == 4


def test_planet_member():
    pluto = PLANET_MEMBERS[9]
    assert pluto.name == "pluto"
    assert pluto["color"] == "water"
    assert pluto["symbol"] == "♇"


def test_sign_member():
    sign = SIGN_MEMBERS[3]
    assert sign.ruler == "moon"
    assert sign["element"] == "water"


def test_house_member():
    house = HOUSE_MEMBERS[3]
    assert house.name == "four"
    assert house.color == "water"


def test_extra_member():
    chiron = EXTRA_MEMBERS[0]
    assert chiron.name == "chiron"
    assert chiron["color"] == "asteroids"
    assert chiron["symbol"] == "⚷"
    ceres = EXTRA_MEMBERS[1]
    assert ceres.name == "ceres"
    assert ceres["color"] == "asteroids"
    assert ceres["symbol"] == "⚳"
