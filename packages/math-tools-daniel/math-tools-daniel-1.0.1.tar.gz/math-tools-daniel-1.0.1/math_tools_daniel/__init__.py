"""
Math Tools Daniel - Um pacote matemático completo.

Este pacote fornece funções matemáticas básicas e avançadas, incluindo:
- Funções básicas: fatorial, números primos, média, Fibonacci
- Funções auxiliares: MDC, MMC, números perfeitos, exponenciação modular
- Estatística: mediana, moda, desvio padrão, variância, quartis
- Sequências: Fibonacci, primos, progressões, Collatz

Autor: Daniel Santos
Versão: 1.0.0
Email: danfergatthi@gmail.com
"""

# Importa as funções principais
from .utils import (
    factorial,
    is_prime,
    average,
    fibonacci,
    is_perfect_number,
    gcd,
    lcm,
    prime_factors,
    power_mod,
    validate_number_list
)

from .processing import (
    median,
    mode,
    standard_deviation,
    variance,
    quartiles,
    fibonacci_sequence,
    prime_sequence,
    arithmetic_sequence,
    geometric_sequence,
    factorial_sequence,
    collatz_sequence
)

# Metadados do pacote
__version__ = "1.0.0"
__author__ = "Daniel Santos"
__email__ = "danfergatthi@gmail.com"
__description__ = "Um pacote matemático completo com funções básicas e avançadas"

# Lista de todas as funções exportadas
__all__ = [
    # Funções básicas
    'factorial',
    'is_prime',
    'average',
    'fibonacci',

    # Funções auxiliares
    'is_perfect_number',
    'gcd',
    'lcm',
    'prime_factors',
    'power_mod',
    'validate_number_list',

    # Estatística
    'median',
    'mode',
    'standard_deviation',
    'variance',
    'quartiles',

    # Sequências
    'fibonacci_sequence',
    'prime_sequence',
    'arithmetic_sequence',
    'geometric_sequence',
    'factorial_sequence',
    'collatz_sequence'
]