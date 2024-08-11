from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import numpy as np

from pandas import DataFrame
from scipy import stats
from tqdm import tqdm
from joblib import Parallel, delayed

from src.src.constants import BACIColumnsTradeData, WBDCountry


class TradeNetwork:
    """
    Represents a trade network for a specific year.

    This class provides methods to load trade data, access information about countries,
    products, and regions, and filter trade data based on regions.
    """
    def __init__(self, year: int):
        self.year = year
        self.trades_df: DataFrame = self._load_data()
        self.countries: set[str] = pd.concat(
            [
                self.trades_df[BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value],
                self.trades_df[BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value],
            ]
        ).unique()
        self.products: set[str] = set(self.trades_df[BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value])
        self.countries_region = self._load_region_data()
        self.region_countries = self._invert_dict(self.countries_region)
        self.trades_region_df: DataFrame = self._trades_by_region()

    def _load_data(self) -> DataFrame:
        """
        Loads trade data for the specified year from a predefined file path.

        This method reads the trade data CSV file containing information on product categories,
        exporter and importer country codes, and trade value.

        Returns:
            DataFrame: The loaded trade data for the year.
        """
        file_path = Path(
            f"data/processed_data/BACI_HS92_V202401b/cleaned_trade_data/cleaned_HS92_Y{self.year}_V202401b.csv")
        return pd.read_csv(
            file_path,
            usecols=[
                BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value,
                BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value,
                BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value,
                BACIColumnsTradeData.MONEY.value
            ],
            low_memory=False
        )

    @staticmethod
    def _load_region_data() -> dict[str, str]:
        # TODO: Colocar la dirección es de muy mala practica
        region_data = pd.read_csv("data\\raw_data\world_bank_data\countries.csv")
        return region_data.set_index(WBDCountry.ISO_CODE_3.value)[WBDCountry.REGION_NAME.value].to_dict()

    @staticmethod
    def _invert_dict(my_dict: dict[str, str]) -> dict[Any, list]:
        inverted_dict = defaultdict(list)

        for key, value in my_dict.items():
            inverted_dict[value].append(key)

        return dict(inverted_dict)

    def find_countries_in_region(self, region) -> list[str]:
        return self.region_countries.get(region, [])

    def _trades_by_region(self):
        region_trade_network = self.trades_df.copy()
        region_trade_network[BACIColumnsTradeData.IMPORTER_REGION.value] = region_trade_network[
            BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value
        ].map(
            lambda country: self.countries_region.get(country)
        )
        region_trade_network[BACIColumnsTradeData.EXPORTER_REGION.value] = region_trade_network[
            BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value
        ].map(
            lambda country: self.countries_region.get(country)
        )

        grouped_df = region_trade_network.groupby(
            [
                BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value,
                BACIColumnsTradeData.IMPORTER_REGION.value,
                BACIColumnsTradeData.EXPORTER_REGION.value,
            ],

        ).sum().reset_index()

        grouped_df.drop(
            columns=[BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value, BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value],
            inplace=True
        )

        return grouped_df


