from pydantic import BaseModel, validator


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
    exporter: str
    importer: str
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
