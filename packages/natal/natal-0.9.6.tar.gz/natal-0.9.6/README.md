# Natal

> create Natal Chart with ease

## Features

- SVG natal chart generation in pure python
- composite chart (transit/synastry/sun return ... etc) generation
- highly configurable
    - all planets, asteroids, vertices can be enabled / disabled
    - orbs for each aspect
    - light, dark, or mono theme
    - light / dark theme color definitions
    - chart stroke, opacity, font, spacing between planets ...etc
- high precision astrological data with [Swiss Ephemeris]
- natal chart data statistics
    - element, modality, and polarity counts
    - planets in each houses
    - quadrant and hemisphere distribution
    - aspect pair counts
    - composite chart aspects
    - aspects cross reference table
    - generate report in markdown or html
- thoroughly tested with `pytest`

## Sample Charts

- default dark theme

<img src="https://bit.ly/4eufbuW" width=600/>

- default light theme

<img src="https://bit.ly/3MT86Zl" width=600/>

- mono theme

<img src="https://bit.ly/3ZygoNw" width=600/>

## Quick Start

- installation

`uv add natal`

- generate a chart

```python
from natal import Data, Chart

# create chart data object
mimi = Data(
    name="MiMi",
    utc_dt="1980-04-20 06:30",
    lat=25.0531,
    lon=121.526,
)

# return natal chart in SVG string
Chart(mimi, width=600).svg

# create transit data object
transit = Data(
    name="Transit",
    utc_dt="2024-01-01 05:30",
    lat=25.0531,
    lon=121.526,
)

# create a transit chart
transit_chart = Chart(
    data1=mimi, 
    data2=transit, 
    width=600
)

# view the composite chart in jupyter notebook
from IPython.display import HTML

HTML(transit_chart.svg)
```

following SVG chart will be produced:

<img src="https://bit.ly/3MX7H8e" width=600/>

## Data Object

```python
## -- retrieve natal chart properties -- ##

mimi.planets     # list[Planet]
mimi.houses      # list[House]
mimi.extras      # list[Extra]
mimi.vertices    # list[Vertex]
mimi.signs       # list[Sign]
mimi.aspects     # list[Aspect]
mimi.quadrants   # list[list[Aspectable]]

# Planet object 
sun = mimi.planets[0]

sun.degree # 30.33039116987769
sun.normalized_degree # 230.62043431588035 # degree relative to Asc
sun.color # fire
sun.speed # 0.9761994105153413
sun.retro # False
sun.dms # 00°19'
sun.signed_dms # 00°♉19'
sun.signed_deg # 0
sun.sign.name # taurus
sun.sign.symbol # ♉
sun.sign.value # 2
sun.sign.color # earth
sun.sign.ruler # venus
sun.sign.classic_ruler # venus
sun.sign.element # earth
sun.sign.modality # fixed
sun.sign.polarity # negative

# Aspect object
aspect = mimi.aspects[0]

aspect.body1 # sun Planet obj 
aspect.body2 # mars Planet obj
aspect.aspect_member # AspectMember(name='trine', symbol='△', value=120, color='air')
aspect.applying # False
aspect.orb # 3.3424
```

## Stats

- statistics of Data object in tabular form

```python
from natal import Stats

stats = Stats(data1=mimi, data2=transit)

print(stats.full_report(kind="markdown"))
```

- following markdown report will be produced:

