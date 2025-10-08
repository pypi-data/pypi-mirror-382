from natal.const import Body, SignMember, AspectMember, SIGN_MEMBERS, DotDict
from math import floor


class MovableBody(Body):
    """A celestial body that can move and have aspects.

    Attributes:
        degree (float): Position in degrees (0-360)
        speed (float): Movement speed (negative for retrograde)
        normalized_degree (float): Position relative to Ascendant
    """

    degree: float = 0
    speed: float = 0
    normalized_degree: float = 0

    @property
    def signed_deg(self) -> int:
        """Get degree within current sign.

        Returns:
            int: Degree position within sign (0-29)
        """
        return int(self.degree % 30)

    @property
    def minute(self) -> int:
        """Get arc minutes of position.

        Returns:
            int: Arc minutes of position (0-59)
        """
        minutes = (self.degree % 30 - self.signed_deg) * 60
        return floor(minutes)

    @property
    def retro(self) -> bool:
        """Retrograde status

        Returns:
            bool: True if retrograde, False otherwise.
        """
        return self.speed < 0

    @property
    def rx(self) -> str:
        """Retrograde symbol

        Returns:
            str: The retrograde symbol if retrograde, empty string otherwise.
        """
        return "℞" if self.retro else ""

    @property
    def sign(self) -> SignMember:
        """Return sign name, symbol, element, modality, and polarity

        Returns:
            SignMember: The sign member.
        """
        idx = int(self.degree // 30)
        return SIGN_MEMBERS[idx]

    @property
    def dms(self) -> str:
        """Degree Minute Second representation of the position

        Returns:
            str: The DMS representation.
        """
        op = [f"{self.signed_deg:02d}°", f"{self.minute:02d}'"]
        if self.rx:
            op.append(self.rx)
        return "".join(op)

    @property
    def signed_dms(self) -> str:
        """Degree Minute representation with sign

        Returns:
            str: The signed DMS representation.
        """
        op = [f"{self.signed_deg:02d}°", self.sign.symbol, f"{self.minute:02d}'"]
        if self.rx:
            op.append(self.rx)
        return " ".join(op)


class Planet(MovableBody):
    """Represents a planet"""

    ...


class Extra(MovableBody):
    """Represents an extra celestial body (e.g. Moon's Node and Asteroids)"""

    ...


class Vertex(MovableBody):
    """Represents a vertex (Asc, Dsc, MC, IC)"""

    ...


class Aspectable(MovableBody):
    """Represents a celestial body that can form aspects"""

    ...


class Sign(SignMember):
    """alias to SignMember"""

    ...


class House(MovableBody):
    """Represents a house"""

    ruler: str = None
    ruler_sign: str = None
    ruler_house: int = None
    classic_ruler: str = None
    classic_ruler_sign: str = None
    classic_ruler_house: int = None


class Aspect(DotDict):
    """An aspect between two celestial bodies.

    Attributes:
        body1 (Aspectable): First body in aspect
        body2 (Aspectable): Second body in aspect
        aspect_member (AspectMember): Type of aspect
        applying (bool | None): Whether aspect is applying
        orb (float | None): Orb in degrees from exact aspect
    """

    body1: Aspectable
    body2: Aspectable
    aspect_member: AspectMember
    applying: bool | None = None
    orb: float | None = None
