"""
This module provides statistical analysis for natal charts.

It contains the Stats class, which calculates and presents various astrological statistics
for a single natal chart or a comparison between two charts.
"""

from collections import defaultdict
from math import floor
from natal.classes import Aspect, Aspectable
from natal.data import Data
from tabulate import tabulate
from tagit import div, h4
from typing import Iterable, Literal, NamedTuple

DistKind = Literal["element", "modality", "polarity"]
ReportKind = Literal["markdown", "html"]
Grid = list[Iterable[str | int]]


class StatData(NamedTuple):
    """
    A named tuple representing statistical data with a title and grid.

    Attributes:
        title (str): The title of the statistical data.
        grid (Grid): A grid containing the statistical information.
    """

    title: str
    grid: Grid


class Stats:
    """
    Statistics for a natal chart data.

    This class calculates and presents various astrological statistics for a single natal chart
    or a comparison between two charts.

    Attributes:
        data1 (Data): The primary natal chart data.
        data2 (Data | None): The secondary natal chart data for comparisons (optional).
    """

    data1: Data
    data2: Data | None = None

    def __init__(self, data1: Data, data2: Data | None = None) -> None:
        """
        Initialize the Stats object with one or two natal chart data sets.

        Args:
            data1 (Data): The primary natal chart data.
            data2 (Data, optional): The secondary natal chart data for comparisons. Defaults to None.
        """
        self.data1 = data1
        self.data2 = data2
        if self.data2:
            self.composite_pairs = data2.composite_aspects_pairs(self.data1)
            self.composite_aspects = data1.calculate_aspects(self.composite_pairs)

    # data grids =================================================================

    @property
    def basic_info(self) -> StatData:
        """
        Generate basic information about the provided data.

        Returns:
            The title and grid of basic information data, where the grid includes name, location coordinates, and UTC time.
        """
        title = "Basic Information"
        time_fmt = "%Y-%m-%d %H:%M"
        dt1 = self.data1.utc_dt.strftime(time_fmt)
        coordinates1 = f"{self.data1.lat}°N, {self.data1.lon}°E"
        grid = [("name", "location", "UTC time")]
        grid.append((self.data1.name, coordinates1, dt1))
        if self.data2:
            dt2 = self.data2.utc_dt.strftime(time_fmt)
            coordinates2 = f"{self.data2.lat}°N, {self.data2.lon}°E"
            grid.append((self.data2.name, coordinates2, dt2))
        return StatData(title, grid)

    def distribution(self, kind: DistKind) -> StatData:
        """
        Generate distribution statistics for elements, modalities, or polarities.

        Args:
            kind: The type of distribution to calculate. Must be one of "element", "modality", or "polarity".

        Returns:
            The title and grid of distribution data, where the grid includes the distribution type,
            count, and bodies.
        """
        title = f"{kind.capitalize()} Distribution ({self.data1.name})"
        bodies = defaultdict(lambda: [0, []])
        for body in self.data1.aspectables:
            key = body.sign[kind]
            bodies[key][0] += 1  # act as a counter
            bodies[key][1].append(f"{body.name} {body.sign.symbol} ")
        grid = [(kind, "sum", "bodies")]
        data = [(key, val[0], ", ".join(val[1])) for key, val in bodies.items()]
        grid.extend(data)
        return StatData(title, grid)

    @property
    def celestial_body(self) -> StatData:
        """
        Generate a grid of celestial body positions for the primary chart.

        Returns:
            StatData: A named tuple containing the title and grid of celestial body data,
                      where the grid includes body name, sign, house, and dignity.
        """
        title = f"Celestial Bodies ({self.data1.name})"
        grid = [("body", "sign", "house", "dignity")]
        for body in self.data1.aspectables:
            grid.append(
                (
                    body.name,
                    body.signed_dms,
                    self.data1.house_of(body),
                    dignity_of(body),
                )
            )
        return StatData(title, grid)

    @property
    def data2_celestial_body(self) -> StatData:
        """
        Generate a grid of celestial body positions for the secondary chart.

        Returns:
            StatData: A named tuple containing the title and grid of celestial body data
                      for the secondary chart, showing its bodies in the primary chart's context.
                      The grid includes body name, sign, house, and dignity.

        Raises:
            AttributeError: If no secondary chart (data2) is available.
        """
        if not self.data2:
            raise AttributeError("No secondary chart available")

        title = f"Celestial Bodies of {self.data2.name} in {self.data1.name}'s chart"
        grid = [(self.data2.name, "sign", "house", "dignity")]
        for body in self.data2.aspectables:
            grid.append(
                (
                    body.name,
                    body.signed_dms,
                    self.data1.house_of(body),
                    dignity_of(body),
                )
            )
        return StatData(title, grid)

    @property
    def house(self) -> StatData:
        """
        Generate a grid of house data for the primary chart.

        Returns:
            StatData: A named tuple containing the title and grid of house data,
                      where the grid includes house number, cusp, ruler, ruler sign, and ruler house.
        """
        title = f"Houses ({self.data1.name})"
        grid = [("house", "cusp", "ruler", "ruler sign", "ruler house")]
        for house in self.data1.houses:
            grid.append(
                (
                    house.value,
                    house.signed_dms,
                    house.ruler,
                    house.ruler_sign,
                    house.ruler_house,
                )
            )
        return StatData(title, grid)

    @property
    def quadrant(self) -> StatData:
        """
        Generate a grid of celestial body distribution in quadrants.

        Returns:
            StatData: A named tuple containing the title and grid of quadrant distribution data,
                      where the grid includes quadrant name, body count, and body names.
        """
        title = f"Quadrants ({self.data1.name})"
        quad_names = ["1st", "2nd", "3rd", "4th"]
        quadrants = defaultdict(lambda: [0, []])
        for i, quad in enumerate(self.data1.quadrants):
            if quad:
                for body in quad:
                    quadrants[i][0] += 1  # act as a counter
                    quadrants[i][1].append(f"{body.name}")
            else:
                # no celestial body in this quadrant
                quadrants[i][0] = 0
        grid = [("quadrant", "sum", "bodies")]
        data = [
            (quad_names[quad_no], val[0], ", ".join(val[1])) for quad_no, val in quadrants.items()
        ]
        return StatData(title, grid + data)

    @property
    def hemisphere(self) -> StatData:
        """
        Generate a grid of celestial body distribution in hemispheres.

        Returns:
            StatData: A named tuple containing the title and grid of hemisphere distribution data,
                      where the grid includes hemisphere direction, body count, and body names.
        """
        title = f"Hemispheres ({self.data1.name})"
        grid = [("hemisphere", "sum", "bodies")]
        data = self.quadrant.grid[1:]

        def formatter(a: int, b: int) -> str:
            return (data[a][2] + ", " + data[b][2]).strip(" ,")

        left = ("Eastern", data[0][1] + data[3][1], formatter(0, 3))
        right = ("Western", data[1][1] + data[2][1], formatter(1, 2))
        top = ("Northern", data[2][1] + data[3][1], formatter(2, 3))
        bottom = ("Southern", data[0][1] + data[1][1], formatter(0, 1))
        return StatData(title, grid + [left, right, top, bottom])

    @property
    def aspect(self) -> StatData:
        """
        Generate a grid of aspects for the primary chart.

        Returns:
            StatData: A named tuple containing the title and grid of aspect data,
                      where the grid includes body 1, aspect type, body 2, phase, and orb.
        """
        title = f"Aspects ({self.data1.name})"
        headers = ["body 1", "aspect", "body 2", "phase", "orb"]
        return StatData(title, _aspect_grid(self.data1.aspects, headers))

    @property
    def composite_aspect(self) -> StatData:
        """
        Generate a grid of composite aspects between two charts.

        Returns:
            StatData: A named tuple containing the title and grid of composite aspect data,
                      where the grid includes body names from both charts, aspect type, phase, and orb.

        Raises:
            AttributeError: If no secondary chart (data2) is available.
        """
        if not self.data2:
            raise AttributeError("No secondary chart available for composite aspects")

        title = f"Aspects of {self.data2.name} vs {self.data1.name}"
        headers = [self.data2.name, "aspect", self.data1.name, "phase", "orb"]
        return StatData(title, _aspect_grid(self.composite_aspects, headers))

    @property
    def cross_ref(self) -> StatData:
        """
        Generate a grid for aspect cross-reference between charts or within a single chart.

        Returns:
            StatData: A named tuple containing the title and grid of aspect cross-reference data,
                      where the grid shows aspect connections between bodies, with a sum column.
        """
        name = (
            f"{self.data2.name}(cols) vs {self.data1.name}(rows)" if self.data2 else self.data1.name
        )
        title = f"Aspect Cross Reference of {name}"
        aspectable1 = self.data1.aspectables
        aspectable2 = self.data2.aspectables if self.data2 else self.data1.aspectables
        aspects = self.composite_aspects if self.data2 else self.data1.aspects
        body_symbols = [body.symbol for body in aspectable2]
        grid: list[list[str]] = [[""] + body_symbols + ["sum"]]
        for body1 in aspectable1:
            row = [body1.symbol]
            aspect_count = 0
            for body2 in aspectable2:
                aspect = next(
                    (
                        asp
                        for asp in aspects
                        if (asp.body1 == body1 and asp.body2 == body2)
                        or (asp.body1 == body2 and asp.body2 == body1)
                    ),
                    None,
                )
                if aspect:
                    row.append(aspect.aspect_member.symbol)
                    aspect_count += 1
                else:
                    row.append("")

            row.append(str(aspect_count))  # Add sum to the end of the row
            grid.append(row)
        return StatData(title, grid)

    def full_report(self, kind: ReportKind) -> str:
        """
        Generate a full report containing all statistical tables.

        Args:
            kind (ReportKind): The format of the report, either "markdown" or "html".

        Returns:
            str: A formatted string containing the full statistical report with various tables.
        """
        output = "\n"
        output += self.table_of("basic_info", kind)
        for dist in DistKind.__args__:
            output += self.table_of("distribution", kind, dist)
        output += self.table_of("celestial_body", kind)
        output += self.table_of("house", kind, colalign=("left", "center", "left", "center"))
        output += self.table_of("quadrant", kind)
        output += self.table_of("hemisphere", kind)
        if self.data2:
            output += self.table_of("data2_celestial_body", kind)
            output += self.table_of(
                "composite_aspect", kind, colalign=("left", "center", "left", "center")
            )
        else:
            output += self.table_of("aspect", kind)
        output += self.table_of("cross_ref", kind, stralign="center")
        return output

    def table_of(
        self,
        fn_name: str,
        kind: ReportKind,
        *fn_args: object,
        **markdown_options: object,
    ) -> str:
        """
        Format a table with a title.

        Args:
            fn_name (str): The name of the method to call (e.g., "distribution", "celestial_body").
            kind (ReportKind): The kind of report to generate ("markdown" or "html").
            *fn_args: Variable positional arguments passed to the method.
            **markdown_options: Additional keyword arguments for tabulate formatting.

        Returns:
            str: A formatted string containing the titled table in the specified format.
        """
        stat = getattr(self, fn_name)
        if fn_args:
            # stat is property when no args, no need to call it
            stat = stat(*fn_args)
        base_option = dict(headers="firstrow", numalign="center")

        if kind == "markdown":
            options = base_option | {"tablefmt": "github"} | markdown_options
            output = f"# {stat.title}\n\n"
            output += tabulate(stat.grid, **options)
            output += "\n\n\n"
            return output
        elif kind == "html":
            options = base_option | {"tablefmt": "html"}
            tb = tabulate(stat.grid, **options)
            output = div([h4(stat.title), tb], class_=f"tabulate {fn_name}")
            return str(output)

    def ai_md(
        self,
        fn_name: str,
        cols: int,  # number of columns used in data table
    ) -> str:
        """markdown data for AI context"""
        stat = getattr(self, fn_name)
        rows = stat.grid
        output = f"# {stat.title}\n\n"
        header = rows.pop(0)
        output += "|"
        for item in header[:cols]:
            output += f"{item} | "
        output += "\n"
        output += "|" + "--- | " * cols
        output += "\n"
        for row in rows:
            output += "|"
            for item in row[:cols]:
                output += f"{item} | "
            output += "\n"
        output += "\n\n"
        return output


