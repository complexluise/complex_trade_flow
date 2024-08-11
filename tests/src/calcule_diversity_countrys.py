import pytest
import pandas as pd
import numpy as np
from src.constants import BACIColumnsTradeData

# Import the classes we want to test
from src.calcule_diversity_countries import TradeNetwork, DiversityCalculator, EconomicComplexityAnalyzer



@pytest.fixture
def mock_trade_data():
    data = {
        BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value: ['570210', '806740', '570210', '570210', '570210'],
        BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value: ['AFG', 'AUS', 'AUS', 'OZA', 'IND'],
        BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value: ['AUS', 'OZA', 'IND', 'IND', 'AUS'],
        BACIColumnsTradeData.MONEY.value: [1000.30, 1500.37, 70000.76, 523.05, 709.32]
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_region_data():
    return {
        "AFG": "South Asia",
        "IND": "South Asia",
        'AUS': 'East Asia & Pacific',
        'OZA': 'Sub-Saharan Africa'
    }

# Mock for _load_data method
@pytest.fixture
def mock_load_data(mock_trade_data, mock_region_data, monkeypatch):
    def mock_load_trade_data(*args, **kwargs):
        return mock_trade_data

    def mock_load_region_data(*args, **kwargs):
        return mock_region_data

    monkeypatch.setattr(TradeNetwork, '_load_data', mock_load_trade_data)
    monkeypatch.setattr(TradeNetwork, '_load_region_data', mock_load_region_data)


class TestTradeNetwork:
    def test_trade_network_initialization(self, mock_load_data):
        network = TradeNetwork(2022)
        assert network.year == 2022
        assert set(network.countries) == {'AFG', 'AUS', 'IND', 'OZA'}
        assert set(network.products) == {'570210', '806740'}
        assert network.trades_region_df.shape == (4, 4)

    def test__load_region_data(self):
        region_countries = TradeNetwork._load_region_data()
        assert isinstance(region_countries, dict)


class TestDiversityCalculator:

    def test_filter_data_by_trade_partners_country(self, mock_load_data):
        self.trade_network = TradeNetwork(2022)
        self.diversity_calculator = DiversityCalculator(self.trade_network)
        df = self.diversity_calculator.filter_data_by_country_partners()
        assert isinstance(df, pd.DataFrame)

    def test_filter_data_by_trade_partners_region(self, mock_load_data):
        self.trade_network = TradeNetwork(2022)
        self.diversity_calculator = DiversityCalculator(self.trade_network)
        countries_in_region = self.trade_network.find_countries_in_region('South Asia')
        other_countries = set(self.trade_network.countries).difference(set(countries_in_region))
        # aquí le debo pasar el conjunto de paises
        df = self.diversity_calculator.filter_data_by_country_partners(importers=countries_in_region,
                                                                       exporters=other_countries)
        assert isinstance(df, pd.DataFrame)

    def test_diversity_calculator(self, mock_load_data):
        network = TradeNetwork(2022)
        calculator = DiversityCalculator(network)

        # Test marginal probabilities
        probs = calculator.calculate_marginal_probabilities(BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value)
        expected_probs = np.array([0.979651530234438, 0.020348469765562063])  # Calculated manually
        np.testing.assert_allclose(probs, expected_probs, rtol=1e-5)

        # Test diversity index
        diversity = calculator.calculate_diversity_index()
        expected_diversity = 1.1044994155500054  # Calculated manually
        assert abs(diversity - expected_diversity) < 1e-4


# Test EconomicComplexityAnalyzer



@pytest.fixture()
def mock_load_region_data(mock_region_data, monkeypatch):
    def mock_load(*args, **kwargs):
        return mock_region_data

    monkeypatch.setattr(EconomicComplexityAnalyzer, '_load_region_data', mock_load)


def test_analyze_country(mock_load_data):
    trade_network = TradeNetwork(2022)
    analyzer = EconomicComplexityAnalyzer(2022, 2022)
    results = analyzer.analyze_country(trade_network, "AFG")

    assert len(results) == 4  # One row for each country
    assert set(results['country']) == {'AFG', 'AUS', 'OZA', 'IND'}
    assert set(results['region']) == {'South Asia', 'East Asia & Pacific', 'Sub-Saharan Africa'}

    # Check if diversity indices are calculated (exact values depend on the calculation method)
    assert all(results['export_product_diversity'] > 0)
    assert all(results['import_product_diversity'] > 0)


def test_analyze_region(mock_load_data):
    trade_network = TradeNetwork(2022)
    analyzer = EconomicComplexityAnalyzer(2022, 2022)
    results = analyzer.analyze_region(trade_network, "South Asia")

    assert len(results) == 4  # One row for each country
    assert set(results['country']) == {'AFG', 'AUS', 'OZA', 'IND'}
    assert set(results['region']) == {'South Asia', 'East Asia & Pacific', 'Sub-Saharan Africa'}

    # Check if diversity indices are calculated (exact values depend on the calculation method)
    assert all(results['export_product_diversity'] > 0)
    assert all(results['import_product_diversity'] > 0)


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
