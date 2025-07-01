from collections import defaultdict
from typing import Optional, Dict, Any
import pandas as pd

from .constants import BACIColumnsTradeData
from .trade_data_loader import TradeDataLoader
from .utils import ClassificationScheme


class TradeNetwork:
    """
    Representa una red de comercio para un año específico.
    """

    def __init__(
            self,
            trade_data: pd.DataFrame,
            classification_schemes: list[ClassificationScheme] | None = None
    ):
        self.trade_data = trade_data  # TODO validate trade data
        self.countries: set[str] = set(pd.concat([
            self.trade_data[BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value],
            self.trade_data[BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value]
        ]).unique())
        self.products: set[str] = set(self.trade_data[BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value])

        if classification_schemes:
            self.classification_schemes = classification_schemes
            self.classified_countries = self._apply_classifications()
            self.entities = self._get_entities(self.classified_countries)
            self.trade_data_classified = self._classify_trade_data()

    @classmethod
    def from_year(
            cls,
            year: int,
            base_directory: str = "data/processed_data/BACI_HS92_V202401b/cleaned_trade_data/",
            classification_schemes: list[ClassificationScheme] | None = None
    ) -> "TradeNetwork":
        """
        Crea una instancia de TradeNetwork para un año específico cargando datos de comercio.
        Este método actúa como un constructor alternativo para la clase TradeNetwork.

        Args:
            year: Un entero que representa el año para el cual se cargarán los datos comerciales.
            base_directory: Una cadena que representa la ruta del directorio base donde
                se almacenan los archivos de datos comerciales. Por defecto es
                "data/processed_data/BACI_HS92_V202401b/cleaned_trade_data/".
            classification_schemes: Una lista opcional de objetos ClassificationScheme
                para clasificar los datos comerciales. Por defecto es None.

        Returns:
            Una instancia de la clase TradeNetwork que contiene datos comerciales para el
            año especificado.
        """
        trade_data = TradeDataLoader(base_directory).load_trade_data(year)
        return cls(trade_data=trade_data, classification_schemes=classification_schemes)


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

    def filter_data_by_entities(self, scheme_name: str, importers=None, exporters=None):
        """
        Filters trade data based on specified importer and exporter classifications.
        Pro defecto importers y exportes traen todas las entidades

        Args:
            scheme_name (str): The name of the classification scheme to use.
            importers (list, optional): List of importer classifications. Defaults to None.
            exporters (list, optional): List of exporter classifications. Defaults to None.

        Returns:
            DataFrame: Filtered trade data based on the specified classifications.
        """
        importers = importers or self.entities[scheme_name]
        exporters = exporters or self.entities[scheme_name]
        return self.trade_data_classified[
            (
                self.trade_data_classified[f"{scheme_name}_importer"].isin(importers)
            )
            & (
                self.trade_data_classified[f"{scheme_name}_exporter"].isin(exporters)
            )
            ]

    @staticmethod
    def _get_entities(first_dict: dict[str, dict[str, str]]) -> dict[str, set]:
        inverted_dict = defaultdict(set)

        for main_key in first_dict.keys():
            second_dict = first_dict[main_key]
            inverted_dict[main_key] = set(second_dict.values())

        return dict(inverted_dict)
