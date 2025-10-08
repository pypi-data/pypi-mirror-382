# <div align="center">[<img src="https://raw.githubusercontent.com/gerlero/parametrix/main/logo.png" alt="Parametrix logo" width=250></img>](https://github.com/gerlero/parametrix/)</div>

**[`flax.nnx.Param`](https://flax.readthedocs.io/en/latest/api_reference/flax.nnx/variables.html#flax.nnx.Param)-like computed parameters for bare [JAX](https://github.com/jax-ml/jax) (and [Equinox](https://github.com/patrick-kidger/equinox)).**

[![Documentation](https://img.shields.io/readthedocs/parametrix)](https://parametrix.readthedocs.io/)
[![CI](https://github.com/gerlero/parametrix/actions/workflows/ci.yml/badge.svg)](https://github.com/gerlero/parametrix/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/gerlero/parametrix/branch/main/graph/badge.svg)](https://codecov.io/gh/gerlero/parametrix)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Publish](https://github.com/gerlero/parametrix/actions/workflows/pypi-publish.yml/badge.svg)](https://github.com/gerlero/parametrix/actions/workflows/pypi-publish.yml)
[![PyPI](https://img.shields.io/pypi/v/parametrix)](https://pypi.org/project/parametrix/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/parametrix)](https://pypi.org/project/parametrix/)


## Installation

```bash
pip install parametrix
```

## Example

The following example shows how to use [`Param`](https://parametrix.readthedocs.io) as a base class for a parameter class that enforces positivity:

```python
import jax.numpy as jnp
from parametrix import Param

class PositiveOnlyParam(Param):
    def __init__(self, value):
        super().__init__(jnp.log(value))

    @property
    def value(self):
        return jnp.exp(self.raw_value)
```

The backing values of `Param`s are always stored as `jax.Array`s, meaning that they will automatically be picked up as learnable parameters by libraries like Equinox.

`Param` objects also behave like numeric types, so that they are able to be used within models and any other functions without having to make any changes to the code.

## Documentation

API documentation is available at [Read the Docs](https://parametrix.readthedocs.io/).
