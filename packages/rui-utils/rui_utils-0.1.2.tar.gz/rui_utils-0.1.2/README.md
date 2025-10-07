[![build-badge](https://github.com/xiachenrui/rui_utils/actions/workflows/build.yml/badge.svg)](https://github.com/xiachenrui/rui_utils/actions/workflows/build.yml)
![PyPI](https://img.shields.io/pypi/v/rui_utils?label=pypi)
[![Downloads](https://static.pepy.tech/badge/rui_utils)](https://pepy.tech/project/rui_utils)
![Python 3.10](https://img.shields.io/badge/python->=3.10-blue.svg)
[![codecov](https://codecov.io/gh/xiachenrui/rui_utils/graph/badge.svg?token=zgwG4u9v0F)](https://codecov.io/gh/xiachenrui/rui_utils)
[![license-badge](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# rui_utils

## Installation

> [!IMPORTANT]
> Requires Python >= 3.10 and CUDA-enabled GPU (CPU-only device is not recommended).

We recommend to install `rui_utils` to a new conda environment with [RAPIDS](https://docs.rapids.ai/install) dependencies.

```sh
mamba create -n rui_utils -c conda-forge -c rapidsai -c nvidia python=3.11 rapids=25.06 'cuda-version>=12.0,<=12.8' -y && conda activate rui_utils
pip install rui_utils
```
