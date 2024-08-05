from pydantic import BaseModel, Field, model_validator, validator
from typing import Optional


class Region(BaseModel):
    id: str = Field(alias="region.id")
    iso2code: str = Field(alias="region.iso2code")
    value: str = Field(alias="region.value")


class AdminRegion(BaseModel):
    id: Optional[str] = Field(default=None, alias="adminregion.id")
    iso2code: Optional[str] = Field(default=None, alias="adminregion.iso2code")
    value: Optional[str] = Field(default=None, alias="adminregion.value")


class IncomeLevel(BaseModel):
    id: Optional[str] = Field(default=None, alias="incomeLevel.id")
    iso2code: Optional[str] = Field(default=None, alias="incomeLevel.iso2code")
    value: Optional[str] = Field(default=None, alias="incomeLevel.value")


class LendingType(BaseModel):
    id: Optional[str] = Field(default=None, alias="lendingType.id")
    iso2code: Optional[str] = Field(default=None, alias="lendingType.iso2code")
    value: Optional[str] = Field(default=None, alias="lendingType.value")


class Country(BaseModel):
    id: str = Field(alias="id")
    iso2: str = Field(alias="iso2Code")
    name: str = Field(alias="name")
    capital_city: Optional[str] = Field(default=None, alias="capitalCity")
    longitude: Optional[float] = Field(default=None, alias="longitude")
    latitude: Optional[float] = Field(default=None, alias="latitude")
    region: Region = Field(default=None)
    admin_region: AdminRegion = Field(default=None)
    income_level: IncomeLevel = Field(default=None)
    lending_type: LendingType = Field(default=None)

    class Config:
        allow_population_by_field_name = True

    @model_validator(mode='before')
    @classmethod
    def parse_coordinates(cls, data):
        for field in ['longitude', 'latitude']:
            value = data.get(field, None)
            try:
                data[field] = float(value) if value not in ['', None] else None
            except ValueError:
                data[field] = None
        return data


class HarmonizedCategory(BaseModel):
    code: str
    description: str

    @validator("code", "description", pre=True)
    def validate_string_fields(cls, v):
        if isinstance(v, str):
            return v.strip()
        raise ValueError("String value expected")


class HarmonizedSystem(BaseModel):
    HS2: HarmonizedCategory
    HS4: HarmonizedCategory
    HS6: HarmonizedCategory


class TradeData(BaseModel):
    year: str
    exporter: Country
    importer: Country
    value: str
    quantity: str
    product_category: HarmonizedSystem

    @validator("year", "exporter", "importer", pre=True)
    def validate_string_fields(cls, v):
        if isinstance(v, str):
            return v.strip()
        raise ValueError("String value expected")

    @validator("value", "quantity", pre=True)
    def validate_numeric_fields(cls, v):
        if v is None or v == "":
            return 0
        try:
            return float(v.replace(",", ""))
        except ValueError as e:
            raise ValueError(f"Could not convert to float: {v}") from e
