# Python SLURM benchmark manager framework

<!-- [![Latest release](https://gitlab.com/vepain/slurmbench-py/-/badges/release.svg)](https://gitlab.com/vepain/slurmbench-py/-/releases) -->
<!-- [![Coverage report](https://gitlab.com/vepain/slurmbench-py/badges/main/coverage.svg)](https://gitlab.com/vepain/slurmbench-py/-/commits/main) -->
[![PyPI version](https://badge.fury.io/py/slurmbench.svg)](https://badge.fury.io/py/slurmbench)
[![Ruff](https://gitlab.com/vepain/slurmbench-py/-/jobs/artifacts/main/raw/ruff/ruff.svg?job=ruff)](https://gitlab.com/vepain/slurmbench-py/-/commits/main)
[![Mypy](https://gitlab.com/vepain/slurmbench-py/-/jobs/artifacts/main/raw/mypy/mypy.svg?job=mypy)](https://gitlab.com/vepain/slurmbench-py/-/commits/main)
[![Pipeline status](https://gitlab.com/vepain/slurmbench-py/badges/main/pipeline.svg)](https://gitlab.com/vepain/slurmbench-py/-/commits/main)
[![Documentation Status](https://readthedocs.org/projects/slurmbench/badge/?version=latest)](https://slurmbench.readthedocs.io/en/latest)

## Install

Requires:

* `slurm`
* `bash`
* `python 3.13`

### Python environments

### With conda

<!-- DOCU condaenv for dev -> change when user's one is ready -->
* [*For dev*] Create the conda environment

  ```sh
  conda env create -n slurmbench-dev -f config/condaenv_313-dev.yml
  ```

* [*For dev*] Activate the conda environment

  ```sh
  conda activate slurmbench-dev
  ```

#### With virtualenv

```sh
python3.13 -m virtualenv .venv_slurmbench_313
source ./.venv_slurmbench_313/bin/activate  # active.fish for fish shell...
pip install .  # `pip install -e .` for editable mode i.e. for dev
```

## Usage

<!-- DOCU change now it is slurmbench -->
```sh
slurmbench --help
```

## Create automatic documentation

<!-- DOCU change now it is slurmbench -->
```sh
slurmbench doc auto  # creates autodoc in `docs` directory
slurmbench doc clean  # to clean the auto documentation
```
