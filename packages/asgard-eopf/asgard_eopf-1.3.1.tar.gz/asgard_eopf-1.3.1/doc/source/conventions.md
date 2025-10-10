# Conventions

## Time encoding

The time in ASGARD is encoded using:

* a reference epoch (always 2000-01-01T00:00:00 for EOCFI based implementations)
* a delta from this epoch (encoded in `float64`)
* a unit (always Julian days for EOCFI based implementations)

Usually, times arrays are handled by ASGARD, so we store the fields:

* "epoch": reference epoch as `str`
* "offset": Numpy array of `float64`
* "unit": Unit for offsets ("d" or "s") (resp. Julian days or seconds)

The time scale is independent from the time encoding. The time encoding may be expressed in any of
these time scales:

* TAI
* UTC
* UT1
* GPS

## Geodetic coordinates

The geodetic coordinates are usually expressed as:

* longitude (in deg)
* latitude (in deg)
* altitude (in m)

## Cartographic coordinates

ASGARD handles most of the computations in geodetic coordinates (lon, lat, height). For conversions
with other cartographic projections, users should rely on
[pyproj](https://pyproj4.github.io/pyproj/stable/index.html). This library has a comprehensive list
of supported projection. In particular, it is possible to apply transforms to Numpy arrays
efficiently, like in this
[example](https://pyproj4.github.io/pyproj/stable/advanced_examples.html#repeated-transformations).

## Style/Typography

When refering to ASGARD and ASGARD-Legacy, please comply with the following guidelines:

| context  | typography      |
| -------- | --------------- |
| name/doc | `ASGARD-Legacy` |
| file/url | `asgard-legacy` |
| variable | `asgard_legacy` |
| constant | `ASGARD_LEGACY` |

The idea is the same for ASGARD, except that the Python package is called
`asgard_eopf` due to a conflict in [Python package index](https://pypi.org).

Please refer to [PEP 8](https://peps.python.org/pep-0008/)
for more information on that matter.
