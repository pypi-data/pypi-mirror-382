# mchnpkg/distributions/cvdistributions.py
"""
Cryptographically secure random distributions using Python's `secrets`.
IEEE-754 double has 53-bit mantissa => use 53 random bits for U in [0,1).
"""

from __future__ import annotations
import math
import secrets
from typing import Iterable, List

_TWO_POW_53 = 1 << 53  # 2**53

def _u01() -> float:
    """Return U ~ Uniform[0,1) using 53 random bits (cryptographically secure)."""
    return secrets.randbits(53) / _TWO_POW_53

def uniform(a: float = 0.0, b: float = 1.0) -> float:
    """Return one sample from Uniform(a, b) using cryptographically secure bits."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("a and b must be real numbers")
    if not b > a:
        raise ValueError("require b > a")
    u = _u01()                 # in [0,1)
    return a + (b - a) * u     # in [a,b)

def uniform_samples(n: int, a: float = 0.0, b: float = 1.0) -> List[float]:
    """Return n IID samples from Uniform(a, b) using `uniform`."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return [uniform(a, b) for _ in range(n)]







