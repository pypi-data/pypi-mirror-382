import itertools
import swisseph as swe
from datetime import datetime
from math import floor
from natal.classes import Aspect, Aspectable, Body, Extra, House, Planet, Sign, Vertex
from natal.config import Config, DotDict
from natal.const import (
    ASPECT_MEMBERS,
    EXTRA_MEMBERS,
    HOUSE_MEMBERS,
    PLANET_MEMBERS,
    SIGN_MEMBERS,
    VERTEX_MEMBERS,
)
from natal.utils import pairs, str_to_dt
from pathlib import Path
from typing import Iterable, Self
from zoneinfo import ZoneInfo

type BodyPairs = Iterable[tuple[Aspectable, Aspectable]]


class Data(DotDict):
    """Data object for a natal chart."""

    data_folder = Path(__file__).parent.absolute()

    def __init__(
        self,
        name: str,
        lat: float,
        lon: float,
        utc_dt: datetime | str,
        config: Config = Config(),
        moshier: bool = False,
    ) -> None:
        """Initialize a natal chart data object.

        Args:
            name: The name for this chart
            lat: Latitude of the city
            lon: Longitude of the city
            utc_dt: datetime object or string in format "YYYY-MM-DD HH:MM" in UTC timezone
            config: Configuration settings with defaults
            moshier: Use Moshier ephemeris, no asteroids support, but more performant

        Returns:
            None
        """
        swe.set_ephe_path(None if moshier else str(Path(__file__).parent.absolute()))
        self.name = name
        self.lat = lat
        self.lon = lon
        self.utc_dt = str_to_dt(utc_dt) if isinstance(utc_dt, str) else utc_dt
        self.config = config
        self.moshier = moshier
        self.house_sys = config.house_sys
        self.houses: list[House] = []
        self.planets: list[Planet] = []
        self.extras: list[Extra] = []
        self.vertices: list[Vertex] = []
        self.signs: list[Sign] = []
        self.aspects: list[Aspect] = []
        self.quadrants: list[list[Aspectable]] = []
        self.set_houses_vertices()
        self.set_movable_bodies()
        self.set_aspectable()
        self.set_signs()
        self.set_normalized_degrees()
        self.set_aspects()
        self.set_rulers()
        self.set_quadrants()

    def set_movable_bodies(self) -> None:
        """Set the positions of the planets and other celestial bodies."""
        self.planets = self.set_positions(PLANET_MEMBERS)
        if not self.moshier:
            self.extras = self.set_positions(EXTRA_MEMBERS)

    def set_houses_vertices(self) -> None:
        """Calculate the cusps of the houses and set the vertices."""
        cusps, (asc_deg, mc_deg, *_) = swe.houses(
            self.julian_day,
            self.lat,
            self.lon,
            self.house_sys.encode(),
        )

        for house, cusp in zip(HOUSE_MEMBERS, cusps):
            house_body = House(
                **house,
                degree=floor(cusp * 100) / 100,
            )
            self.houses.append(house_body)

        self.vertices = [
            Vertex(degree=asc_deg, **VERTEX_MEMBERS[0]),
            Vertex(degree=(mc_deg + 180) % 360, **VERTEX_MEMBERS[1]),
            Vertex(degree=(asc_deg + 180) % 360, **VERTEX_MEMBERS[2]),
            Vertex(degree=mc_deg, **VERTEX_MEMBERS[3]),
        ]

        for v in self.vertices:
            setattr(self, v.name, v)

    def set_aspectable(self) -> None:
        """Set the aspectable celestial bodies based on the display configuration."""
        self.aspectables = [
            body
            for body in (self.planets + self.extras + self.vertices)
            if self.config.display[body.name]
        ]

    def set_signs(self) -> None:
        """Set the signs of the zodiac."""
        for i, sign_member in enumerate(SIGN_MEMBERS):
            sign = Sign(
                **sign_member,
                degree=i * 30,
            )
            self.signs.append(sign)

    def set_aspects(self) -> None:
        """Set the aspects between the aspectable celestial bodies."""
        body_pairs = pairs(self.aspectables)
        self.aspects = self.calculate_aspects(body_pairs)

    def set_normalized_degrees(self) -> None:
        """Normalize the positions of celestial bodies relative to the first house."""
        bodies = self.signs + self.planets + self.extras + self.vertices + self.houses
        for body in bodies:
            body.normalized_degree = self.normalize(body.degree)

    def set_rulers(self) -> None:
        """Set the rulers for each house."""
        for house in self.houses:
            ruler = getattr(self, house.sign.ruler)
            classic_ruler = getattr(self, house.sign.classic_ruler)
            house.ruler = ruler.name
            house.ruler_sign = f"{ruler.sign.symbol}"
            house.ruler_house = self.house_of(ruler)
            house.classic_ruler = classic_ruler.name
            house.classic_ruler_sign = (
                f"{classic_ruler.sign.symbol} {classic_ruler.sign.name}"
            )
            house.classic_ruler_house = self.house_of(classic_ruler)

    def set_quadrants(self) -> None:
        """Set the distribution of celestial bodies in quadrants."""
        bodies = [b for b in self.aspectables if b not in self.vertices]
        _, ic, dsc, mc = [v.normalized_degree for v in self.vertices]

        first = [b for b in bodies if b.normalized_degree < ic]
        second = [b for b in bodies if ic <= b.normalized_degree < dsc]
        third = [b for b in bodies if dsc <= b.normalized_degree < mc]
        fourth = [b for b in bodies if mc <= b.normalized_degree]
        self.quadrants = [first, second, third, fourth]

    # utils ===============================

    @property
    def julian_day(self) -> float:
        """Convert dt to UTC and return Julian day.

        Returns:
            float: The Julian day number
        """
        return swe.date_conversion(
            self.utc_dt.year,
            self.utc_dt.month,
            self.utc_dt.day,
            self.utc_dt.hour + self.utc_dt.minute / 60,
        )[1]

    def set_positions(self, bodies: list[Body]) -> list[Aspectable]:
        """Set the positions of celestial bodies.

        Args:
            bodies: List of celestial body definitions

        Returns:
            List of aspectable bodies with positions set
        """
        output = []
        for body in bodies:
            ((lon, _, _, speed, *_), _) = swe.calc_ut(self.julian_day, body.value)
            pos = Aspectable(
                **body,
                degree=lon,
                speed=speed,
            )
            setattr(self, body.name, pos)
            output.append(pos)
        return output

    def house_of(self, body: Body) -> int:
        """Get the house number containing a celestial body.

        Args:
            body: The celestial body to locate

        Returns:
            House number (1-12) containing the body
        """
        sorted_houses = sorted(self.houses, key=lambda x: x.degree, reverse=True)
        for house in sorted_houses:
            if body.degree >= house.degree:
                return house.value
        return sorted_houses[0].value

    def normalize(self, degree: float) -> float:
        """Normalize a degree relative to the Ascendant.

        Args:
            degree: The degree to normalize

        Returns:
            Normalized degree (0-360)
        """
        return (degree - self.asc.degree + 360) % 360

    def calculate_aspects(self, body_pairs: BodyPairs) -> list[Aspect]:
        """Calculate aspects between pairs of celestial bodies.

        Args:
            body_pairs: Pairs of bodies to check for aspects

        Returns:
            List of aspects found between the bodies
        """
        output = []
        for b1, b2 in body_pairs:
            sorted_bodies = sorted([b1, b2], key=lambda x: x.degree)
            org_angle = sorted_bodies[1].degree - sorted_bodies[0].degree
            # get the smaller angle
            angle = 360 - org_angle if org_angle > 180 else org_angle
            for aspect_member in ASPECT_MEMBERS:
                orb_val = self.config.orb[aspect_member.name]
                if not orb_val:
                    continue
                max_orb = aspect_member.value + orb_val
                min_orb = aspect_member.value - orb_val
                if min_orb <= angle <= max_orb:
                    applying = sorted_bodies[0].speed > sorted_bodies[1].speed
                    if angle < aspect_member.value:
                        applying = not applying
                    applying = not applying if org_angle > 180 else applying
                    output.append(
                        Aspect(
                            body1=b1,
                            body2=b2,
                            aspect_member=aspect_member,
                            applying=applying,
                            orb=abs(angle - aspect_member.value),
                        )
                    )
        return output

    def composite_aspects_pairs(self, data2: Self) -> BodyPairs:
        """Generate pairs of aspectable bodies for composite chart.

        Args:
            data2: Second chart data to compare against

        Returns:
            Pairs of bodies to check for aspects
        """
        return itertools.product(self.aspectables, data2.aspectables)
