"""
Testes unitários para as funções estatísticas.
"""

import pytest
import sys
import os

# Adiciona o diretório pai ao path para importar o módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from math_tools_daniel.processing.statistics import (
    median, mode, standard_deviation, variance, quartiles
)


class TestMedian:
    """Testes para a função median."""
    
    def test_median_odd_length(self):
        """Testa mediana de lista com número ímpar de elementos."""
        assert median([1, 2, 3, 4, 5]) == 3.0
        assert median([7, 1, 9]) == 7.0
        assert median([5]) == 5.0
    
    def test_median_even_length(self):
        """Testa mediana de lista com número par de elementos."""
        assert median([1, 2, 3, 4]) == 2.5
        assert median([1, 3]) == 2.0
        assert median([10, 20, 30, 40]) == 25.0
    
    def test_median_unsorted(self):
        """Testa mediana de lista não ordenada."""
        assert median([3, 1, 4, 1, 5]) == 3.0
        assert median([6, 2, 8, 4]) == 5.0
    
    def test_median_with_duplicates(self):
        """Testa mediana com valores duplicados."""
        assert median([1, 1, 1, 1]) == 1.0
        assert median([1, 2, 2, 3]) == 2.0
    
    def test_median_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(ValueError):
            median([])
        with pytest.raises(TypeError):
            median("123")
        with pytest.raises(TypeError):
            median([1, 2, "3"])


class TestMode:
    """Testes para a função mode."""
    
    def test_mode_single(self):
        """Testa moda única."""
        assert mode([1, 2, 2, 3, 4]) == [2]
        assert mode([5, 5, 5, 1, 2]) == [5]
    
    def test_mode_multiple(self):
        """Testa múltiplas modas."""
        result = mode([1, 1, 2, 2, 3])
        assert set(result) == {1, 2}
        assert len(result) == 2
    
    def test_mode_all_same_frequency(self):
        """Testa quando todos têm a mesma frequência."""
        result = mode([1, 2, 3, 4])
        assert set(result) == {1, 2, 3, 4}
    
    def test_mode_single_element(self):
        """Testa lista com um elemento."""
        assert mode([5]) == [5]
    
    def test_mode_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(ValueError):
            mode([])
        with pytest.raises(TypeError):
            mode("123")
        with pytest.raises(TypeError):
            mode([1, 2, "3"])


class TestStandardDeviation:
    """Testes para a função standard_deviation."""
    
    def test_standard_deviation_sample(self):
        """Testa desvio padrão amostral."""
        # Teste com valores conhecidos
        data = [1, 2, 3, 4, 5]
        result = standard_deviation(data, sample=True)
        assert pytest.approx(result, rel=1e-2) == 1.58
    
    def test_standard_deviation_population(self):
        """Testa desvio padrão populacional."""
        data = [1, 2, 3, 4, 5]
        result = standard_deviation(data, sample=False)
        assert pytest.approx(result, rel=1e-2) == 1.41
    
    def test_standard_deviation_identical_values(self):
        """Testa desvio padrão de valores idênticos."""
        assert standard_deviation([5, 5, 5, 5]) == 0.0
    
    def test_standard_deviation_two_values(self):
        """Testa desvio padrão com dois valores."""
        result = standard_deviation([1, 3], sample=True)
        assert pytest.approx(result, rel=1e-9) == 1.414213562373095
    
    def test_standard_deviation_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(ValueError):
            standard_deviation([])
        with pytest.raises(ValueError):
            standard_deviation([5], sample=True)  # Apenas um valor para amostra
        with pytest.raises(TypeError):
            standard_deviation([1, 2, "3"])


class TestVariance:
    """Testes para a função variance."""
    
    def test_variance_sample(self):
        """Testa variância amostral."""
        data = [1, 2, 3, 4, 5]
        result = variance(data, sample=True)
        assert pytest.approx(result, rel=1e-2) == 2.5
    
    def test_variance_population(self):
        """Testa variância populacional."""
        data = [1, 2, 3, 4, 5]
        result = variance(data, sample=False)
        assert pytest.approx(result, rel=1e-2) == 2.0
    
    def test_variance_identical_values(self):
        """Testa variância de valores idênticos."""
        assert variance([5, 5, 5, 5]) == 0.0


class TestQuartiles:
    """Testes para a função quartiles."""
    
    def test_quartiles_basic(self):
        """Testa quartis básicos."""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        q1, q2, q3 = quartiles(data)
        assert q1 == 2.5  # Mediana de [1, 2, 3, 4]
        assert q2 == 5.0  # Mediana de [1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert q3 == 7.5  # Mediana de [6, 7, 8, 9]
    
    def test_quartiles_even_length(self):
        """Testa quartis com número par de elementos."""
        data = [1, 2, 3, 4, 5, 6, 7, 8]
        q1, q2, q3 = quartiles(data)
        assert q1 == 2.5
        assert q2 == 4.5
        assert q3 == 6.5
    
    def test_quartiles_unsorted(self):
        """Testa quartis com dados não ordenados."""
        data = [9, 1, 5, 3, 7, 2, 8, 4, 6]
        q1, q2, q3 = quartiles(data)
        assert q1 == 2.5  # Mediana de [1, 2, 3, 4] após ordenação
        assert q2 == 5.0  # Mediana de [1, 2, 3, 4, 5, 6, 7, 8, 9]
        assert q3 == 7.5  # Mediana de [6, 7, 8, 9]
    
    def test_quartiles_invalid_input(self):
        """Testa entradas inválidas."""
        with pytest.raises(ValueError):
            quartiles([1, 2, 3])  # Menos de 4 elementos
        with pytest.raises(TypeError):
            quartiles("123456")
        with pytest.raises(TypeError):
            quartiles([1, 2, 3, "4"])


if __name__ == "__main__":
    pytest.main([__file__])
