"""
Módulo utils do pacote math_tools_daniel.

Este módulo contém funções matemáticas básicas e auxiliares.
"""

from .math_functions import factorial, is_prime, average, fibonacci
from .math_helpers import (
    is_perfect_number,
    gcd,
    lcm,
    prime_factors,
    power_mod,
    validate_number_list
)

__all__ = [
    'factorial',
    'is_prime',
    'average',
    'fibonacci',
    'is_perfect_number',
    'gcd',
    'lcm',
    'prime_factors',
    'power_mod',
    'validate_number_list'
]