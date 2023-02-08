"""
    name: factor
    once: false
    origin: tgpy://module/factor
    priority: 1674448904.86973
    save_locals: true
"""
from collections import defaultdict
import subprocess
import sympy


def factor_rho(n):
    res = subprocess.run(["factor", str(n)], capture_output=True)
    return list(map(int, res.stdout.decode().partition(":")[2].split()))


def factor_ecm(n):
    res = subprocess.run(["ecm", "-q", "3000000"], input=str(n).encode(), capture_output=True)
    prefactors = list(map(int, res.stdout.decode().split()))
    factors = []
    for prefactor in prefactors:
        factors += factor(prefactor)
    return factors


def _factor(n):
    if sympy.isprime(n):
        return [n]
    if n < 10 ** 38:
        return factor_rho(n)
    return factor_ecm(n)


@dot
def factor(n):
    return sorted(_factor(int(n)))


@dot
def factor_text(n):
    n = int(n)
    if n == 1:
        return "1"
    by_power = defaultdict(int)
    for x in factor(n):
        by_power[x] += 1
    return " × ".join(str(k) if v == 1 else str(k) + superscript(v) for k, v in by_power.items())


def superscript(n):
    return ("⁻" if n < 0 else "") + "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(c)] for c in str(abs(n)))
