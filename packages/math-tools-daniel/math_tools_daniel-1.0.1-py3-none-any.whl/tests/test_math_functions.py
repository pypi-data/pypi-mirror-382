"""
Testes unitários para as funções matemáticas básicas.
"""

import pytest
import sys
import os

# Adiciona o diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math_tools_daniel.utils.math_functions import factorial, is_prime, average, fibonacci


class TestFactorial:
    """Testes para a função factorial."""
    
    def test_factorial_zero(self):
        """Testa fatorial de 0."""
        assert factorial(0) == 1
    
    def test_factorial_one(self):
        """Testa fatorial de 1."""
        assert factorial(1) == 1
    
    def test_factorial_positive(self):
        """Testa fatorial de números positivos."""
        assert factorial(5) == 120
        assert factorial(3) == 6
        assert factorial(4) == 24
        assert factorial(6) == 720
    
    def test_factorial_negative(self):
        """Testa que fatorial de número negativo levanta ValueError."""
        with pytest.raises(ValueError):
            factorial(-1)
        with pytest.raises(ValueError):
            factorial(-5)
    
    def test_factorial_non_integer(self):
        """Testa que fatorial de não-inteiro levanta TypeError."""
        with pytest.raises(TypeError):
            factorial(3.5)
        with pytest.raises(TypeError):
            factorial("5")
        with pytest.raises(TypeError):
            factorial([5])


class TestIsPrime:
    """Testes para a função is_prime."""
    
    def test_is_prime_small_primes(self):
        """Testa números primos pequenos."""
        assert is_prime(2) == True
        assert is_prime(3) == True
        assert is_prime(5) == True
        assert is_prime(7) == True
        assert is_prime(11) == True
        assert is_prime(13) == True
        assert is_prime(17) == True
        assert is_prime(19) == True
    
    def test_is_prime_small_composites(self):
        """Testa números compostos pequenos."""
        assert is_prime(4) == False
        assert is_prime(6) == False
        assert is_prime(8) == False
        assert is_prime(9) == False
        assert is_prime(10) == False
        assert is_prime(12) == False
        assert is_prime(14) == False
        assert is_prime(15) == False
    
    def test_is_prime_edge_cases(self):
        """Testa casos extremos."""
        assert is_prime(0) == False
        assert is_prime(1) == False
        assert is_prime(-1) == False
        assert is_prime(-5) == False
    
    def test_is_prime_large_numbers(self):
        """Testa números grandes."""
        assert is_prime(97) == True
        assert is_prime(101) == True
        assert is_prime(100) == False
        assert is_prime(121) == False  # 11²
    
    def test_is_prime_non_integer(self):
        """Testa que não-inteiro levanta TypeError."""
        with pytest.raises(TypeError):
            is_prime(3.5)
        with pytest.raises(TypeError):
            is_prime("7")


class TestAverage:
    """Testes para a função average."""
    
    def test_average_integers(self):
        """Testa média de inteiros."""
        assert average([1, 2, 3, 4, 5]) == 3.0
        assert average([10, 20, 30]) == 20.0
        assert average([1]) == 1.0
        assert average([0, 0, 0]) == 0.0
    
    def test_average_floats(self):
        """Testa média de números decimais."""
        assert average([1.5, 2.5, 3.5]) == 2.5
        assert average([0.1, 0.2, 0.3]) == pytest.approx(0.2, rel=1e-9)
    
    def test_average_mixed(self):
        """Testa média de números mistos."""
        assert average([1, 2.5, 3, 4.5]) == 2.75
    
    def test_average_negative(self):
        """Testa média com números negativos."""
        assert average([-1, -2, -3]) == -2.0
        assert average([-5, 0, 5]) == 0.0
    
    def test_average_empty_list(self):
        """Testa que lista vazia levanta ValueError."""
        with pytest.raises(ValueError):
            average([])
    
    def test_average_non_list(self):
        """Testa que não-lista levanta TypeError."""
        with pytest.raises(TypeError):
            average("123")
        with pytest.raises(TypeError):
            average(123)
    
    def test_average_non_numeric(self):
        """Testa que elementos não-numéricos levantam TypeError."""
        with pytest.raises(TypeError):
            average([1, 2, "3"])
        with pytest.raises(TypeError):
            average([1, 2, None])


class TestFibonacci:
    """Testes para a função fibonacci."""
    
    def test_fibonacci_base_cases(self):
        """Testa casos base de Fibonacci."""
        assert fibonacci(0) == 0
        assert fibonacci(1) == 1
    
    def test_fibonacci_small_numbers(self):
        """Testa números pequenos de Fibonacci."""
        assert fibonacci(2) == 1
        assert fibonacci(3) == 2
        assert fibonacci(4) == 3
        assert fibonacci(5) == 5
        assert fibonacci(6) == 8
        assert fibonacci(7) == 13
        assert fibonacci(8) == 21
    
    def test_fibonacci_larger_numbers(self):
        """Testa números maiores de Fibonacci."""
        assert fibonacci(10) == 55
        assert fibonacci(15) == 610
        assert fibonacci(20) == 6765
    
    def test_fibonacci_negative(self):
        """Testa que número negativo levanta ValueError."""
        with pytest.raises(ValueError):
            fibonacci(-1)
        with pytest.raises(ValueError):
            fibonacci(-10)
    
    def test_fibonacci_non_integer(self):
        """Testa que não-inteiro levanta TypeError."""
        with pytest.raises(TypeError):
            fibonacci(3.5)
        with pytest.raises(TypeError):
            fibonacci("5")


if __name__ == "__main__":
    pytest.main([__file__])
