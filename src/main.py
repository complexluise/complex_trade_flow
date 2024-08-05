"""This is the main executable script for the CLI application."""
from src.etl.etl_processor import ETLProcessor


def upload_countries():
    ETLProcessor.upload_countries("data/raw_data/world_bank_data/countries.csv")


def upload_products():
    ETLProcessor.upload_products("data/raw_data/world_bank_data/product_codes_HS92_V202401b.csv")


def upload_trade_data():
    pass


def main():
    """
    The main entry point of the application when run as a script.
    """
    upload_products()


if __name__ == "__main__":
    main()
