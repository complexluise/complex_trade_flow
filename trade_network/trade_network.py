from typing import Optional
import pandas as pd

from .constants import BACIColumnsTradeData
from .trade_data_loader import TradeDataLoader
from .utils import ClassificationScheme


class TradeNetwork:
    """
    Representa una red de comercio para un año específico.
    """
    def __init__(self, year: int, classification_schemes: list[ClassificationScheme], trade_data: Optional[pd.DataFrame] = None):
        self.year = year
        self.trade_data = trade_data if trade_data is not None else self._load_trade_data()
        self.countries: set[str] = set(pd.concat([
            self.trade_data[BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value],
            self.trade_data[BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value]
        ]).unique())
        self.products: set[str] = set(self.trade_data[BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value])
        self.classification_schemes = classification_schemes
        self.classified_countries = self._apply_classifications()
        self.trade_data_classified = self._classify_trade_data()

    def _load_trade_data(self) -> pd.DataFrame:
        """
        Carga los datos de comercio para el año especificado.

        Returns:
            pd.DataFrame: El DataFrame con los datos de comercio.
        """
        trade_data_loader = TradeDataLoader("data/processed_data/BACI_HS92_V202401b/cleaned_trade_data/")
        return trade_data_loader.load_trade_data(self.year)

    def _apply_classifications(self) -> dict[str, dict[str, str]]:
        """
        Aplica todos los esquemas de clasificación a los países.

        Returns:
            dict[str, dict[str, str]]: Un diccionario que mapea cada esquema de clasificación a
            un diccionario de países y sus clasificaciones.
        """
        return {
            scheme.name: scheme.apply_classification(self.countries)
            for scheme in self.classification_schemes
        }

    def _classify_trade_data(self) -> pd.DataFrame:
        """
        Organiza los datos de comercio por clasificaciones.

        Returns:
            pd.DataFrame: Los datos de comercio agrupados por categoría de producto, importador y exportador.
        """
        classified_trade_data = self.trade_data.copy()

        for scheme_name, classified_countries in self.classified_countries.items():
            classified_trade_data[f"{scheme_name}_importer"] = classified_trade_data[
                BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value
            ].map(classified_countries.get)
            classified_trade_data[f"{scheme_name}_exporter"] = classified_trade_data[
                BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value
            ].map(classified_countries.get)

        return classified_trade_data
