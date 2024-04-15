import pandas as pd
import os
import re
import networkx as nx

def filter_product(df, product_code, hs_code="HS6"):
    if hs_code == "HS6":
        bool_mask = df["Product category"] == product_code
    elif hs_code == "HS4":
        bool_mask = df["Product category HS[4]"] == product_code
    elif hs_code == "HS2":
        bool_mask = df["Product category HS[2]"] == product_code

    df_filtered = df[bool_mask]
    return df_filtered

def merge_links(df, by_columns=["Exporter", "Importer"], HarmonizedSystem=4):
    df_merge = df.groupby(by=by_columns).sum()
    df_merge.reset_index(inplace=True)
    return df_merge

def add_metadata(df_left, df_right, tuple_columns):
    df_right = df_right.rename(mapper=lambda x: tuple_columns[0] + "_" + str(x), axis=1)
    df_result = df_left.merge(
        df_right,
        left_on=tuple_columns[0],
        right_on=tuple_columns[0] + "_" + tuple_columns[1],
        how="inner",
    )
    return df_result

def string2float(x):
    try:
        number = re.search(r"\d+.?\d+", x).group(0)
    except:
        number = "0"
    return number

def pandas_2_graph(df):
    G = nx.DiGraph()
    for row in df.iterrows():
        G.add_weighted_edges_from(
            [(row[1]["Exporter"], row[1]["Importer"], row[1]["Value"])]
        )
    return G
