from csv import DictReader
from pydantic import BaseModel
from typing import Type

from src.models.pydantic_models import (
    TradeData,
    Country,
    HarmonizedCategory,
    Region,
    AdminRegion,
    IncomeLevel,
    LendingType,
)


class DataExtractor:

    @staticmethod
    def _open_csv(file_path: str, model: Type[BaseModel]) -> list[BaseModel]:
        extracted_data: list = []
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader: DictReader = DictReader(file)
            yield reader

    @staticmethod
    def extract_trade_data_baci(file_path: str) -> list[BaseModel]:
        return DataExtractor._open_csv(file_path, model=TradeData)

    @staticmethod
    def extract_country_data_wbd(file_path: str):
        extracted_data: list = []
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader: DictReader = DictReader(file)
            for row in reader:
                country = Country(**row)
                country.region = Region(**row)
                country.admin_region = AdminRegion(**row)
                country.income_level = IncomeLevel(**row)
                country.lending_type = LendingType(**row)
                extracted_data.append(country)
        return extracted_data

    @staticmethod
    def extract_product_codes(file_path: str) -> list[HarmonizedCategory]:
        extracted_data: list = []
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader: DictReader = DictReader(file)
            for row in reader:
                product = HarmonizedCategory(**row)
                extracted_data.append(product)

        return extracted_data

    @staticmethod
    def extract_gdp_deflator_wbd(file_path: str):
        return DataExtractor._open_csv(file_path, model=Country)


