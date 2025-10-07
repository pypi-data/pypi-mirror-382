"""
Módulo de funções auxiliares matemáticas.

Este módulo contém funções auxiliares e utilitárias para operações matemáticas
mais avançadas e validações.

Autor: Daniel Santos
Versão: 1.0.0
"""

from typing import List, Union, Tuple
import math


def is_perfect_number(n: int) -> bool:
    """
    Verifica se um número é perfeito.

    Um número perfeito é um número natural que é igual à soma
    de seus divisores próprios (excluindo ele mesmo).

    Args:
        n (int): Número inteiro a ser verificado.

    Returns:
        bool: True se o número for perfeito, False caso contrário.

    Examples:
        >>> is_perfect_number(6)
        True
        >>> is_perfect_number(28)
        True
        >>> is_perfect_number(12)
        False
    """
    if not isinstance(n, int) or n <= 1:
        return False

    divisors_sum = 1  # 1 é sempre um divisor próprio
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            divisors_sum += i
            if i != n // i:  # Evita contar a raiz quadrada duas vezes
                divisors_sum += n // i

    return divisors_sum == n


def gcd(a: int, b: int) -> int:
    """
    Calcula o Máximo Divisor Comum (MDC) de dois números.

    Utiliza o algoritmo de Euclides para encontrar o MDC.

    Args:
        a (int): Primeiro número inteiro.
        b (int): Segundo número inteiro.

    Returns:
        int: O MDC de a e b.

    Examples:
        >>> gcd(48, 18)
        6
        >>> gcd(17, 13)
        1
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Ambos os argumentos devem ser números inteiros")

    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """
    Calcula o Mínimo Múltiplo Comum (MMC) de dois números.

    Utiliza a relação: MMC(a,b) = |a*b| / MDC(a,b)

    Args:
        a (int): Primeiro número inteiro.
        b (int): Segundo número inteiro.

    Returns:
        int: O MMC de a e b.

    Examples:
        >>> lcm(4, 6)
        12
        >>> lcm(3, 7)
        21
    """
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Ambos os argumentos devem ser números inteiros")

    if a == 0 or b == 0:
        return 0

    return abs(a * b) // gcd(a, b)


def prime_factors(n: int) -> List[int]:
    """
    Encontra todos os fatores primos de um número.

    Args:
        n (int): Número inteiro positivo para fatorar.

    Returns:
        List[int]: Lista dos fatores primos de n.

    Raises:
        ValueError: Se n for menor ou igual a 1.

    Examples:
        >>> prime_factors(12)
        [2, 2, 3]
        >>> prime_factors(17)
        [17]
        >>> prime_factors(60)
        [2, 2, 3, 5]
    """
    if not isinstance(n, int):
        raise TypeError("O argumento deve ser um número inteiro")

    if n <= 1:
        raise ValueError("O número deve ser maior que 1")

    factors = []
    d = 2

    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1

    if n > 1:
        factors.append(n)

    return factors


def power_mod(base: int, exponent: int, modulus: int) -> int:
    """
    Calcula (base^exponent) mod modulus de forma eficiente.

    Utiliza exponenciação rápida para evitar overflow em números grandes.

    Args:
        base (int): Base da exponenciação.
        exponent (int): Expoente (deve ser não negativo).
        modulus (int): Módulo (deve ser positivo).

    Returns:
        int: Resultado de (base^exponent) mod modulus.

    Examples:
        >>> power_mod(2, 10, 1000)
        24
        >>> power_mod(3, 5, 7)
        5
    """
    if not all(isinstance(x, int) for x in [base, exponent, modulus]):
        raise TypeError("Todos os argumentos devem ser números inteiros")

    if exponent < 0:
        raise ValueError("O expoente deve ser não negativo")

    if modulus <= 0:
        raise ValueError("O módulo deve ser positivo")

    result = 1
    base = base % modulus

    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent = exponent >> 1
        base = (base * base) % modulus

    return result


def validate_number_list(numbers: List[Union[int, float]]) -> bool:
    """
    Valida se uma lista contém apenas números válidos.

    Args:
        numbers: Lista a ser validada.

    Returns:
        bool: True se a lista for válida, False caso contrário.
    """
    if not isinstance(numbers, list):
        return False

    if not numbers:
        return False

    return all(isinstance(num, (int, float)) and not math.isnan(num) and math.isfinite(num)
               for num in numbers)