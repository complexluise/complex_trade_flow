

class DataTransform:

    @staticmethod
    def enrich_data():
        pass

    @staticmethod
    def fetch_region_from_iso3(iso3):
        # Example: Mock function that returns a region based on ISO code
        region_map = {'USA': 'North America', 'BRA': 'Latin America'}
        return region_map.get(iso3, None)

    @staticmethod
    def filter_by_product_category(data: list[dict], product_code: str) -> list[dict]:
        """Filter by product category code."""
        return [record for record in data if record["product_category"] == product_code]