class BACI_Cleaner:
    def __init__(self, dataset):
        self.FOLDERS = {
            "raw": "Raw_Data",
            "processed": "Processed_Data",
            "final": "Final_Data",
        }

        self.DATASET = dataset
        self.DATASET_ARRAY = self.DATASET.split("_")
        self.HS_YEAR = self.DATASET_ARRAY[1]
        self.VERSION_DATASET = self.DATASET_ARRAY[-1]

        self.product_codes_filename = (
            f"product_codes_{self.HS_YEAR}_{self.VERSION_DATASET}.csv"
        )
        self.country_codes_filename = f"country_codes_{self.VERSION_DATASET}.csv"

        self.df_product_codes = pd.read_csv(
            self.FOLDERS["raw"]
            + "/"
            + self.DATASET
            + "/"
            + self.product_codes_filename,
            dtype="string",
        )
        self.df_country_codes = pd.read_csv(
            self.FOLDERS["raw"]
            + "/"
            + self.DATASET
            + "/"
            + self.country_codes_filename,
            dtype="string",
            encoding="latin-1",
        )

        self.list_files_raw = os.listdir(self.FOLDERS["raw"] + "/" + self.DATASET)

        # METADATA
        self.columns_dict = {
            "t": "Year",
            "k": "Product category",  # (HS 6-digit code)
            "i": "Exporter",  # (ISO 3-digit country code)
            "j": "Importer",  # (ISO 3-digit country code)
            "v": "Value",  # of the trade flow (in thousands current USD)
            "q": "Quantity",  # (in metric tons)
        }

        self.df_gdp_linked = pd.read_csv(
            "World_Bank_Data/NY.GDP.DEFL.ZS.AD_1995-20222.csv", dtype="string"
        )

    def get_gdp_deflator(self, year, country="USA"):
        # Obtiene el deflactor de gdp para un año

        bool_mask = (self.df_gdp_linked["countryiso3code"] == country) & (
            self.df_gdp_linked["date"] == str(year)
        )
        df_gdp_deflator = self.df_gdp_linked[bool_mask]

        if df_gdp_deflator.empty:
            return 0
        else:
            gdp_deflator = df_gdp_deflator["value"].values[0]
            gdp_deflator = float(gdp_deflator)
            gdp_deflator_decimal = gdp_deflator
            return gdp_deflator_decimal

    def get_cummulative_gdp_deflator(self, years):
        # Obtiene el cummulative deflactor de gdp para un rango de años

        years_list = list(range(years[0], years[1] + 1))
        gdp_deflator_list = []

        for year in years_list:
            gdp_deflator_list.append(self.get_gdp_deflator(year))

        inflation_list = [(1 + x / 100) for x in gdp_deflator_list]
        cummulative_inflation = np.prod(inflation_list)
        return cummulative_inflation

    def get_gdp_linked(self, year, country="USA"):
        # country is USA due to Values are in thousand of US in for all countrys

        # Obtiene el deflactor de gdp para un año
        bool_mask = (self.df_gdp_linked["countryiso3code"] == country) & (
            self.df_gdp_linked["date"] == str(year)
        )
        df_gdp_linked = self.df_gdp_linked[bool_mask]

        if df_gdp_linked.empty:
            return 0.0
        else:
            gdp_linked = df_gdp_linked["value"].values[0]

        return gdp_linked

    def get_gdp_base(self):

        pass

    def to_constant_USD(self, df, year):
        # Obtiene el valor constante para un año
        gdp_linked = float(self.get_gdp_linked(year))
        year_base = 2013  # year that have less change in the first neigbour
        gdp_based = float(self.get_gdp_linked(year_base))

        df["Value"] = df["Value"].apply(lambda x: float(x) / gdp_linked/gdp_based * 100)
        return df

    def data_clean_by_year(self, filename, money_type="current_USD", graph=True):
        year_file = filename.split("_")[2]
        year = year_file[1:]

        # open file
        print(f"Processing: {filename}")
        raw_file = filename
        raw_df = pd.read_csv(
            self.FOLDERS["raw"] + "/" + self.DATASET + "/" + raw_file, dtype="string"
        )

        # Open WorldbankData
        indicators = [
            {
                "indicator_code": "NE.IMP.GNFS.ZS",
                "description": "Import of goods and services % of GDP",
                "attribute_name": "propension",
            },
            {
                "indicator_code": "NY.GDP.MKTP.CD",
                "description": "GDP",
                "attribute_name": "ingreso",
            },
            {
                "indicator_code": "SP.POP.TOTL",
                "description": "Population",
                "attribute_name": "poblacion",
            },
            {
                "indicator_code": "TX.VAL.MRCH.CD.WT",
                "description": "Merchandise exports",
                "attribute_name": "exportacion_mercancia",
            },
            {
                "indicator_code": "TX.VAL.MANF.ZS.UN",
                "description": "GDP per capita",
                "attribute_name": "exportacion_manufacturas",
            },
        ]

        # Rename Columns
        raw_df.rename(columns=self.columns_dict, inplace=True)
        # Enrich data
        col_metadata_country = {
            "Importer": "country_code",
            "Exporter": "country_code",
        }

        col_metadata_product = {"Product category": "code"}
        # Add metadata to country columns
        for key, value in col_metadata_country.items():
            raw_df = add_metadata(raw_df, self.df_country_codes, (key, value))

        for key, value in col_metadata_product.items():
            raw_df = add_metadata(raw_df, self.df_product_codes, (key, value))

        # add harmonized system code 4 and 2 digits
        raw_df["Product category HS[2]"] = raw_df["Product category"].apply(
            lambda x: x[:2]
        )
        raw_df["Product category HS[4]"] = raw_df["Product category"].apply(
            lambda x: x[:4]
        )

        clean_df = raw_df[
            [
                "Year",
                "Exporter_iso_3digit_alpha",
                "Importer_iso_3digit_alpha",
                "Value",
                "Quantity",
                "Product category_code",
            ]
        ].copy()

        clean_df.rename(
            columns={
                "Exporter_iso_3digit_alpha": "Exporter",
                "Importer_iso_3digit_alpha": "Importer",
            },
            inplace=True,
        )

        # Normalize data
        normalize = ["Value", "Quantity"]
        for col in normalize:
            clean_df[col] = clean_df[col].apply(string2float)

        clean_df = clean_df.astype({"Value": "float", "Quantity": "float"})

        # Correct to Constant USD
        if money_type == "constant_USD":
            print("Converting to Constant USD")
            clean_df = self.to_constant_USD(clean_df, year=int(year))

        # SAVE ENRICHED DATA
        SAVE_FOLDER = self.FOLDERS["processed"] + "/" + self.DATASET + "/" + year_file
        os.makedirs(SAVE_FOLDER, exist_ok=True)

        # print('Saving Enriched file: ', filename)
        clean_df.to_csv(SAVE_FOLDER + "/" + "Enriched_" + filename, index=False)

        # CONVERT 2 GRAPH

        # MERGE LINKS
        # print('Saving Merged file: ', filename)
        df_merged = merge_links(clean_df, by_columns=["Year", "Exporter", "Importer"])
        df_merged.to_csv(SAVE_FOLDER + "/" + "Merged_" + filename, index=False)

        if graph == True:
            G = pandas_2_graph(df_merged)
            # ADD Indicators from World Bank Data
            for indicator in indicators:
                df_ind = pd.read_csv(
                    "World_Bank_Data"
                    + "/"
                    + indicator["indicator_code"]
                    + "_1995-2022.csv",
                    dtype="string",
                )
                year = year_file[1:]
                df_ind.query("date == @year", inplace=True)
                indicator_dict = (
                    df_ind[["countryiso3code", "value"]]
                    .dropna()
                    .to_dict(orient="records")
                )
                indicator_dict = {
                    record["countryiso3code"]: record["value"]
                    for record in indicator_dict
                }
                nx.set_node_attributes(G, indicator_dict, indicator["attribute_name"])

            # Identificar los nodos que NO tienen el atributo 'propension'
            nodes_sin_propension = [
                n
                for n, attr in G.nodes(data=True)
                if "propension" not in attr or "ingreso" not in attr
            ]
            # Eliminar los nodos que no tienen el atributo 'propension' ni 'ingreso'
            for n in nodes_sin_propension:
                G.remove_node(n)

            return G

        print("Saving graphml file: ", filename)
        nx.write_graphml(
            G, SAVE_FOLDER + "/" + "Graph_" + filename.replace(".csv", ".graphml")
        )

        return df_merged

    def dataframe_to_graph(self, df):
        edges = df[["Exporter", "Importer", "Value"]].values
        G = nx.DiGraph()
        G.add_weighted_edges_from(edges)
        return G


if __name__ == "__main__":
    print("Starting BACI Cleaner")
    DATASET = "BACI_HS92_V202301"
    print("Dataset: ", DATASET)
    cleaner_obj = BACI_Cleaner(DATASET)
    lista = cleaner_obj.list_files_raw
    for filename in lista:
        cleaner_obj.data_clean_by_year(filename, money_type="constant_USD")
