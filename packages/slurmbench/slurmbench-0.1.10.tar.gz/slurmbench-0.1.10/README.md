# Python SLURM benchmark manager framework

[![PyPI][pypi_badge]][pypi_link] <!-- [![Coverage report][coverage_badge]][coverage_link] -->
[![Mypy][mypy_badge]][mypy_link]
[![Ruff][ruff_badge]][ruff_link]
[![Pipeline status][pipeline_badge]][pipeline_link]
[![Documentation][docs_badge]][docs_link]
[![License][license_badge]][licence_link]

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


<!-- Badges -->

<!--
Changes:
* PyPI project name `slurmbench`
* Git project name `slurmbench-py`
* GitLab project ID `75007090`
-->

[pypi_badge]: https://img.shields.io/pypi/v/slurmbench?style=for-the-badge&logo=python&color=blue "Package badge"
[pypi_link]: https://pypi.org/project/slurmbench/ "Package link"

[coverage_badge]: https://img.shields.io/gitlab/pipeline-coverage/vepain%2Fslurmbench-py?job_name=test_coverage&branch=main&style=for-the-badge&logo=codecov "Coverage badge"
[coverage_link]: https://gitlab.com/vepain/slurmbench-py/-/commits/main "Coverage link"

[ruff_badge]: https://img.shields.io/endpoint?url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2F75007090%2Fjobs%2Fartifacts%2Fmain%2Fraw%2Fruff%2Fbadge.json%3Fjob%3Druff&style=for-the-badge&logo=ruff&label=Ruff "Ruff badge"
[ruff_link]: https://gitlab.com/vepain/slurmbench-py/-/commits/main "Ruff link"

<!-- https://gitlab.com/api/v4/projects/75007090/jobs/artifacts/main/raw/ruff/badge.json?job=ruff -->

[mypy_badge]: https://img.shields.io/endpoint?url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2F75007090%2Fjobs%2Fartifacts%2Fmain%2Fraw%2Fmypy%2Fbadge.json%3Fjob%3Dmypy&style=for-the-badge&label=Mypy "Mypy badge"
[mypy_link]: https://gitlab.com/vepain/slurmbench-py/-/commits/main "Mypy link"

[pipeline_badge]: https://img.shields.io/gitlab/pipeline-status/vepain%2Fslurmbench-py?branch=main&style=for-the-badge&logo=circleci "Pipeline badge"
[pipeline_link]: https://gitlab.com/vepain/slurmbench-py/-/commits/main "Pipeline link"

[docs_badge]: https://img.shields.io/readthedocs/slurmbench?style=for-the-badge&logo=readthedocs "Documentation badge"
[docs_link]: https://slurmbench.readthedocs.io/en/latest/ "Documentation link"

[license_badge]: https://img.shields.io/gitlab/license/vepain%2Fslurmbench-py?style=for-the-badge&logo=readdotcv&color=green "Licence badge"
[licence_link]: https://gitlab.com/vepain/slurmbench-py "Licence link"
