from __future__ import annotations

import os

from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

from pandas import DataFrame
from scipy import stats
from tqdm import tqdm
from joblib import Parallel, delayed

from src.constants import BACIColumnsTradeData, WBDCountry


class ClassificationScheme:
    """
    Handles loading and applying different classification schemes to countries.

    This class can load classification data from different sources and map countries
    to their respective classifications (e.g., regions, income levels).
    """
    def __init__(self, name: str, file_path: Optional[str] = None, key_column: Optional[str] = None, value_column: Optional[str] = None):
        self.name = name
        self.file_path = file_path
        self.key_column = key_column
        self.value_column = value_column
        self.classification_data = self._load_classification_data()

    def _load_classification_data(self) -> dict[str, str]:
        """
        Loads classification data from a CSV file, or returns an empty dictionary for NoClassification.

        Returns:
            dict[str, str]: A dictionary mapping country codes to classification values.
        """
        if self.file_path and self.key_column and self.value_column:
            classification_df = pd.read_csv(self.file_path)
            return classification_df.set_index(self.key_column)[self.value_column].to_dict()
        else:
            return {}  # For NoClassification, return an empty dictionary

    def apply_classification(self, countries: set[str]) -> dict[str, str]:
        """
        Maps each country to its classification value or to itself if no classification is provided.

        Args:
            countries (set[str]): A set of country codes.

        Returns:
            dict[str, str]: A dictionary mapping each country to its classification value or to itself.
        """
        if not self.file_path:
            return {country: country for country in countries}  # NoClassification behavior
        return {country: self.classification_data.get(country, 'Unknown') for country in countries}


