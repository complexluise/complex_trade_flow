import pytest
import numpy as np
from pathlib import Path
import json

from pandas import DataFrame

from complex_trade_flow.clean_trade_data import RawDataManager, GDPDataHandler, DataCleaner


def test_integration():
    DataCleaner.clean_trade_data()


def test_normalize_column_names():

    manager = RawDataManager(1995)

    raw_shape = manager.transaction_data.shape
    raw_money_sum = manager.transaction_data["v"].sum()


    cleaned_data: DataFrame = DataCleaner.normalize_column_names(
        manager.transaction_data, manager.country_data
    )

    assert cleaned_data.shape == raw_shape  # shape dont change
    assert cleaned_data["money"].sum() == raw_money_sum  # sum money dont change

def test_gdp_deflator():
    pass
