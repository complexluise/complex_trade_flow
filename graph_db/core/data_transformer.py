from typing import List, Dict
from graph_db.models.pydantic_models import TradeData


class DataTransformer:
    @staticmethod
    def filter_by_product_category(data: List[Dict], product_code: str) -> List[Dict]:
        """Filter by product category code."""
        return [record for record in data if record["product_category"] == product_code]
