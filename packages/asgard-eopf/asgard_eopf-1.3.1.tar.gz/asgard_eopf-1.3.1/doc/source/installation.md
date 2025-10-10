# Installation Procedure 

*TL;DR*: end users only need:

```sh
pip install asgard_eopf
```

→ it will install the latest stable release from [PyPI](https://pypi.org/project/asgard-eopf/).


## Technical details

ASGARD is part of the DPR project which aims at unifying Copernicus Sentinel
software stack, the Legacy packages are developped to test and asses the level
of ISO funcitonnality.

Here is a snapshot of ASGARD and ASGARD-Legacy main dependencies:

![](doc/source/resources/dependencies_map.png)

**NOTE**: The standard Python dependencies (Numpy, ...) are not shown here for clarity,
only the ones not available on public repository.

ASGARD based on [PyRugged](https://gitlab.eopf.copernicus.eu/geolib/pyrugged)
and [Orekit-JCC](https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc).


### PyRugged

[PyRugged](https://gitlab.eopf.copernicus.eu/geolib/pyrugged) is a Python port
of [Rugged](https://gitlab.orekit.org/orekit/rugged) (Java).
The refactored products and low-level API make use of this implementation.

It may also be built from sources, the only non-standard dependency is Orekit-JCC which provides the bindings to Orekit.


### Orekit-JCC

[Orekit-JCC](https://gitlab.eopf.copernicus.eu/geolib/orekit-jcc) is an
interface layer between ASGARD/PyRugged and [Orekit](https://gitlab.orekit.org/orekit/orekit).
It is a Java project compiled and wrapped to Python using
[JCC](https://lucene.apache.org/pylucene/jcc/) and
[GraalVM](https://github.com/graalvm/graalvm-ce-builds/releases?q=jdk).


## Installation guide for developers

First, some additional libraries and necessary system dependencies shall be installed:
```sh
sudo apt-get install python3-venv libpython3-dev gcc git
```

Then, clone [ASGARD repository](https://gitlab.eopf.copernicus.eu/geolib/asgard):
```sh
git clone https://gitlab.eopf.copernicus.eu/geolib/asgard.git
```

Finally, go to the folder you just cloned, create a virtual-environement,
upgrade `pip` if need be, and install `asgard-eopf`, here with the `dev`
[dependency-group](https://pip.pypa.io/en/stable/user_guide/#dependency-groups):
```sh
cd asgard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e . --group dev
```

Here, `pip install -e` install the project in editable mode (i.e. setuptools "develop mode").
The "editable mode" is required since cython shared objects need to be kept in place to be able to import the project
in [*flat-layout*](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).
*ie*. if `-e` option is not set, you might get `ImportError: no module named asgard.core.math` error,
because the locally built cython binary is deleted after the package installation.

**NOTE**: You can also install the notebook dependencies: `pip install -e . --group notebook`
or the default mode by providing nothing: `pip install -e .`


## Tests and validation

The tests and validation data can be found on S3 bucket, and should be located
in a folder referred by the environment variable: `export ASGARD_DATA=[PATH_TO_ASGARD_DATA]`.
Please ask the credentials and use the script `gitlab-ci/download.py` to download them.

This step can take a while since it needs to download **29GB**, once done,
you can run `pytest` command to check if ASGARD is well installed.
