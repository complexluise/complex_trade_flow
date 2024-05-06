import csv
from typing import List, Dict
from src.models.pydantic_models import TradeData


class DataExtractor:
    def extract_trade_data(self, file_path: str) -> List[Dict]:
        extracted_data = []
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                trade_data = TradeData.parse_obj(row)
                extracted_data.append(trade_data.dict())
        return extracted_data