class TradeNetwork:
    """
    Represents a trade network for a specific year.

    This class provides methods to load trade data, access information about countries,
    products, and apply classification schemes.
    """
    def __init__(self, year: int, classification_schemes: list[ClassificationScheme], preloaded_data: Optional[DataFrame] = None):
        self.year = year
        self.trades_df: DataFrame = preloaded_data if preloaded_data is not None else self._load_data()
        self.countries: set[str] = set(pd.concat(
            [
                self.trades_df[BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value],
                self.trades_df[BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value],
            ]
        ).unique())
        self.products: set[str] = set(self.trades_df[BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value])
        self.classification_schemes = classification_schemes
        self.classified_countries = self._apply_classifications()
        self.trades_classified_df: DataFrame = self._trades_by_classification()

    def _load_data(self) -> DataFrame:
        """
        Loads trade data for the specified year from a predefined file path.

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

    def _apply_classifications(self) -> dict[str, dict[str, str]]:
        """
        Applies all classification schemes to the countries.

        Returns:
            dict[str, dict[str, str]]: A dictionary mapping each classification scheme name to
            a dictionary of countries and their classifications.
        """
        return {
            scheme.name: scheme.apply_classification(self.countries)
            for scheme in self.classification_schemes
        }

    def _trades_by_classification(self):
        """
        Organizes trade data by classifications.

        Returns:
            DataFrame: The trade data grouped by product category, importer, and exporter classifications.
        """
        classified_trade_network = self.trades_df.copy()

        for scheme_name, classified_countries in self.classified_countries.items():
            classified_trade_network[f"{scheme_name}_importer"] = classified_trade_network[
                BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value
            ].map(classified_countries.get)
            classified_trade_network[f"{scheme_name}_exporter"] = classified_trade_network[
                BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value
            ].map(classified_countries.get)

        return classified_trade_network


class DiversityCalculator:
    """
    Calculates the diversity of trade partners within a trade network.
    """
    def __init__(self, trade_network: TradeNetwork):
        self.trade_network = trade_network

    def filter_data_by_classification(self, scheme_name: str, importers=None, exporters=None):
        """
        Filters trade data based on specified importer and exporter classifications.

        Args:
            scheme_name (str): The name of the classification scheme to use.
            importers (list, optional): List of importer classifications. Defaults to None.
            exporters (list, optional): List of exporter classifications. Defaults to None.

        Returns:
            DataFrame: Filtered trade data based on the specified classifications.
        """
        importers = importers or self.trade_network.classified_countries[scheme_name].keys()
        exporters = exporters or self.trade_network.classified_countries[scheme_name].keys()
        return self.trade_network.trades_classified_df[
            (
                self.trade_network.trades_classified_df[f"{scheme_name}_importer"].isin(importers)
            )
            & (
                self.trade_network.trades_classified_df[f"{scheme_name}_exporter"].isin(exporters)
            )
        ]

    @staticmethod
    def calculate_marginal_probabilities(category: str, data: DataFrame, column: str) -> np.ndarray:
        """
        Calculates the marginal probabilities for a specific category within trade data.

        Args:
            category (str): The name of the category column in the trade data.
            data (DataFrame): The trade data DataFrame.
            column (str): Column name used to get the distribution

        Returns:
            np.ndarray: A NumPy array containing the marginal probabilities.
        """
        distribution = data.groupby(category)[column].sum().values
        return distribution / np.sum(distribution)

    def calculate_diversity_index(self, scheme_name: str, importers=None, exporters=None) -> float:
        """
        Calculates the diversity index for trade data based on a classification scheme.

        Args:
            scheme_name (str): The name of the classification scheme to use.
            importers (list, optional): List of importer classifications. Defaults to None.
            exporters (list, optional): List of exporter classifications. Defaults to None.

        Returns:
            float: diversity index.
        """
        data = self.filter_data_by_classification(scheme_name, importers, exporters)
        probabilities = self.calculate_marginal_probabilities(
            category=BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value,
            data=data,
            column=BACIColumnsTradeData.MONEY.value
        )
        return 2 ** stats.entropy(probabilities, base=2)


class EconomicComplexityAnalyzer:
    """
    TODO: algunas cosas acopladas como los directorios
    """
    def __init__(self, start_year: int, end_year: int, classification_schemes: list[ClassificationScheme]):
        self.start_year = start_year
        self.end_year = end_year
        self.classification_schemes = classification_schemes
        self.analysis_dict = {
            "compute_entity_product_diversification": self.compute_entity_product_diversification
        }

    @staticmethod
    def compute_entity_product_diversification(trade_network: TradeNetwork, entity: str, scheme_name: str) -> dict:
        calculator = DiversityCalculator(trade_network)

        all_entities = trade_network.classified_countries[scheme_name].keys()

        return {
            scheme_name: entity,
            "export_product_diversity": calculator.calculate_diversity_index(
                scheme_name=scheme_name,
                importers=all_entities,
                exporters=[entity]
            ),
            "import_product_diversity": calculator.calculate_diversity_index(
                scheme_name=scheme_name,
                importers=[entity],
                exporters=all_entities
            ),
        }

    def analyze_year(self, year: int, scheme_name: str, analysis_type) -> DataFrame:
        network = TradeNetwork(year, self.classification_schemes)

        results = Parallel(n_jobs=-1)(
            delayed(analysis_type)(network, entity, scheme_name) for entity in
            tqdm(network.classified_countries[scheme_name].keys(), desc=f"Analyzing year {year}")
        )

        return pd.DataFrame(results)

    def run_analysis(self, type_analysis: str, output_directory: str) -> None:
        """
        Runs the diversity analysis for each year and classification scheme, and stores the results.
        """
        analysis = self.analysis_dict[type_analysis]
        for scheme in self.classification_schemes:
            for year in range(self.start_year, self.end_year + 1):
                print(f"Analyzing {scheme.name} for {year}...")
                analysis_df = analysis(year, scheme.name)
                self.save_csv(analysis_df, output_directory,scheme.name, year)

    @staticmethod
    def save_csv(df, output_directory, scheme_name, year):
        # TODO: esta función de guarado esta acoplada a la diversidad
        output_directory = output_directory + "/diversity/"
        os.makedirs(output_directory, exist_ok=True)
        output_filename = f"{scheme_name}_diversity_{year}.csv"
        df.to_csv(output_directory+output_filename, index=False)
        print(f"Saved results to {output_directory+output_filename}")


if __name__ == "__main__":
    # Define classification schemes

    no_classification = ClassificationScheme(
        name="by_country"
    )

    region_scheme = ClassificationScheme(
        name="by_region",
        file_path="data/raw_data/world_bank_data/countries.csv",
        key_column=WBDCountry.ISO_CODE_3.value,
        value_column=WBDCountry.REGION_NAME.value
    )

    analyzer = EconomicComplexityAnalyzer(1995, 1996, classification_schemes=[region_scheme])
    analyzer.run_analysis(
        output_directory=f"data/processed_data/{region_scheme}/diversity/"
    )
