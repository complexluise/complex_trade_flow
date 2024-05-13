"""This is the main executable script for the CLI application."""
from src.etl.etl_processor import ETLProcessor


def upload_countries():
    ETLProcessor.upload_countries("data/raw_data/world_bank_data/countries.csv")


def main():
    """
    The main entry point of the application when run as a script.
    """
    upload_products()


if __name__ == "__main__":
    main()
