import requests
import pandas as pd
import time

Base_URL = "http://api.worldbank.org/v2"


def get_params_string(params_dict):
    if params_dict:
        params_list = []
        for key, value in params_dict.items():
            params_list.append(key + "=" + str(value))
        params = "?" + "&".join(params_list)
    else:
        params = ""

    return params


def request_contry(params_dict, sub_query):
    # TODO: USE WBGAPI -> https://blogs.worldbank.org/opendata/introducing-wbgapi-new-python-package-accessing-world-bank-data
    print(params_dict)

    params = get_params_string(params_dict)
    country_url = Base_URL + "/country" + sub_query + params
    print(country_url)

    payload = {}
    headers = {}

    response = requests.request("GET", country_url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return None


# Iterate by page and get all countries
def iterate_by_page(sub_query="", params_dict={}):
    my_response = []
    is_last_page = False
    page = 1
    while not is_last_page:
        # make request
        params_dict["format"] = "json"
        params_dict["page"] = page
        response = request_contry(params_dict, sub_query)
        my_response.append(response)
        page += 1
        is_last_page = not response[0]["page"] < response[0]["pages"]

    return my_response


def parse_country_data(my_json):
    df_list = []
    for page in my_json:
        df = pd.json_normalize(page[1])
        df_list.append(df)

    df_final = pd.concat(df_list)

    return df_final


def get_indicator_data_country(country, indicator, dates):
    response = iterate_by_page(
        sub_query="/" + country + "/indicator/" + indicator, params_dict={"date": dates}
    )
    df = parse_country_data(response)
    return df


def get_countries_data():
    my_json = iterate_by_page()
    df_country = parse_country_data(my_json)
    return df_country


if __name__ == "__main__":
    # Get country data
    df_country = get_countries_data()
    # df_country.to_csv('World Bank Data/countries.csv', index=False)

    # Example of getting data for USA
    # df = get_indicator_data_country('USA', 'NY.GDP.PCAP.CD', '1995:2022')

    # Input counties list, data indicator and dates

    countries = df_country["id"].to_list()
    indicators = [
        # {"indicator_code": 'NE.IMP.GNFS.ZS',
        # "description":"Import of goods and services (% of GDP)"},
        # {"indicator_code": 'NY.GDP.MKTP.CD',
        # "description":"GDP (current US$)"},
        # {"indicator_code": 'SP.POP.TOTL',
        # "description":"Population, total"},
        # {"indicator_code": 'TX.VAL.MRCH.CD.WT',
        # "description":"Merchandise exports (current US$)"},
        # {"indicator_code": 'TX.VAL.MANF.ZS.UN',
        # "description":"GDP per capita (current US$)"},
        # {"indicator_code": 'EG.USE.PCAP.KG.OE',
        # "description":"Energy use (kg of oil equivalent per capita)"},
        # {"indicator_code": 'NY.GDP.DEFL.KD.ZG',
        # "description":"Inflation, GDP deflator (annual %)"}
        # {"indicator_code": 'NY.GDP.DEFL.ZS',
        # "description":"GDP deflator (base year varies by country)"},
        #{
        #    "indicator_code": "NY.GDP.DEFL.ZS.AD",
        #    "description": "GDP deflator: linked series (base year varies by country)",
        #}
        #{
        #    "indicator_code": "SI.POV.GINI",
        #    "description": "Gini coefficient of income distribution",
        #},
        #{
        #    "indicator_code": "SI.DST.10TH.10",
        #    "description": "Income share held by highest 10%"
        #},
        #{
        #    "indicator_code": "SI.DST.FRST.20",
        #    "description": "Income share held by lowest 20%"
        #},
        #{
        #    "indicator_code": "SI.DST.05TH.20",
        #    "description": "Income share held by highest 20%"
        #},
        #{
        #    "indicator_code": "SI.SPR.PC40.ZG",
        #    "description": "Annualized average growth rate in per capita real survey mean consumption or income, bottom 40% of population (%)"
        #},
        # Impacto ecológico
        {
            "indicator_code": "EN.ATM.CO2E.PC",
            "description": "CO2 emissions (metric tons per capita)"
        },
        {
            "indicator_code": "EG.USE.PCAP.KG.OE",
            "description": "Energy use (kg of oil equivalent per capita)",
        },
        {
            "indicator_code": "EG.FEC.RNEW.ZS",
            "description": "Renewable energy consumption (% of total final energy consumption)"
        },
        {
            "indicator_code": "NY.ADJ.SVNG.GN.ZS",
            "description": "Adjusted net savings, including particulate emission damage (% of GNI)"
        }
    ]
    dates = "1995:2022"

    for indicator in indicators:
        df_list = []
        for country in countries:
            print("Getting data for country: ", country)
            try:
                df = get_indicator_data_country(
                    country, indicator["indicator_code"], dates
                )
            except Exception as e:
                print(e)
                print("Error getting data for country: ", country)
                continue

            df_list.append(df)
            time.sleep(5)

        df_final = pd.concat(df_list)
        df_final.to_csv(
            "World_Bank_Data/"
            + indicator["indicator_code"]
            + "_"
            + dates.replace(":", "-")
            + ".csv",
            index=False,
            encoding="utf-8",
        )
