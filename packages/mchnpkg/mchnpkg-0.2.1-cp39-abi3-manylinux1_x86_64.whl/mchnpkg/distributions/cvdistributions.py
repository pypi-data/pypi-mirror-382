# mchnpkg/distributions/cvdistributions.py
"""
Cryptographically secure random distributions using Python's `secrets`.
- IEEE-754 double has 53-bit mantissa => use 53 random bits for U in [0,1).
- Inverse-CDF for Exponential: F^{-1}(u) = -ln(1 - u) / lambda
"""

from __future__ import annotations
import math
import secrets
from typing import List

_TWO_POW_53 = 1 << 53  # 2**53

def _u01() -> float:
    """Return U ~ Uniform[0,1) using 53 random bits (cryptographically secure)."""
    return secrets.randbits(53) / _TWO_POW_53

# ---------- Uniform ----------
def uniform(a: float = 0.0, b: float = 1.0) -> float:
    """One sample from Uniform(a, b) with cryptographic randomness."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("a and b must be real numbers")
    if not b > a:
        raise ValueError("require b > a")
    u = _u01()                 # in [0,1)
    return a + (b - a) * u     # in [a,b)

def uniform_samples(n: int, a: float = 0.0, b: float = 1.0) -> List[float]:
    """n IID Uniform(a, b) samples."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return [uniform(a, b) for _ in range(n)]

# ---------- Exponential (new) ----------
def exponentialdist(lmbda: float) -> float:
    """
    One sample from Exponential(lambda), lambda > 0, via inverse transform:
        X = -ln(1 - U) / lambda,  U ~ U(0,1).
    Uses log1p for numerical stability when U is near 0.
    """
    if not isinstance(lmbda, (int, float)) or not (lmbda > 0.0):
        raise ValueError("lambda must be a positive real number")
    u = _u01()                       # in [0,1)
    return -math.log1p(-u) / lmbda   # log1p(-u) == ln(1 - u)

def exponential_samples(n: int, lmbda: float) -> List[float]:
    """n IID Exponential(lambda) samples."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    if not isinstance(lmbda, (int, float)) or not (lmbda > 0.0):
        raise ValueError("lambda must be a positive real number")
    # comprehension is fast and keeps cryptographic calls independent
    return [-math.log1p(-_u01()) / lmbda for _ in range(n)]

# ---------- Self-test (optional) ----------
if __name__ == "__main__":
    xs = exponential_samples(5, 1.0)
    print("5 samples Exp(1):", xs)
    print("mean ~ 1.0:", sum(xs) / len(xs))



# ---------- Poisson via discrete inverse transform ----------
def poissondist(lmbda: float) -> int:
    """
    One sample from Poisson(lambda) using inverse CDF (discrete).
    Recurrence for PMF:
        p0 = exp(-lambda)
        p_{k+1} = p_k * lambda / (k+1)
    We accumulate c = sum_{i=0}^k p_i until U <= c.
    """
    if not isinstance(lmbda, (int, float)) or not (lmbda > 0.0):
        raise ValueError("lambda must be a positive real number")

    u = _u01()           # in [0,1)
    k = 0
    p = math.exp(-lmbda) # p_0
    c = p                # cumulative up to k=0
    while u > c:
        k += 1
        p *= lmbda / k   # p_k from p_{k-1}
        c += p
    return k

def poisson_samples(n: int, lmbda: float) -> List[int]:
    """n IID Poisson(lambda) samples via poissondist."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return [poissondist(lmbda) for _ in range(n)]

# (Optional) preserve an alias if the assignment spells it "poissiondist"
poissiondist = poissondist  # alias to satisfy spec variations
