"""Flax-like computed parameters for bare JAX."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Iterator

    import numpy as np

import equinox as eqx
import jax
import jax.numpy as jnp

T = TypeVar("T")


class Param(eqx.Module, Generic[T]):
    """Base class for a parameter."""

    raw_value: jax.Array
    """The raw, stored value of the parameter."""

    def __init__(self, value: T | jax.Array | np.ndarray[Any, Any]) -> None:
        """Initialize the parameter.

        **Arguments:**

        - `value`: The value of the parameter.
        """
        self.raw_value = jnp.asarray(value)

    @property
    def value(self) -> jax.Array:
        """The value of the parameter.

        Subclasses can override this property to return any other value
        computed from `raw_value`.
        """
        return self.raw_value

    def __jax_array__(self) -> jax.Array:
        return self.value

    def __getitem__(self, key: Any) -> Any:
        return self.value[key]

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.value)

    def __contains__(self, item: object) -> bool:
        return item in self.value

    def __add__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__add__(other)

    def __sub__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__sub__(other)

    def __mul__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__mul__(other)

    def __matmul__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__matmul__(other)

    def __truediv__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__truediv__(other)

    def __floordiv__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__floordiv__(other)

    def __mod__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__mod__(other)

    def __divmod__(self, other: Any) -> tuple[jax.Array, jax.Array]:
        if isinstance(other, Param):
            other = other.value
        return self.value.__divmod__(other)

    def __pow__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__pow__(other)

    def __radd__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__radd__(other)

    def __rsub__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__rsub__(other)

    def __rmul__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__rmul__(other)

    def __rmatmul__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__rmatmul__(other)

    def __rtruediv__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__rtruediv__(other)

    def __rfloordiv__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__rfloordiv__(other)

    def __rmod__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__rmod__(other)

    def __rdivmod__(self, other: Any) -> tuple[jax.Array, jax.Array]:
        if isinstance(other, Param):
            other = other.value
        return self.value.__rdivmod__(other)  # type: ignore[return-value]

    def __rpow__(self, other: Any) -> jax.Array:
        if isinstance(other, Param):
            other = other.value
        return self.value.__rpow__(other)

    def __neg__(self) -> jax.Array:
        return self.value.__neg__()

    def __pos__(self) -> jax.Array:
        return self.value.__pos__()

    def __abs__(self) -> jax.Array:
        return self.value.__abs__()

    def __invert__(self) -> jax.Array:
        return self.value.__invert__()

    def __complex__(self) -> complex:
        return self.value.__complex__()

    def __int__(self) -> int:
        return self.value.__int__()

    def __float__(self) -> float:
        return self.value.__float__()

    def __index__(self) -> int:
        return self.value.__index__()

    def __round__(self, ndigits: int) -> jax.Array:
        return self.value.__round__(ndigits)
