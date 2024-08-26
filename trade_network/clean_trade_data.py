import json
import pandas as pd

from pandas import DataFrame
from pathlib import Path
from .constants import BACIColumnsTradeData, CountryCodes, WBDCountry, WBDGDPDeflator

with open("./trade_network/data_paths.json") as file:
    paths = json.load(file)


class RawDataManager:
    def __init__(self, year):
        self.year = year

        self.transaction_data = pd.read_csv(
            paths["raw_data_dir"] + f"BACI_HS92_Y{year}_V202401b.csv",
            sep=","
        )
        self.country_data = pd.read_csv(
            paths["raw_data_dir"] + "country_codes_V202401b.csv"
        )
        # Countries location region
        self.wbd_countries = pd.read_csv(paths["wbd_countries"])
        # GDP deflator: linked series (base year varies by country), use dtype="string" to avoid unicodeerror
        self.gdp_deflator = pd.read_csv(
            paths["wbd_gdp_deflator"],
            dtype="string"
        )

        self.enriched_country_data = self.enrich()

    def enrich(self):
        enriched = self.country_data.merge(
            self.wbd_countries,
            how="left",
            left_on=CountryCodes.ISO_CODE_3.value,
            right_on=WBDCountry.ISO_CODE_3.value,
        )
        enriched.drop_duplicates(subset=["country_iso3"], inplace=True)  # TODO: ¿Por qué hay duplicados?
        return enriched


class GDPDataHandler:
    """
    Class to handle GDP-related data transformations.
    """

    def __init__(self, df_gdp, base_year: str = "2013"):
        """
        Initializes the GDPDataHandler with a DataFrame containing GDP data and an optional base year.

        Args:
        df_gdp (pd.DataFrame): DataFrame containing GDP data with columns 'countryiso3code', 'date', and 'value'.
        base_year (int): The base year for constant USD conversion, default 2013.
        """
        self.df_gdp = df_gdp
        self.base_year = base_year

    def get_gdp_linked(self, year, country="USA"):
        """
        Retrieves the GDP deflator for a given year and country.

        Args:
        year (int): The year for which the GDP deflator is requested.
        country (str): The country code for which the GDP data is requested.

        Returns:
        float: The GDP deflator value, or 0.0 if no data is available.
        """
        bool_mask = (self.df_gdp[WBDGDPDeflator.ISO_CODE_3.value] == country) & (
                self.df_gdp[WBDGDPDeflator.YEAR.value] == str(year)
        )
        df_filtered = self.df_gdp[bool_mask]

        if df_filtered.empty:
            return 0.0
        else:
            return float(df_filtered[WBDGDPDeflator.MONEY.value].iloc[0])

    def to_constant_usd(self, df: DataFrame, year: str) -> DataFrame:
        """
        Converts the 'Value' column of a DataFrame from current USD to constant USD using the GDP deflator.

        Args:
        df (pd.DataFrame): The DataFrame containing the 'Value' column to convert.
        year (int): The year for the GDP deflator to apply.

        Returns:
        pd.DataFrame: The modified DataFrame with 'Value' in constant USD.
        """
        gdp_linked = self.get_gdp_linked(year)
        gdp_base = self.get_gdp_linked(self.base_year)

        if gdp_linked == 0 or gdp_base == 0:
            raise ValueError("GDP deflator is zero, which may indicate missing data.")

        df[BACIColumnsTradeData.MONEY.value] = df[
            BACIColumnsTradeData.MONEY.value
        ].apply(lambda x: (float(x) / gdp_linked) * gdp_base * 100)
        return df


class DataCleaner:
    @staticmethod
    def normalize_column_names(transaction_data, country_data) -> DataFrame:
        transaction_data.replace({"q": "           NA"}, "0", inplace=True)
        transaction_data["q"] = transaction_data["q"].astype(float)
        country_map = pd.Series(
            country_data[WBDCountry.ISO_CODE_3.value].values,
            index=country_data[CountryCodes.CODE.value],
        ).to_dict()
        transaction_data["i"] = transaction_data["i"].map(country_map)
        transaction_data["j"] = transaction_data["j"].map(country_map)
        transaction_data.rename(
            columns={
                "t": BACIColumnsTradeData.YEAR.value,
                "i": BACIColumnsTradeData.EXPORTER_ISO_CODE_3.value,
                "j": BACIColumnsTradeData.IMPORTER_ISO_CODE_3.value,
                "k": BACIColumnsTradeData.PRODUCT_CATEGORY_CODE.value,
                "v": BACIColumnsTradeData.MONEY.value,
                "q": BACIColumnsTradeData.MASS.value,
            },
            inplace=True,
        )
        return transaction_data

    @staticmethod
    def clean_trade_data():
        """
        TODO: use Parallel to optimize time execution
        """
        years = [str(year) for year in range(1995, 2022 + 1)]

        for year in years:
            print("Processing year = ", year)

            manager = RawDataManager(year)

            cleaned_data: DataFrame = DataCleaner.normalize_column_names(
                manager.transaction_data, manager.enriched_country_data
            )

            gpd_handler = GDPDataHandler(manager.gdp_deflator, base_year="2013")
            data_corrected = gpd_handler.to_constant_usd(cleaned_data, year)

            data_corrected.to_csv(
                paths["cleaned_data_dir"] + f"cleaned_HS92_Y{year}_V202401b.csv",
                index=False
            )

