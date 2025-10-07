"""
Módulo processing do pacote math_tools_daniel.

Este módulo contém funções para processamento estatístico e de sequências matemáticas.
"""

from .statistics import (
    median,
    mode,
    standard_deviation,
    variance,
    quartiles
)

from .sequences import (
    fibonacci_sequence,
    prime_sequence,
    arithmetic_sequence,
    geometric_sequence,
    factorial_sequence,
    collatz_sequence
)

__all__ = [
    'median',
    'mode',
    'standard_deviation',
    'variance',
    'quartiles',
    'fibonacci_sequence',
    'prime_sequence',
    'arithmetic_sequence',
    'geometric_sequence',
    'factorial_sequence',
    'collatz_sequence'
]