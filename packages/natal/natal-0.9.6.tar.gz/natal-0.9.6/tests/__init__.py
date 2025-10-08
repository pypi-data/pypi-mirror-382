from pytest import fixture
from natal.data import Data

person1 = {
    "name": "shing",
    "lat": 22.2783,
    "lon": 114.175,
    "utc_dt": "1976-04-20 09:58",
}

person2 = {
    "name": "belle",
    "lat": 22.2783,
    "lon": 114.175,
    "utc_dt": "2011-01-23 00:44",
}


@fixture(scope="package")
def data1():
    return Data(**person1)


@fixture(scope="package")
def data2():
    return Data(**person2)
