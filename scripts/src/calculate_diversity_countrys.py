from __future__ import annotations
from typing import Tuple
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats
from dataclasses import dataclass
from tqdm import tqdm
from joblib import Parallel, delayed

from scripts.src.constants import BACIColumnsTradeData, WBDCountry


@dataclass
class TradeFlow:
    exporter: str
    importer: str
    product: str
    value: float


class TradeNetwork:
    def __init__(self, year: int):
        self.year = year
        self.trades_df: pd.DataFrame = self._load_data()
        self.countries: set[str] = pd.concat(
            [
                self.trades_df[BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value],
                self.trades_df[BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value],
            ]
        ).unique()
        self.products: set[str] = set(self.trades_df[BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value])

    def _load_data(self) -> pd.DataFrame:
        file_path = Path(
            f"../processed_data/BACI_HS92_V202401b/cleaned_trade_data/cleaned_HS92_Y{self.year}_V202401b.csv")
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


class DiversityCalculator:
    def __init__(self, trade_network: TradeNetwork):
        self.trade_network = trade_network

    def filter_data_by_trade_partners(self, importers=None, exporters=None):
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

    def calculate_marginal_probabilities(
            self, category, importers=None, exporters=None
    ):
        data = self.filter_data_by_trade_partners(importers, exporters)
        distribution = (
            data.groupby(category)[BACIColumnsTradeData.MONEY.value].sum().values
        )
        return distribution / np.sum(distribution)

    def calculate_diversity_index(self, importers=None, exporters=None) -> float:
        probabilities = self.calculate_marginal_probabilities(
            BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value, importers, exporters
        )
        return 2 ** stats.entropy(probabilities, base=2)


class EconomicComplexityAnalyzer:
    def __init__(self, start_year: int, end_year: int):
        self.start_year = start_year
        self.end_year = end_year
        self.region_data = self._load_region_data()

    @staticmethod
    def _load_region_data() -> dict[str, str]:
        region_data = pd.read_csv("../raw_data/world_bank_data/countries.csv")
        return region_data.set_index(WBDCountry.ISO_CODE_3.value)["region.value"].to_dict()

    def analyze_country(self, network: TradeNetwork, country: str) -> dict:
        calculator = DiversityCalculator(network)

        export_diversity = calculator.calculate_diversity_index(exporters=network.countries)
        import_diversity = calculator.calculate_diversity_index(importers=network.countries)
        return {
            "country": country,
            "export_product_diversity": export_diversity,
            "import_product_diversity": import_diversity,
            "region": self.region_data.get(country, "Unknown")
        }

    def analyze_region(self, network: TradeNetwork, region: str) -> dict:
        calculator = DiversityCalculator(network)
        region_countries = [country for country, reg in self.region_data.items() if reg == region]  ### Verify if the code works with a test
        region_exports = pd.concat([network.countries for country in region_countries])
        region_imports = pd.concat([network.countries for country in region_countries])

        export_diversity = calculator.calculate_diversity_index(exporters=region_exports)
        import_diversity = calculator.calculate_diversity_index(importers=region_imports)

        return {
            "region": region,
            "export_product_diversity": export_diversity,
            "import_product_diversity": import_diversity,
            "num_countries": len(region_countries)
        }

    def analyze_year(self, year: int) -> pd.DataFrame:
        network = TradeNetwork(year)

        results = Parallel(n_jobs=-1)(
            delayed(self.analyze_country)(network, country) for country in
            tqdm(network.countries, desc=f"Analyzing year {year}")
        )

        return pd.DataFrame(results)

    def run_analysis(self) -> None:
        for year in range(self.start_year, self.end_year + 1):
            print(f"Processing year = {year}")
            results = self.analyze_year(year)
            self._save_results(results, year)

    @staticmethod
    def _save_results(results: pd.DataFrame, year: int) -> None:
        output_path = Path(
            f"../processed_data/BACI_HS92_V202401b/diversity_countries/countries_diversity_HS92_Y{year}_V202401b.csv")
        results.to_csv(output_path, index=False)


if __name__ == "__main__":
    analyzer = EconomicComplexityAnalyzer(1995, 2022)
    analyzer.run_analysis()