```markdown
# Basic Information

| name    | location             | UTC time         |
|---------|----------------------|------------------|
| MiMi    | 25.0531°N, 121.526°E | 1980-04-20 06:30 |
| Transit | 25.0531°N, 121.526°E | 2024-01-01 05:30 |


# Element Distribution (MiMi)

| element   |  sum  | bodies                                          |
|-----------|-------|-------------------------------------------------|
| earth     |   4   | sun ♉ , jupiter ♍ , saturn ♍ , asc ♍        |
| water     |   2   | moon ♋ , uranus ♏                             |
| fire      |   4   | mercury ♈ , mars ♌ , neptune ♐ , asc_node ♌ |
| air       |   3   | venus ♊ , pluto ♎ , mc ♊                     |


# Modality Distribution (MiMi)

| modality   |  sum  | bodies                                                          |
|------------|-------|-----------------------------------------------------------------|
| fixed      |   4   | sun ♉ , mars ♌ , uranus ♏ , asc_node ♌                      |
| cardinal   |   3   | moon ♋ , mercury ♈ , pluto ♎                                 |
| mutable    |   6   | venus ♊ , jupiter ♍ , saturn ♍ , neptune ♐ , asc ♍ , mc ♊ |


# Polarity Distribution (MiMi)

| polarity   |  sum  | bodies                                                                        |
|------------|-------|-------------------------------------------------------------------------------|
| negative   |   6   | sun ♉ , moon ♋ , jupiter ♍ , saturn ♍ , uranus ♏ , asc ♍                |
| positive   |   7   | mercury ♈ , venus ♊ , mars ♌ , neptune ♐ , pluto ♎ , asc_node ♌ , mc ♊ |


# Celestial Bodies (MiMi)

| body     | sign         |  house  | dignity   |
|----------|--------------|---------|-----------|
| sun      | 00° ♉ 19'   |    8    |           |
| moon     | 08° ♋ 29'   |   10    | domicile  |
| mercury  | 08° ♈ 28'   |    8    |           |
| venus    | 15° ♊ 12'   |   10    |           |
| mars     | 26° ♌ 59'   |   12    |           |
| jupiter  | 00° ♍ 17' ℞ |   12    | detriment |
| saturn   | 21° ♍ 03' ℞ |    1    |           |
| uranus   | 24° ♏ 31' ℞ |    3    |           |
| neptune  | 22° ♐ 29' ℞ |    4    |           |
| pluto    | 20° ♎ 06' ℞ |    2    |           |
| asc_node | 26° ♌ 03' ℞ |   12    |           |
| asc      | 09° ♍ 42'   |    1    |           |
| mc       | 09° ♊ 13'   |   10    |           |


# Houses (MiMi)

| house   |    cusp    | ruler   |  ruler sign  |  ruler house  |
|---------|------------|---------|--------------|---------------|
| 1       | 09° ♍ 41' | mercury |      ♈      |       8       |
| 2       | 07° ♎ 13' | venus   |      ♊      |      10       |
| 3       | 07° ♏ 38' | pluto   |      ♎      |       2       |
| 4       | 09° ♐ 13' | jupiter |      ♍      |      12       |
| 5       | 10° ♑ 25' | saturn  |      ♍      |       1       |
| 6       | 10° ♒ 44' | uranus  |      ♏      |       3       |
| 7       | 09° ♓ 41' | neptune |      ♐      |       4       |
| 8       | 07° ♈ 13' | mars    |      ♌      |      12       |
| 9       | 07° ♉ 38' | venus   |      ♊      |      10       |
| 10      | 09° ♊ 13' | mercury |      ♈      |       8       |
| 11      | 10° ♋ 25' | moon    |      ♋      |      10       |
| 12      | 10° ♌ 44' | sun     |      ♉      |       8       |


# Quadrants (MiMi)

| quadrant   |  sum  | bodies                               |
|------------|-------|--------------------------------------|
| 1st ◵      |   3   | saturn, uranus, pluto                |
| 2nd ◶      |   1   | neptune                              |
| 3rd ◷      |   2   | sun, mercury                         |
| 4th ◴      |   5   | moon, venus, mars, jupiter, asc_node |


# Hemispheres (MiMi)

| hemisphere   |  sum  | bodies                                                      |
|--------------|-------|-------------------------------------------------------------|
| ←            |   8   | saturn, uranus, pluto, moon, venus, mars, jupiter, asc_node |
| →            |   3   | neptune, sun, mercury                                       |
| ↑            |   7   | sun, mercury, moon, venus, mars, jupiter, asc_node          |
| ↓            |   4   | saturn, uranus, pluto, neptune                              |


# Celestial Bodies of Transit in MiMi's chart

| Transit   | sign         |  house  | dignity   |
|-----------|--------------|---------|-----------|
| sun       | 10° ♑ 16'   |    4    |           |
| moon      | 08° ♍ 42'   |   12    |           |
| mercury   | 22° ♐ 14' ℞ |    4    | detriment |
| venus     | 02° ♐ 53'   |    3    |           |
| mars      | 27° ♐ 28'   |    4    |           |
| jupiter   | 05° ♉ 34'   |    8    |           |
| saturn    | 03° ♓ 15'   |    6    |           |
| uranus    | 19° ♉ 22' ℞ |    9    |           |
| neptune   | 25° ♓ 04'   |    7    |           |
| pluto     | 29° ♑ 21'   |    5    |           |
| asc_node  | 20° ♈ 51' ℞ |    8    |           |
| asc       | 14° ♉ 41'   |    9    |           |
| mc        | 02° ♒ 08'   |    5    |           |


# Aspects of Transit vs MiMi

| Transit   |  aspect  | MiMi     |  phase  | orb    |
|-----------|----------|----------|---------|--------|
| sun       |    ☍     | moon     |   → ←   | 1° 47' |
| sun       |    □     | mercury  |   → ←   | 1° 48' |
| sun       |    △     | asc      |   ← →   | 0° 34' |
| moon      |    ⚹     | moon     |   → ←   | 0° 13' |
| moon      |    ☌     | asc      |   → ←   | 1° 00' |
| moon      |    □     | mc       |   → ←   | 0° 31' |
| mercury   |    □     | saturn   |   → ←   | 1° 11' |
| mercury   |    ☌     | neptune  |   ← →   | 0° 15' |
| mars      |    △     | mars     |   ← →   | 0° 29' |
| mars      |    △     | asc_node |   ← →   | 1° 25' |
| uranus    |    △     | saturn   |   → ←   | 1° 41' |
| neptune   |    △     | uranus   |   ← →   | 0° 33' |
| pluto     |    □     | sun      |   ← →   | 0° 58' |
| asc_node  |    △     | neptune  |   ← →   | 1° 37' |
| asc_node  |    ☍     | pluto    |   → ←   | 0° 45' |
| mc        |    □     | sun      |   → ←   | 1° 49' |


# Aspect Cross Reference of Transit(cols) vs MiMi(rows)

|     |  ☉  |  ☽  |  ☿  |  ♀  |  ♂  |  ♃  |  ♄  |  ♅  |  ♆  |  ♇  |  ☊  |  Asc  |  MC  |  sum  |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-------|------|-------|
|  ☉  |     |     |     |     |     |     |     |     |     |  □  |     |       |  □   |   2   |
|  ☽  |  ☍  |  ⚹  |     |     |     |     |     |     |     |     |     |       |      |   2   |
|  ☿  |  □  |     |     |     |     |     |     |     |     |     |     |       |      |   1   |
|  ♀  |     |     |     |     |     |     |     |     |     |     |     |       |      |   0   |
|  ♂  |     |     |     |     |  △  |     |     |     |     |     |     |       |      |   1   |
|  ♃  |     |     |     |     |     |     |     |     |     |     |     |       |      |   0   |
|  ♄  |     |     |  □  |     |     |     |     |  △  |     |     |     |       |      |   2   |
|  ♅  |     |     |     |     |     |     |     |     |  △  |     |     |       |      |   1   |
|  ♆  |     |     |  ☌  |     |     |     |     |     |     |     |  △  |       |      |   2   |
|  ♇  |     |     |     |     |     |     |     |     |     |     |  ☍  |       |      |   1   |
|  ☊  |     |     |     |     |  △  |     |     |     |     |     |     |       |      |   1   |
| Asc |  △  |  ☌  |     |     |     |     |     |     |     |     |     |       |      |   2   |
| MC  |     |  □  |     |     |     |     |     |     |     |     |     |       |      |   1   |
```

