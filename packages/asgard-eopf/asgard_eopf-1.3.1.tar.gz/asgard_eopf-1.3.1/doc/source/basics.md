# Basic functions

To instantiate a Geometry, a dictionnary shall be define.
In order to define this dictionnary, some basic functions of ASGARD can be used.
This sections presents the main ones.

## Orbit transformation

Orbit can be expressed in different frames.
A transforataion between Frame can be performed using
`EarthBody.transform_orbit`,
see [API documentation](https://geolib.pages.eopf.copernicus.eu/asgard/apidoc/asgard.models.html#asgard.models.body.EarthBody.transform_orbit).
It is for example mandatory before a merge is done, to make sure orbits are all in the same frame
An example is available in `test_merge_orbits` in `tests/test_models_orbit.py`.

```python
bulletin = open("bulletinb-413.txt").readlines() # from datacenter.iers.org
time_model = TimeReference(iers_bulletin_b=bulletin)
body_model = EarthBody(time_reference=time_model)
body_model.transform_orbit(orbit, FrameId.EF)
```

`TimeReference` [IERS bulletin](https://datacenter.iers.org/bulletins.php)
should match the `orbit` start/end date range.

Please note that the transformation is done in-place. If you need to keep the
original orbit, you will have to make a copy using: `dict.copy()`.

More information on frames can be found on [Orekit website](https://www.orekit.org/site-orekit-11.3.3/architecture/frames.html).

## Getting Orbit Information

Orbit information can be computed through orbits Low-level models. There are two orbit model available:
* `GenericOrbitModel` : taking as input a list of OSV from NAVATT or FRO/FPO files, orbit info like anx are found by interpolation. 
Note that cycle and phase number are not computed in this case.   
* `OrbitScenarioModel` : taking as input a list of orbit information from OSF. An orbit propagation is performed. In nominal case OSF should be used to compute light information (see below). The propagation should be performed only in degraded case (no FPO/FRO available)

Example using ASGARD:

### using orbit states vector 

```python
from asgard.models.time import TimeReference
from asgard.models.body import EarthBody
from asgard.models.orbit import GenericOrbitModel

#Configure the TimeReference
config_time = {
    "iers_bulletin_a": iers_data,
}
time_model = TimeReference(**config_time)

#Configure the EarthBody
config_earth_body = {"time_reference": time_model}
earth_body = EarthBody(**config_earth_body)

# Configure the Orbit
time_orb_gps = 8338.064236111111
time_orb_str = f"GPS={time_model.to_str(time_orb_gps, ref_in=TimeRef.GPS)}"

# attitude are not used for orbit information, an attitude mode could be used.
config_orbit_model = {
    "orbit": [ORBIT],
    "attitude": {"aocs_mode": "YSM"},
    "time_orb": time_orb_str,
    "earth_body": earth_body,
}
orbit_model = GenericOrbitModel(**config_orbit_model)

# Get the orbit information
orbit_info = orbit_model.info

# Get orbit information at another date
orbit_info = orbit_model.get_info(date)
```

> Please note that cycle and phase are not computed.

### using orbit scenario  

```python
from asgard.models.time import TimeReference
from asgard.models.body import EarthBody
from asgard.models.orbit import OrbitScenarioModel

#Configure the TimeReference
config_time = {
    "iers_bulletin_a": iers_data,
}
time_model = TimeReference(**config_time)

#Configure the EarthBody
config_earth_body = {"time_reference": time_model}
earth_body = EarthBody(**config_earth_body)

# Configure the Orbit propagation initialization 
time_orb_gps = 8338.064236111111
time_orb_str = f"GPS={time_model.to_str(time_orb_gps, ref_in=TimeRef.GPS)}"

config_orbit_model = {
    "orbit": [ORBIT],
    "orbit_frame": "EME2000",
    "attitude": {"aocs_mode": "YSM"},
    "time_orb": time_orb_str,
    "earth_body": earth_body,
}
orbit_model = OrbitScenarioModel(**config_orbit_model)

# Get the orbit information for L0 (absolute orbit number,relative orbit number,phase id,cycle number)
light_orbit_info = orbit_model.get_info(date, light=True)

# Get complete orbit info (ANX, mean Keplerians elements, ...), by perfoming orbit propagation
orbit_info = orbit_model.get_info(date)
```


Example using ASGARD-Legacy:
```python
    from asgard_legacy.wrappers.eocfi.product import GenericProduct

    # Get orbit_scenario
    orbit_scenario = [...]

    # Init Orbit Model
    gpd = GenericProduct("SENTINEL_3A")
    gpd.init_model()
    gpd.init_time(orbit_scenario=[orbit_scenario])
    gpd.init_orbit(orbits=[], orbit_scenario=[orbit_scenario])

    # Get orbit information
    anx = gpd.orbit_info(8338.064236111111)
```
Please note that if the orbit is not containing OSF information, cycle and phase number won't be computed.

## Time conversion

To convert time, use methods from `TimeReference` class, see [API documentation](https://geolib.pages.eopf.copernicus.eu/asgard/apidoc/asgard.models.html#asgard.models.time.TimeReference.convert)

`TimeReference` can be initialized without argument. The leap second management is done using underlying orekit data UTC-TAI history.
The UTC-UT1 difference can be set (0 by default without argument) using iers bulletin or by a lut from orbit files (see  examples in `tests/test_models_time.py`)   

```python
with open("/path/to/iers/bulletin.txt", "r", encoding="utf-8") as iers_file:
    iers_lines = iers_file.readlines()

tai_value = 8330.890787037037
trf = TimeReference(iers_bulletin_a=iers_lines)
trf.convert(tai_value, TimeRef.TAI, TimeRef.UTC)
>>> 8330.890358796296
```

More examples available in `tests/test_models_time.py`.

More information on time can be found on [Orekit website](https://www.orekit.org/site-orekit-11.3.3/architecture/time.html).

## Elevation retrival

DEM (Digital Elevation Model) is an important part of the geolocalisation process.
To retrive the elevation on dedicated coordinates, the ElevationManager class can be used.

Please note that:

* The GETAS ZARR requires to have "half_pixel_dem_shift" at True, for others, it shall be put at False
* Latitude and Longitude shall be provided as radians

 Here is an example of use:

```python
import os.path as osp
from pyrugged.raster.simple_tile import SimpleTile
from asgard.models.dem import ElevationManager

# Configure the DEM path. It can also be provided as FStore or Xarray
dem_path = osp.join(
    ASGARD_DATA,
    "ADFstatic/S0__ADF_GETAS_20000101T000000_21000101T000000_20240325T113307.zarr",
)

# Create an elevation Manager
elev = ElevationManager(dem_path=dem_path, half_pixel_dem_shift=True, tile_lon=1000)

# Create a SimpleTile that will load the DEM data around the Lat/Lon require, with a size of tile_lon
tile = SimpleTile()

# Configure the required lat/lon in radians
latitude = np.radians(43.601111)
longitude = np.radians(1.449722)

# Update the SimpleTile object to load the elevation
elev.update_tile(latitude, longitude, tile)

# Perform an bi-lenear interpolation of the altitude at the required lat/lon
altitude = tile.interpolate_elevation(latitude, longitude)
```

NOTE: function [interpolate_elevation_arr](https://gitlab.eopf.copernicus.eu/geolib/pyrugged/-/blob/1.1.2/pyrugged/raster/simple_tile.py#L541) is also available

Other examples can be found in [test_models_dem.py](https://gitlab.eopf.copernicus.eu/geolib/asgard/-/blob/1.1.0/tests/test_models_dem.py)
