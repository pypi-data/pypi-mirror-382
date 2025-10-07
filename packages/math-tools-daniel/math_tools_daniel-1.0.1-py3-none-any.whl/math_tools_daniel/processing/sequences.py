"""
Módulo de processamento de sequências matemáticas.

Este módulo contém funções para gerar e analisar sequências matemáticas.

Autor: Daniel Santos
Versão: 1.0.0
"""

from typing import List, Union
import math


def fibonacci_sequence(n: int) -> List[int]:
    """
    Gera uma sequência de Fibonacci com n termos.

    Args:
        n (int): Número de termos da sequência.

    Returns:
        List[int]: Lista com os n primeiros números de Fibonacci.

    Examples:
        >>> fibonacci_sequence(5)
        [0, 1, 1, 2, 3]
        >>> fibonacci_sequence(8)
        [0, 1, 1, 2, 3, 5, 8, 13]
    """
    if not isinstance(n, int):
        raise TypeError("O argumento deve ser um número inteiro")

    if n <= 0:
        return []

    if n == 1:
        return [0]

    sequence = [0, 1]
    for i in range(2, n):
        sequence.append(sequence[i-1] + sequence[i-2])

    return sequence


def prime_sequence(n: int) -> List[int]:
    """
    Gera uma sequência com os n primeiros números primos.

    Args:
        n (int): Número de primos a gerar.

    Returns:
        List[int]: Lista com os n primeiros números primos.

    Examples:
        >>> prime_sequence(5)
        [2, 3, 5, 7, 11]
        >>> prime_sequence(3)
        [2, 3, 5]
    """
    if not isinstance(n, int):
        raise TypeError("O argumento deve ser um número inteiro")

    if n <= 0:
        return []

    primes = []
    candidate = 2

    while len(primes) < n:
        is_prime = True
        for prime in primes:
            if prime * prime > candidate:
                break
            if candidate % prime == 0:
                is_prime = False
                break

        if is_prime:
            primes.append(candidate)

        candidate += 1

    return primes


def arithmetic_sequence(start: Union[int, float], step: Union[int, float], n: int) -> List[Union[int, float]]:
    """
    Gera uma progressão aritmética.

    Args:
        start (Union[int, float]): Primeiro termo da sequência.
        step (Union[int, float]): Razão da progressão aritmética.
        n (int): Número de termos.

    Returns:
        List[Union[int, float]]: Lista com os termos da progressão aritmética.

    Examples:
        >>> arithmetic_sequence(1, 2, 5)
        [1, 3, 5, 7, 9]
        >>> arithmetic_sequence(0, 0.5, 4)
        [0, 0.5, 1.0, 1.5]
    """
    if not isinstance(n, int):
        raise TypeError("O número de termos deve ser um inteiro")

    if not isinstance(start, (int, float)) or not isinstance(step, (int, float)):
        raise TypeError("O primeiro termo e a razão devem ser números")

    if n <= 0:
        return []

    return [start + i * step for i in range(n)]


def geometric_sequence(start: Union[int, float], ratio: Union[int, float], n: int) -> List[Union[int, float]]:
    """
    Gera uma progressão geométrica.

    Args:
        start (Union[int, float]): Primeiro termo da sequência.
        ratio (Union[int, float]): Razão da progressão geométrica.
        n (int): Número de termos.

    Returns:
        List[Union[int, float]]: Lista com os termos da progressão geométrica.

    Examples:
        >>> geometric_sequence(1, 2, 5)
        [1, 2, 4, 8, 16]
        >>> geometric_sequence(3, 0.5, 4)
        [3, 1.5, 0.75, 0.375]
    """
    if not isinstance(n, int):
        raise TypeError("O número de termos deve ser um inteiro")

    if not isinstance(start, (int, float)) or not isinstance(ratio, (int, float)):
        raise TypeError("O primeiro termo e a razão devem ser números")

    if n <= 0:
        return []

    sequence = []
    current = start

    for _ in range(n):
        sequence.append(current)
        current *= ratio

    return sequence


def factorial_sequence(n: int) -> List[int]:
    """
    Gera uma sequência com os fatoriais de 0 até n.

    Args:
        n (int): Último número para calcular o fatorial.

    Returns:
        List[int]: Lista com os fatoriais de 0! até n!.

    Examples:
        >>> factorial_sequence(4)
        [1, 1, 2, 6, 24]
        >>> factorial_sequence(2)
        [1, 1, 2]
    """
    if not isinstance(n, int):
        raise TypeError("O argumento deve ser um número inteiro")

    if n < 0:
        raise ValueError("O argumento deve ser não negativo")

    factorials = []
    current_factorial = 1

    for i in range(n + 1):
        if i == 0:
            factorials.append(1)
        else:
            current_factorial *= i
            factorials.append(current_factorial)

    return factorials


def collatz_sequence(n: int) -> List[int]:
    """
    Gera a sequência de Collatz (3n+1) para um número.

    A conjectura de Collatz afirma que esta sequência sempre chega a 1.

    Args:
        n (int): Número inicial (deve ser positivo).

    Returns:
        List[int]: Sequência de Collatz até chegar a 1.

    Examples:
        >>> collatz_sequence(5)
        [5, 16, 8, 4, 2, 1]
        >>> collatz_sequence(3)
        [3, 10, 5, 16, 8, 4, 2, 1]
    """
    if not isinstance(n, int):
        raise TypeError("O argumento deve ser um número inteiro")

    if n <= 0:
        raise ValueError("O argumento deve ser positivo")

    sequence = []
    current = n

    while current != 1:
        sequence.append(current)
        if current % 2 == 0:
            current = current // 2
        else:
            current = 3 * current + 1

    sequence.append(1)
    return sequence