- see [demo.ipynb] for the HTML output

## PDF Report

- install with `uv add natal-report`
- see [natal-report] package for details
- [light theme PDF sample]
- [mono theme PDF sample]

## Configuration

- create a `Config` object and assign it to `Data` object
- it will override the default settings in `config.py`
- a sample config as follow:

```py
from natal.config import Display, Config, Orb

# adjust which celestial bodies to display
display = Display(
    mc = False,
    asc_node = False,
    chiron = True
)

# adjust orbs for each aspect
orb = Orb(
    conjunction = 8,
    opposition = 8,
    trine = 6,
    square = 6,
    sextile = 6
)

# the complete config object
config = Config(
    theme_type = "light", # or "dark", "mono"
    display = display,
    orb = orb
)

# create data object with the config
data = Data(
    name = "MiMi",
    utc_dt = "1980-04-20 06:30",
    lat = 25.0531,
    lon = 121.526,
    config = config,
)
```

read the [docs] for complete references

## Tech Stack

- [tagit]: SVG / HTML generation and manipulation
- [pyswisseph]: astrological data - Swiss Ephemeris
- [mkdocs-material]: docs site generation

[light theme PDF sample]: https://github.com/hoishing/natal-report/blob/main/demo_report_light.pdf
[mono theme PDF sample]: https://github.com/hoishing/natal-report/blob/main/demo_report_mono.pdf
[demo.ipynb]: https://github.com/hoishing/natal/blob/main/demo.ipynb
[docs]: https://hoishing.github.io/natal
[mkdocs-material]: https://github.com/squidfunk/mkdocs-material
[natal-report]: https://github.com/hoishing/natal-report
[pyswisseph]: https://github.com/astrorigin/pyswisseph
[Swiss Ephemeris]: https://www.astro.com/swisseph/swephinfo_e.htm
[tagit]: https://github.com/hoishing/tagit
