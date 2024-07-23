

class DataTransform:

    @staticmethod
    def enrich_data():
        pass

    def fetch_region_from_iso3(iso3):
        # Example: Mock function that returns a region based on ISO code
        region_map = {'USA': 'North America', 'BRA': 'Latin America'}
        return region_map.get(iso3, None)
