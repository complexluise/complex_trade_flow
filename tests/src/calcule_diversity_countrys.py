import pytest
import pandas as pd
import numpy as np
from src.constants import BACIColumnsTradeData

# Import the classes we want to test
from src.calcule_diversity_countries import TradeNetwork, DiversityCalculator, EconomicComplexityAnalyzer, \
    ClassificationScheme


@pytest.fixture
def mock_trade_data():
    data = {
        BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value: ['570210', '806740', '570210', '570210', '570210'],
        BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value: ['AFG', 'AUS', 'AUS', 'OZA', 'IND'],
        BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value: ['AUS', 'OZA', 'IND', 'IND', 'AUS'],
        BACIColumnsTradeData.MONEY.value: [1000.30, 1500.37, 70000.76, 523.05, 709.32]
    }
    return pd.DataFrame(data)


# Mock for _load_data method
@pytest.fixture
def mock_load_data(mock_trade_data, monkeypatch):
    def mock_load_trade_data(*args, **kwargs):
        return mock_trade_data

    monkeypatch.setattr(TradeNetwork, '_load_data', mock_load_trade_data)

    no_classification = ClassificationScheme(
        name="by_country"
    )
    return TradeNetwork(2022, [no_classification])


def test_trade_network_initialization(mock_load_data):
    trade_network = mock_load_data
    assert trade_network.year == 2022
    assert set(trade_network.countries) == {'AFG', 'AUS', 'OZA', 'IND'}
    assert set(trade_network.products) == {'570210', '806740'}
    assert 'by_country' in trade_network.classified_countries


def test_classification_application(mock_load_data):
    trade_network = mock_load_data
    classification = trade_network.classified_countries['by_country']
    assert classification['AFG'] == 'AFG'
    assert classification['AUS'] == 'AUS'


def test_trades_by_classification(mock_load_data):
    trade_network = mock_load_data
    trades_classified = trade_network.trades_classified_df
    assert 'by_country_importer' in trades_classified.columns
    assert 'by_country_exporter' in trades_classified.columns


def test_diversity_calculator(mock_load_data):
    trade_network = mock_load_data
    diversity_calculator = DiversityCalculator(trade_network)

    diversity_index = diversity_calculator.calculate_diversity_index('by_country')
    assert isinstance(diversity_index, float)


def test_economic_complexity_analyzer(monkeypatch, mock_load_data):
    no_classification = ClassificationScheme(name="by_country")
    analyzer = EconomicComplexityAnalyzer(2022, 2022, [no_classification])

    mock_trade_network = mock_load_data

    result = analyzer.analyze(mock_trade_network, 'AUS', 'by_country')
    assert 'export_product_diversity' in result
    assert 'import_product_diversity' in result


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
