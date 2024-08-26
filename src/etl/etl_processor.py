"""This module contains the ETLProcessor class, which orchestrates the ETL process (Extract, Transform, Load)."""
from src.etl.data_extractor import DataExtractor
from src.etl.data_loader import DataLoader
from src.models.pydantic_models import TradeData, Country, HarmonizedCategory


class ETLProcessor:
    """
    The ETLProcessor is responsible for managing the overall ETL process,
    ensuring that data flows correctly through the extract, transform, and load phases.
    """

    @staticmethod
    def upload_countries(file_path: str):
        countries_wbd: list[Country] = DataExtractor.extract_country_data_wbd(file_path=file_path)
        DataLoader.load_countries_to_neo4j(countries_wbd)

    @staticmethod
    def upload_products(file_path: str):
        countries_wbd: list[HarmonizedCategory] = DataExtractor.extract_product_codes(file_path=file_path)
        DataLoader.load_countries_to_neo4j(countries_wbd)

    @staticmethod
    def upload_trade_data(files_dir: str):
        pass


if __name__ == '__main__':
    ETLProcessor.upload_countries("data/raw_data/world_bank_data/countries.csv")
