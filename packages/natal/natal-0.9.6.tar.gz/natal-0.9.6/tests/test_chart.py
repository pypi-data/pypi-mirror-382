from pytest import fixture
from natal.chart import Chart
from natal.data import Data
from tests import data1, data2
from math import floor
from natal.config import Display, Config, Orb


@fixture(scope="module")
def chart(data1, data2) -> Chart:
    return Chart(data1=data1, data2=data2, width=500)


@fixture
def house_vertices():
    return [
        (359, 389),
        (29, 59),
        (59, 90),
        (90, 121),
        (121, 151),
        (151, 179),
        (179, 209),
        (209, 239),
        (239, 270),
        (270, 301),
        (301, 331),
        (331, 359),
    ]


@fixture
def adj_outer_degs():
    return [0, 14, 22, 53, 89, 174, 188, 196, 207, 262, 270, 278, 349]


@fixture
def adj_inner_degs():
    return [3, 23, 32, 195, 226, 277, 286, 297, 306, 315, 329, 338, 353]


def test_house_vertices(chart, house_vertices):
    floor_vertices = [
        tuple(floor(v) for v in vertices) for vertices in chart.house_vertices
    ]
    assert house_vertices == floor_vertices


def test_adjusted_outer_degrees(chart, adj_outer_degs):
    input_degs = sorted(asp.normalized_degree for asp in chart.data1.aspectables)
    adj_degs = chart.adjusted_degrees(input_degs, chart.config.chart.outer_min_degree)
    floor_degs = [floor(d) for d in adj_degs]
    assert floor_degs == adj_outer_degs


def test_adjusted_inner_degrees(chart, adj_inner_degs):
    input_degs = sorted(asp.normalized_degree for asp in chart.data2.aspectables)
    adj_degs = chart.adjusted_degrees(input_degs, chart.config.chart.inner_min_degree)
    floor_degs = [floor(d) for d in adj_degs]
    assert floor_degs == adj_inner_degs


def test_fix_wrong_bodies_position():
    d1 = Data("d1", 22.2783, 114.175, "1988-04-20 06:30")
    d2 = Data("d2", 22.2783, 114.175, "2025-02-25 04:00")

    chart1 = Chart(data1=d1, data2=d2, width=600)
    input_degs = sorted(
        chart1.data1.normalize(asp.degree) for asp in chart1.data2.aspectables
    )
    org = [146, 150, 174, 184, 197, 197, 205, 206, 217, 260, 277, 279, 314]
    assert [int(d) for d in input_degs] == org
    adj_degs = chart1.adjusted_degrees(input_degs, chart1.config.chart.outer_min_degree)
    adj_degs_int = [int(d) for d in adj_degs]
    avg = [144, 152, 170, 178, 189, 197, 205, 213, 223, 260, 274, 282, 314]
    assert adj_degs_int == avg


def test_fix_crowded_bodies():
    crowded = Data("Crowded", 22.2783, 114.175, "2025-03-26 04:00")
    chart = Chart(data1=crowded, width=600)
    input_degs = sorted(asp.normalized_degree for asp in chart.data1.aspectables)
    org = [0, 14, 205, 223, 256, 259, 260, 262, 263, 265, 268, 317, 337]
    assert [int(d) for d in input_degs] == org
    avg = [0, 14, 204, 217, 237, 246, 254, 262, 270, 278, 286, 317, 337]
    adj_degs = chart.adjusted_degrees(input_degs, chart.config.chart.outer_min_degree)
    adj_degs_int = [int(d) for d in adj_degs]
    assert adj_degs_int == avg


def test_fix_infinite_loop():
    inf_loop = Data("Inf Loop", 22.2783, 114.175, "2000-01-12 04:00")
    chart = Chart(data1=inf_loop, width=600)
    input_degs = sorted(asp.normalized_degree for asp in chart.data1.aspectables)
    org = [0, 5, 20, 104, 231, 234, 264, 268, 271, 283, 295, 316, 332]
    assert [int(d) for d in input_degs] == org
    avg = [358, 7, 20, 104, 229, 237, 259, 267, 275, 286, 295, 316, 332]
    adj_degs = chart.adjusted_degrees(input_degs, chart.config.chart.outer_min_degree)
    adj_degs_int = [int(d) for d in adj_degs]
    assert adj_degs_int == avg


def test_adj_degs_len():
    info = ["test", 22.2783, 114.175, "2023-12-23 16:00"]
    bodies = Display.model_fields.keys()
    values = [False] * len(bodies)

    for i in range(3):
        values[:i] = [True] * i
        display = Display(**dict(zip(bodies, values)))
        d = Data(*info, config=Config(display=display))
        chart = Chart(data1=d, width=600)
        _ = chart.svg
        assert chart.adj_degs_len == i


def test_fix_orb_eq_0(data1: Data) -> None:
    org_chart = Chart(data1=data1, width=600)
    orb = Orb(conjunction=0, opposition=0)
    data = Data(data1.name, data1.lat, data1.lon, data1.utc_dt, config=Config(orb=orb))
    chart = Chart(data1=data, width=600)
    _ = org_chart.svg
    _ = chart.svg
    assert chart.aspect_lines_len == 14
    assert org_chart.aspect_lines_len == 24
