"""
Testes unitários para as funções auxiliares matemáticas.
"""

import pytest
import sys
import os

# Adiciona o diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math_tools_daniel.utils.math_helpers import (
    is_perfect_number, gcd, lcm, prime_factors, power_mod, validate_number_list
)


class TestIsPerfectNumber:
    """Testes para a função is_perfect_number."""
    
    def test_perfect_numbers(self):
        """Testa números perfeitos conhecidos."""
        assert is_perfect_number(6) == True   # 1 + 2 + 3 = 6
        assert is_perfect_number(28) == True  # 1 + 2 + 4 + 7 + 14 = 28
        assert is_perfect_number(496) == True
    
    def test_non_perfect_numbers(self):
        """Testa números que não são perfeitos."""
        assert is_perfect_number(1) == False
        assert is_perfect_number(8) == False
        assert is_perfect_number(12) == False
        assert is_perfect_number(100) == False
    
    def test_edge_cases(self):
        """Testa casos extremos."""
        assert is_perfect_number(0) == False
        assert is_perfect_number(-6) == False


class TestGCD:
    """Testes para a função gcd (Máximo Divisor Comum)."""
    
    def test_gcd_basic(self):
        """Testa casos básicos de MDC."""
        assert gcd(48, 18) == 6
        assert gcd(17, 13) == 1
        assert gcd(100, 25) == 25
        assert gcd(12, 8) == 4
    
    def test_gcd_same_numbers(self):
        """Testa MDC de números iguais."""
        assert gcd(5, 5) == 5
        assert gcd(100, 100) == 100
    
    def test_gcd_with_zero(self):
        """Testa MDC com zero."""
        assert gcd(5, 0) == 5
        assert gcd(0, 7) == 7
        assert gcd(0, 0) == 0
    
    def test_gcd_negative(self):
        """Testa MDC com números negativos."""
        assert gcd(-48, 18) == 6
        assert gcd(48, -18) == 6
        assert gcd(-48, -18) == 6
    
    def test_gcd_non_integer(self):
        """Testa que não-inteiros levantam TypeError."""
        with pytest.raises(TypeError):
            gcd(3.5, 2)
        with pytest.raises(TypeError):
            gcd("5", 3)


class TestLCM:
    """Testes para a função lcm (Mínimo Múltiplo Comum)."""
    
    def test_lcm_basic(self):
        """Testa casos básicos de MMC."""
        assert lcm(4, 6) == 12
        assert lcm(3, 7) == 21
        assert lcm(12, 8) == 24
    
    def test_lcm_same_numbers(self):
        """Testa MMC de números iguais."""
        assert lcm(5, 5) == 5
        assert lcm(100, 100) == 100
    
    def test_lcm_with_zero(self):
        """Testa MMC com zero."""
        assert lcm(5, 0) == 0
        assert lcm(0, 7) == 0
    
    def test_lcm_coprime(self):
        """Testa MMC de números coprimos."""
        assert lcm(7, 11) == 77
        assert lcm(13, 17) == 221


class TestPrimeFactors:
    """Testes para a função prime_factors."""
    
    def test_prime_factors_basic(self):
        """Testa fatoração básica."""
        assert prime_factors(12) == [2, 2, 3]
        assert prime_factors(60) == [2, 2, 3, 5]
        assert prime_factors(100) == [2, 2, 5, 5]
    
    def test_prime_factors_prime_number(self):
        """Testa fatoração de números primos."""
        assert prime_factors(17) == [17]
        assert prime_factors(23) == [23]
        assert prime_factors(2) == [2]
    
    def test_prime_factors_power_of_prime(self):
        """Testa fatoração de potências de primos."""
        assert prime_factors(8) == [2, 2, 2]  # 2³
        assert prime_factors(27) == [3, 3, 3]  # 3³
        assert prime_factors(25) == [5, 5]     # 5²
    
    def test_prime_factors_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(ValueError):
            prime_factors(1)
        with pytest.raises(ValueError):
            prime_factors(0)
        with pytest.raises(ValueError):
            prime_factors(-5)
        with pytest.raises(TypeError):
            prime_factors(3.5)


class TestPowerMod:
    """Testes para a função power_mod."""
    
    def test_power_mod_basic(self):
        """Testa exponenciação modular básica."""
        assert power_mod(2, 10, 1000) == 24  # 2^10 mod 1000 = 1024 mod 1000 = 24
        assert power_mod(3, 5, 7) == 5       # 3^5 mod 7 = 243 mod 7 = 5
        assert power_mod(5, 3, 13) == 8      # 5^3 mod 13 = 125 mod 13 = 8
    
    def test_power_mod_zero_exponent(self):
        """Testa com expoente zero."""
        assert power_mod(5, 0, 7) == 1
        assert power_mod(100, 0, 3) == 1
    
    def test_power_mod_one_exponent(self):
        """Testa com expoente um."""
        assert power_mod(5, 1, 7) == 5
        assert power_mod(10, 1, 3) == 1  # 10 mod 3 = 1
    
    def test_power_mod_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(ValueError):
            power_mod(2, -1, 5)  # Expoente negativo
        with pytest.raises(ValueError):
            power_mod(2, 3, 0)   # Módulo zero
        with pytest.raises(ValueError):
            power_mod(2, 3, -5)  # Módulo negativo
        with pytest.raises(TypeError):
            power_mod(2.5, 3, 5)  # Base não-inteira


class TestValidateNumberList:
    """Testes para a função validate_number_list."""
    
    def test_valid_lists(self):
        """Testa listas válidas."""
        assert validate_number_list([1, 2, 3]) == True
        assert validate_number_list([1.5, 2.5, 3.5]) == True
        assert validate_number_list([1, 2.5, 3]) == True
        assert validate_number_list([-1, 0, 1]) == True
    
    def test_invalid_lists(self):
        """Testa listas inválidas."""
        assert validate_number_list([]) == False  # Lista vazia
        assert validate_number_list([1, 2, "3"]) == False  # String
        assert validate_number_list([1, 2, None]) == False  # None
        assert validate_number_list([1, 2, [3]]) == False  # Lista aninhada
    
    def test_non_list_input(self):
        """Testa entrada que não é lista."""
        assert validate_number_list("123") == False
        assert validate_number_list(123) == False
        assert validate_number_list(None) == False
    
    def test_special_float_values(self):
        """Testa valores especiais de float."""
        import math
        assert validate_number_list([1, 2, float('inf')]) == False  # Infinito
        assert validate_number_list([1, 2, float('nan')]) == False  # NaN


if __name__ == "__main__":
    pytest.main([__file__])