class DiversityCalculator:
    """
    Calculates the diversity of trade partners within a trade network

    This class provides methods to filter trade data based on importer and exporter countries
    or regions, and calculates the Shannon diversity index to measure trade partner diversity.
    """
    def __init__(self, trade_network: TradeNetwork):
        self.trade_network = trade_network

    def filter_data_by_country_partners(self, importers=None, exporters=None):
        """
        Filters trade data based on specified importer and exporter countries.

        If no importers or exporters are provided, uses all countries in the trade network.

        Args:
            importers (list, optional): List of importer country codes. Defaults to None.
            exporters (list, optional): List of exporter country codes. Defaults to None.

        Returns:
            DataFrame: Filtered trade data based on the specified countries.
        """

        importers = self.trade_network.countries if importers is None else importers
        exporters = self.trade_network.countries if exporters is None else exporters
        return self.trade_network.trades_df[
            (
                self.trade_network.trades_df[BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value].isin(
                    importers
                )
            )
            & (
                self.trade_network.trades_df[BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value].isin(
                    exporters
                )
            )
            ]

    def filter_data_by_region_partners(self, importers=None, exporters=None):
        """
        Filters trade data based on specified importer and exporter regions.

        If no importers or exporters are provided, uses all regions in the trade network.

        Args:
            importers (list, optional): List of importer region names. Defaults to None.
            exporters (list, optional): List of exporter region names. Defaults to None.

        Returns:
            DataFrame: Filtered trade data based on the specified regions.
        """
        importers = self.trade_network.region_countries.keys() if importers is None else importers
        exporters = self.trade_network.region_countries.keys() if exporters is None else exporters
        return self.trade_network.trades_region_df[
            (
                self.trade_network.trades_region_df[BACIColumnsTradeData.IMPORTER_REGION.value].isin(
                    importers
                )
            )
            & (
                self.trade_network.trades_region_df[BACIColumnsTradeData.EXPORTER_REGION.value].isin(
                    exporters
                )
            )
            ]

    @staticmethod
    def calculate_marginal_probabilities(category: str, data: DataFrame):
        """
        Calculates the marginal probabilities for a specific category within trade data.

        This function calculates the proportion of trade value for each unique value in the
        specified category.

        Args:
            category (str): The name of the category column in the trade data.
            data (DataFrame): The trade data DataFrame.

        Returns:
            np.ndarray: A NumPy array containing the marginal probabilities.
        """
        distribution = (
            data.groupby(category)[BACIColumnsTradeData.MONEY.value].sum().values
        )
        return distribution / np.sum(distribution)

    def calculate_diversity_index(self, importers=None, exporters=None, region=False) -> float:
        """Calculates the Shannon diversity index for trade data.

        Measures the diversity of trade partners based on product categories.
        Higher values indicate greater diversity.

        Args:
            importers (list, optional): List of importer country codes. Defaults to None.
            exporters (list, optional): List of exporter country codes. Defaults to None.
            region (bool, optional): If True, calculates diversity at the regional level.
                Otherwise, calculates at the country level. Defaults to False.

        Returns:
            float: Shannon diversity index.
        """

        data = self.filter_data_by_region_partners(importers, exporters) \
            if region else self.filter_data_by_country_partners(importers, exporters)

        probabilities = self.calculate_marginal_probabilities(
            BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value, data
        )
        return 2 ** stats.entropy(probabilities, base=2)


class EconomicComplexityAnalyzer:
    def __init__(self, start_year: int, end_year: int):
        self.start_year = start_year
        self.end_year = end_year

    @staticmethod
    def analyze_country(trade_network: TradeNetwork, country: str) -> dict:
        calculator = DiversityCalculator(trade_network)

        export_diversity = calculator.calculate_diversity_index(
            importers=[country],
            exporters=trade_network.countries)
        import_diversity = calculator.calculate_diversity_index(
            importers=trade_network.countries,
            exporters=[country]
        )
        return {
            "country": country,
            "export_product_diversity": export_diversity,
            "import_product_diversity": import_diversity,
            "region": trade_network.countries_region.get(country, "Unknown")
        }

    @staticmethod
    def analyze_region(trade_network: TradeNetwork, region: str) -> dict:
        calculator = DiversityCalculator(trade_network)

        export_diversity = calculator.calculate_diversity_index(
            importers=[region],
            exporters=trade_network.region_countries.keys(),
            region=True
        )
        import_diversity = calculator.calculate_diversity_index(
            importers=trade_network.region_countries.keys(),
            exporters=[region],
            region=True
        )

        return {
            "region": region,
            "export_product_diversity": export_diversity,
            "import_product_diversity": import_diversity,
        }

    def analyze_year_country(self, year: int) -> DataFrame:
        network = TradeNetwork(year)

        results = Parallel(n_jobs=-1)(
            delayed(self.analyze_country)(network, country) for country in
            tqdm(network.countries, desc=f"Analyzing year {year}")
        )

        return pd.DataFrame(results)

    def analyze_year_region(self, year: int) -> DataFrame:
        network = TradeNetwork(year)

        results = Parallel(n_jobs=-1)(
            delayed(self.analyze_region)(network, region) for region in
            tqdm(network.region_countries, desc=f"Analyzing year {year}")
        )

        return pd.DataFrame(results)

    def run_analysis(self) -> None:
        for year in range(self.start_year, self.end_year + 1):
            print(f"Processing year = {year}")
            results = self.analyze_year_region(year)
            self._save_results_region(results, year)

    @staticmethod
    def _save_results_countries(results: DataFrame, year: int) -> None:
        output_path = Path(
            f"data/processed_data/BACI_HS92_V202401b/diversity_countries/countries_diversity_HS92_Y{year}_V202401b.csv")
        results.to_csv(output_path, index=False)

    @staticmethod
    def _save_results_region(results: DataFrame, year: int) -> None:
        output_path = Path(
            f"data/processed_data/BACI_HS92_V202401b/diversity_regions/regions_diversity_HS92_Y{year}_V202401b.csv")
        results.to_csv(output_path, index=False)


if __name__ == "__main__":
    analyzer = EconomicComplexityAnalyzer(1995, 2022)
    analyzer.run_analysis()
