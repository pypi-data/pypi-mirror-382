"""
Testes unitários para as funções de sequências matemáticas.
"""

import pytest
import sys
import os

# Adiciona o diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math_tools_daniel.processing.sequences import (
    fibonacci_sequence, prime_sequence, arithmetic_sequence,
    geometric_sequence, factorial_sequence, collatz_sequence
)


class TestFibonacciSequence:
    """Testes para a função fibonacci_sequence."""
    
    def test_fibonacci_sequence_basic(self):
        """Testa sequência básica de Fibonacci."""
        assert fibonacci_sequence(5) == [0, 1, 1, 2, 3]
        assert fibonacci_sequence(8) == [0, 1, 1, 2, 3, 5, 8, 13]
        assert fibonacci_sequence(1) == [0]
        assert fibonacci_sequence(2) == [0, 1]
    
    def test_fibonacci_sequence_zero_or_negative(self):
        """Testa casos extremos."""
        assert fibonacci_sequence(0) == []
        assert fibonacci_sequence(-1) == []
    
    def test_fibonacci_sequence_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(TypeError):
            fibonacci_sequence(3.5)
        with pytest.raises(TypeError):
            fibonacci_sequence("5")


class TestPrimeSequence:
    """Testes para a função prime_sequence."""
    
    def test_prime_sequence_basic(self):
        """Testa sequência básica de primos."""
        assert prime_sequence(5) == [2, 3, 5, 7, 11]
        assert prime_sequence(3) == [2, 3, 5]
        assert prime_sequence(1) == [2]
    
    def test_prime_sequence_zero_or_negative(self):
        """Testa casos extremos."""
        assert prime_sequence(0) == []
        assert prime_sequence(-1) == []
    
    def test_prime_sequence_larger(self):
        """Testa sequência maior de primos."""
        result = prime_sequence(10)
        expected = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
        assert result == expected
    
    def test_prime_sequence_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(TypeError):
            prime_sequence(3.5)


class TestArithmeticSequence:
    """Testes para a função arithmetic_sequence."""
    
    def test_arithmetic_sequence_basic(self):
        """Testa progressão aritmética básica."""
        assert arithmetic_sequence(1, 2, 5) == [1, 3, 5, 7, 9]
        assert arithmetic_sequence(0, 0.5, 4) == [0, 0.5, 1.0, 1.5]
        assert arithmetic_sequence(10, -2, 3) == [10, 8, 6]
    
    def test_arithmetic_sequence_zero_step(self):
        """Testa progressão com razão zero."""
        assert arithmetic_sequence(5, 0, 4) == [5, 5, 5, 5]
    
    def test_arithmetic_sequence_zero_or_negative_n(self):
        """Testa casos extremos."""
        assert arithmetic_sequence(1, 2, 0) == []
        assert arithmetic_sequence(1, 2, -1) == []
    
    def test_arithmetic_sequence_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(TypeError):
            arithmetic_sequence("1", 2, 5)
        with pytest.raises(TypeError):
            arithmetic_sequence(1, 2, 3.5)


class TestGeometricSequence:
    """Testes para a função geometric_sequence."""
    
    def test_geometric_sequence_basic(self):
        """Testa progressão geométrica básica."""
        assert geometric_sequence(1, 2, 5) == [1, 2, 4, 8, 16]
        assert geometric_sequence(3, 0.5, 4) == [3, 1.5, 0.75, 0.375]
        assert geometric_sequence(2, 3, 3) == [2, 6, 18]
    
    def test_geometric_sequence_ratio_one(self):
        """Testa progressão com razão 1."""
        assert geometric_sequence(5, 1, 4) == [5, 5, 5, 5]
    
    def test_geometric_sequence_ratio_zero(self):
        """Testa progressão com razão 0."""
        assert geometric_sequence(5, 0, 4) == [5, 0, 0, 0]
    
    def test_geometric_sequence_zero_or_negative_n(self):
        """Testa casos extremos."""
        assert geometric_sequence(1, 2, 0) == []
        assert geometric_sequence(1, 2, -1) == []
    
    def test_geometric_sequence_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(TypeError):
            geometric_sequence("1", 2, 5)
        with pytest.raises(TypeError):
            geometric_sequence(1, 2, 3.5)


class TestFactorialSequence:
    """Testes para a função factorial_sequence."""
    
    def test_factorial_sequence_basic(self):
        """Testa sequência básica de fatoriais."""
        assert factorial_sequence(4) == [1, 1, 2, 6, 24]
        assert factorial_sequence(2) == [1, 1, 2]
        assert factorial_sequence(0) == [1]
    
    def test_factorial_sequence_larger(self):
        """Testa sequência maior de fatoriais."""
        result = factorial_sequence(6)
        expected = [1, 1, 2, 6, 24, 120, 720]
        assert result == expected
    
    def test_factorial_sequence_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(ValueError):
            factorial_sequence(-1)
        with pytest.raises(TypeError):
            factorial_sequence(3.5)


class TestCollatzSequence:
    """Testes para a função collatz_sequence."""
    
    def test_collatz_sequence_basic(self):
        """Testa sequência básica de Collatz."""
        assert collatz_sequence(1) == [1]
        assert collatz_sequence(2) == [2, 1]
        assert collatz_sequence(3) == [3, 10, 5, 16, 8, 4, 2, 1]
        assert collatz_sequence(5) == [5, 16, 8, 4, 2, 1]
    
    def test_collatz_sequence_power_of_two(self):
        """Testa sequência para potências de 2."""
        assert collatz_sequence(4) == [4, 2, 1]
        assert collatz_sequence(8) == [8, 4, 2, 1]
        assert collatz_sequence(16) == [16, 8, 4, 2, 1]
    
    def test_collatz_sequence_larger_number(self):
        """Testa sequência para número maior."""
        result = collatz_sequence(7)
        expected = [7, 22, 11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]
        assert result == expected
    
    def test_collatz_sequence_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(ValueError):
            collatz_sequence(0)
        with pytest.raises(ValueError):
            collatz_sequence(-5)
        with pytest.raises(TypeError):
            collatz_sequence(3.5)


if __name__ == "__main__":
    pytest.main([__file__])
