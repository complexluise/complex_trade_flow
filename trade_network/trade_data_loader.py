from pathlib import Path
import pandas as pd

from .constants import BACIColumnsTradeData


class TradeDataLoader:
    """
    Responsable de cargar y preprocesar los datos de comercio.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_trade_data(self, year: int) -> pd.DataFrame:
        """
        Carga los datos de comercio para el año especificado.

        Args:
            year (int): El año para el cual se deben cargar los datos.

        Returns:
            pd.DataFrame: El DataFrame con los datos de comercio.
        """
        file_path = Path(self.data_dir) / f"cleaned_HS92_Y{year}_V202401b.csv"
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