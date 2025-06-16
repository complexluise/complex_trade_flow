from __future__ import annotations

import os

import pandas as pd

from collections.abc import Callable
from pandas import DataFrame
from tqdm import tqdm
from joblib import Parallel, delayed

from .constants import EconomicComplexity
from .diversity_metrics import DiversityCalculator
from .utils import ClassificationScheme
from complex_trade_flow import TradeNetwork


class EconomicComplexityAnalyzer:
    """
    TODO: algunas cosas acopladas como los directorios
    """
    def __init__(self, start_year: int, end_year: int, classification_schemes: list[ClassificationScheme]):
        self.start_year = start_year
        self.end_year = end_year
        self.classification_schemes = classification_schemes
        self.analysis_dict: dict[EconomicComplexity, Callable] = {
            EconomicComplexity.ENTITY_PRODUCT_DIVERSIFICATION.value: self.compute_entity_product_diversification
        }

    def analyze_year(self, year: int, scheme_name: str, type_analysis: EconomicComplexity) -> DataFrame:
        network = TradeNetwork.from_year(year, classification_schemes=self.classification_schemes)

        analysis: Callable = self.analysis_dict[type_analysis.value]

        results = Parallel(n_jobs=-1)(
            delayed(analysis)(network, entity, scheme_name) for entity in
            tqdm(network.entities[scheme_name], desc=f"Analyzing year {year}")
        )

        return pd.DataFrame(results)

    def run_analysis(self, type_analysis: EconomicComplexity, output_directory: str) -> None:
        """
        Runs the diversity analysis for each year and classification scheme, and stores the results.
        """

        for scheme in self.classification_schemes:
            for year in range(self.start_year, self.end_year + 1):
                print(f"Analyzing {scheme.name} for {year}...")
                analysis_df = self.analyze_year(year, scheme.name, type_analysis)
                self.save_csv(analysis_df, output_directory, scheme.name, year)

    @staticmethod
    def save_csv(df, output_directory, scheme_name, year):
        # TODO: esta función de guarado esta acoplada a la diversidad
        output_directory = output_directory + "/diversity/"
        os.makedirs(output_directory, exist_ok=True)
        output_filename = f"{scheme_name}_diversity_{year}.csv"
        df.to_csv(output_directory+output_filename, index=False)
        print(f"Saved results to {output_directory+output_filename}")

    @staticmethod
    def compute_entity_product_diversification(
            trade_network: TradeNetwork,
            entity: str,
            scheme_name: str
    ) -> dict:
        calculator = DiversityCalculator()
        return {
            scheme_name: entity,
            "export_product_diversity": calculator.calculate_diversity_index(
                data=trade_network.filter_data_by_entities(
                            scheme_name=scheme_name,
                            exporters=[entity]
                        )
            ),
            "import_product_diversity": calculator.calculate_diversity_index(
                data=trade_network.filter_data_by_entities(
                    scheme_name=scheme_name,
                    importers=[entity],
                )
            ),
        }
