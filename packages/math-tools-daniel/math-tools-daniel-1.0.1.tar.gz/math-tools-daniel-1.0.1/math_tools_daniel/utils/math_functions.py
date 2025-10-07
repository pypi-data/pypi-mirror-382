"""
Módulo de funções matemáticas básicas.

Este módulo contém implementações de funções matemáticas fundamentais
incluindo fatorial, verificação de números primos, média e sequência de Fibonacci.

Autor: Daniel Santos
Versão: 1.0.0
"""

from typing import List, Union


def factorial(n: int) -> int:
    """
    Calcula o fatorial de um número inteiro não negativo.

    O fatorial de n (n!) é o produto de todos os números inteiros positivos
    menores ou iguais a n. Por definição, 0! = 1.

    Args:
        n (int): Número inteiro não negativo para calcular o fatorial.

    Returns:
        int: O fatorial de n.

    Raises:
        ValueError: Se n for negativo.
        TypeError: Se n não for um inteiro.

    Examples:
        >>> factorial(5)
        120
        >>> factorial(0)
        1
        >>> factorial(3)
        6
    """
    if not isinstance(n, int):
        raise TypeError("O argumento deve ser um número inteiro")

    if n < 0:
        raise ValueError("O fatorial não está definido para números negativos")

    if n == 0 or n == 1:
        return 1

    result = 1
    for i in range(2, n + 1):
        result *= i

    return result


def is_prime(n: int) -> bool:
    """
    Verifica se um número é primo.

    Um número primo é um número natural maior que 1 que não possui
    divisores positivos além de 1 e ele mesmo.

    Args:
        n (int): Número inteiro a ser verificado.

    Returns:
        bool: True se o número for primo, False caso contrário.

    Raises:
        TypeError: Se n não for um inteiro.

    Examples:
        >>> is_prime(7)
        True
        >>> is_prime(4)
        False
        >>> is_prime(2)
        True
        >>> is_prime(1)
        False
    """
    if not isinstance(n, int):
        raise TypeError("O argumento deve ser um número inteiro")

    if n < 2:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    # Verifica divisores ímpares até a raiz quadrada de n
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False

    return True


def average(numbers: List[Union[int, float]]) -> float:
    """
    Calcula a média aritmética de uma lista de números.

    A média aritmética é a soma de todos os valores dividida
    pela quantidade de valores.

    Args:
        numbers (List[Union[int, float]]): Lista de números para calcular a média.

    Returns:
        float: A média aritmética dos números.

    Raises:
        ValueError: Se a lista estiver vazia.
        TypeError: Se algum elemento da lista não for um número.

    Examples:
        >>> average([1, 2, 3, 4, 5])
        3.0
        >>> average([10, 20, 30])
        20.0
        >>> average([1.5, 2.5, 3.5])
        2.5
    """
    if not isinstance(numbers, list):
        raise TypeError("O argumento deve ser uma lista")

    if not numbers:
        raise ValueError("A lista não pode estar vazia")

    # Verifica se todos os elementos são números
    for num in numbers:
        if not isinstance(num, (int, float)):
            raise TypeError("Todos os elementos da lista devem ser números")

    return sum(numbers) / len(numbers)


def fibonacci(n: int) -> int:
    """
    Calcula o n-ésimo número da sequência de Fibonacci.

    A sequência de Fibonacci é definida como:
    F(0) = 0, F(1) = 1, F(n) = F(n-1) + F(n-2) para n > 1

    Args:
        n (int): Posição na sequência de Fibonacci (começando em 0).

    Returns:
        int: O n-ésimo número de Fibonacci.

    Raises:
        ValueError: Se n for negativo.
        TypeError: Se n não for um inteiro.

    Examples:
        >>> fibonacci(0)
        0
        >>> fibonacci(1)
        1
        >>> fibonacci(5)
        5
        >>> fibonacci(10)
        55
    """
    if not isinstance(n, int):
        raise TypeError("O argumento deve ser um número inteiro")

    if n < 0:
        raise ValueError("A posição na sequência de Fibonacci deve ser não negativa")

    if n == 0:
        return 0
    elif n == 1:
        return 1

    # Implementação iterativa para eficiência
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b

    return b