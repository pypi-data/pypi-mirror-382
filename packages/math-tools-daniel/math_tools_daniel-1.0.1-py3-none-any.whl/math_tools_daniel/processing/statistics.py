"""
Módulo de processamento estatístico.

Este módulo contém funções para análise estatística de dados numéricos.

Autor: Daniel Santos
Versão: 1.0.0
"""

from typing import List, Union, Tuple
import math


def median(numbers: List[Union[int, float]]) -> float:
    """
    Calcula a mediana de uma lista de números.

    A mediana é o valor que separa a metade maior da metade menor
    de uma amostra de dados.

    Args:
        numbers (List[Union[int, float]]): Lista de números.

    Returns:
        float: A mediana dos números.

    Raises:
        ValueError: Se a lista estiver vazia.
        TypeError: Se algum elemento não for um número.

    Examples:
        >>> median([1, 2, 3, 4, 5])
        3.0
        >>> median([1, 2, 3, 4])
        2.5
    """
    if not isinstance(numbers, list):
        raise TypeError("O argumento deve ser uma lista")

    if not numbers:
        raise ValueError("A lista não pode estar vazia")

    for num in numbers:
        if not isinstance(num, (int, float)):
            raise TypeError("Todos os elementos devem ser números")

    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)

    if n % 2 == 0:
        # Se o número de elementos for par, a mediana é a média dos dois elementos centrais
        return (sorted_numbers[n // 2 - 1] + sorted_numbers[n // 2]) / 2
    else:
        # Se o número de elementos for ímpar, a mediana é o elemento central
        return float(sorted_numbers[n // 2])


def mode(numbers: List[Union[int, float]]) -> List[Union[int, float]]:
    """
    Calcula a moda de uma lista de números.

    A moda é o valor que aparece com maior frequência na amostra.
    Pode haver múltiplas modas.

    Args:
        numbers (List[Union[int, float]]): Lista de números.

    Returns:
        List[Union[int, float]]: Lista com os valores da moda.

    Raises:
        ValueError: Se a lista estiver vazia.
        TypeError: Se algum elemento não for um número.

    Examples:
        >>> mode([1, 2, 2, 3, 4])
        [2]
        >>> mode([1, 1, 2, 2, 3])
        [1, 2]
    """
    if not isinstance(numbers, list):
        raise TypeError("O argumento deve ser uma lista")

    if not numbers:
        raise ValueError("A lista não pode estar vazia")

    for num in numbers:
        if not isinstance(num, (int, float)):
            raise TypeError("Todos os elementos devem ser números")

    # Conta a frequência de cada número
    frequency = {}
    for num in numbers:
        frequency[num] = frequency.get(num, 0) + 1

    # Encontra a frequência máxima
    max_frequency = max(frequency.values())

    # Retorna todos os números com frequência máxima
    return [num for num, freq in frequency.items() if freq == max_frequency]


def standard_deviation(numbers: List[Union[int, float]], sample: bool = True) -> float:
    """
    Calcula o desvio padrão de uma lista de números.

    Args:
        numbers (List[Union[int, float]]): Lista de números.
        sample (bool): Se True, calcula o desvio padrão amostral (n-1).
                      Se False, calcula o desvio padrão populacional (n).

    Returns:
        float: O desvio padrão.

    Raises:
        ValueError: Se a lista estiver vazia ou tiver apenas um elemento (para amostra).
        TypeError: Se algum elemento não for um número.

    Examples:
        >>> round(standard_deviation([1, 2, 3, 4, 5]), 2)
        1.58
    """
    if not isinstance(numbers, list):
        raise TypeError("O argumento deve ser uma lista")

    if not numbers:
        raise ValueError("A lista não pode estar vazia")

    if sample and len(numbers) < 2:
        raise ValueError("Para desvio padrão amostral, são necessários pelo menos 2 valores")

    for num in numbers:
        if not isinstance(num, (int, float)):
            raise TypeError("Todos os elementos devem ser números")

    mean = sum(numbers) / len(numbers)
    variance = sum((x - mean) ** 2 for x in numbers)

    if sample:
        variance /= (len(numbers) - 1)
    else:
        variance /= len(numbers)

    return math.sqrt(variance)


def variance(numbers: List[Union[int, float]], sample: bool = True) -> float:
    """
    Calcula a variância de uma lista de números.

    Args:
        numbers (List[Union[int, float]]): Lista de números.
        sample (bool): Se True, calcula a variância amostral (n-1).
                      Se False, calcula a variância populacional (n).

    Returns:
        float: A variância.

    Examples:
        >>> variance([1, 2, 3, 4, 5])
        2.5
    """
    return standard_deviation(numbers, sample) ** 2


def quartiles(numbers: List[Union[int, float]]) -> Tuple[float, float, float]:
    """
    Calcula os quartis de uma lista de números.

    Args:
        numbers (List[Union[int, float]]): Lista de números.

    Returns:
        Tuple[float, float, float]: Q1, Q2 (mediana), Q3.

    Examples:
        >>> quartiles([1, 2, 3, 4, 5, 6, 7, 8, 9])
        (3.0, 5.0, 7.0)
    """
    if not isinstance(numbers, list):
        raise TypeError("O argumento deve ser uma lista")

    if len(numbers) < 4:
        raise ValueError("São necessários pelo menos 4 valores para calcular quartis")

    for num in numbers:
        if not isinstance(num, (int, float)):
            raise TypeError("Todos os elementos devem ser números")

    sorted_numbers = sorted(numbers)
    n = len(sorted_numbers)

    q2 = median(sorted_numbers)

    # Calcula Q1 (mediana da metade inferior)
    lower_half = sorted_numbers[:n // 2]
    q1 = median(lower_half)

    # Calcula Q3 (mediana da metade superior)
    if n % 2 == 0:
        upper_half = sorted_numbers[n // 2:]
    else:
        upper_half = sorted_numbers[n // 2 + 1:]
    q3 = median(upper_half)

    return (q1, q2, q3)