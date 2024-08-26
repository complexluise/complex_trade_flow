import pytest

from complex_trade_flow.networks import TradeNetwork
from complex_trade_flow.utils import ClassificationScheme


def test_trade_netwok_initialization_countries():

    sin_pais = ClassificationScheme(name="SinPaís")
    trade_network = TradeNetwork(1995, [sin_pais])
    assert trade_network.trade_data_classified.shape[0] == trade_network.trade_data.shape[0]
    assert sin_pais.name == list(trade_network.entities.keys())[0]


def test_trade_netwok_initialization_region():
    region_scheme = ClassificationScheme(
        name="by_region",
        file_path="data/raw_data/world_bank_data/countries.csv",
        key_column="id",
        value_column="region.value"
    )
    trade_network = TradeNetwork(1995, [region_scheme])
    assert trade_network.trade_data_classified.shape[0] == trade_network.trade_data.shape[0]
    assert region_scheme.name == list(trade_network.entities.keys())[0]
    assert "by_region_exporter" in list(trade_network.trade_data_classified.columns)