# utils ======================================================================


def _aspect_grid(aspects: list[Aspect], headers: list[str]) -> Grid:
    """
    Generate a grid of aspect data.

    Args:
        aspects (list[Aspect]): A list of Aspect objects to be converted to a grid.
        headers (list[str]): The headers for the aspect grid.

    Returns:
        Grid: A grid containing aspect data, with each row representing an aspect
              and columns including body names, aspect symbol, phase, and orb.
    """
    grid = [headers]
    for aspect in aspects:
        degree = floor(aspect.orb)
        minutes = round((aspect.orb - degree) * 60)
        grid.append(
            (
                aspect.body1.name,
                aspect.aspect_member.symbol,
                aspect.body2.name,
                "→ ←" if aspect.applying else "← →",
                f"{degree}° {minutes:02d}'",
            )
        )
    return grid


def dignity_of(body: Aspectable) -> str:
    """
    Get the dignity of a celestial body.

    Args:
        body (Aspectable): The celestial body to check for dignity.

    Returns:
        str: The dignity of the celestial body.
             Possible values are "domicile", "detriment", "exaltation", "fall", or an empty string.
    """
    if body.name == (body.sign.classic_ruler or body.sign.ruler):
        return "domicile"
    if body.name == (body.sign.classic_detriment or body.sign.detriment):
        return "detriment"
    if body.name == body.sign.exaltation:
        return "exaltation"
    if body.name == body.sign.fall:
        return "fall"
    return ""
