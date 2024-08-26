from enum import Enum


class BACIColumnsTradeData(Enum):
    YEAR = "year"
    EXPORTER_ISO_CODE_3 = "exporter_iso_code_3"
    IMPORTER_ISO_CODE_3 = "importer_iso_code_3"
    EXPORTER_REGION = "exporter_region"
    IMPORTER_REGION = "importer_region"
    PRODUCT_CATEGORY_CODE = "product_category_code"
    MONEY = "money"
    MASS = "mass"


class CountryCodes(Enum):
    CODE = "country_code"
    NAME = "country_name"
    ISO_CODE_2 = "country_iso2"
    ISO_CODE_3 = "country_iso3"


class WBDCountry(Enum):
    ISO_CODE_3 = "id"
    ISO_CODE_2 = "iso2Code"
    REGION_NAME = "region.value"


class WBDGDPDeflator(Enum):
    ISO_CODE_3 = "countryiso3code"
    YEAR = "date"  # date only have year
    MONEY = "value"  # TODO validate money in USD?
