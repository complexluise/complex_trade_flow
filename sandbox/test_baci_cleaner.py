import unittest
import pandas as pd
from BACI_Cleaner import (
    filter_product,
    filter_description,
    merge_links,
    add_metadata,
    string2float,
    pandas_2_graph,
    BACI_Cleaner,
)


class TestBACICleaner(unittest.TestCase):
    def test_filter_product(self):
        data = {
            "Product category": ["0101", "0102", "0201", "0202"],
            "Value": [100, 200, 300, 400],
        }
        df = pd.DataFrame(data)
        result = filter_product(df, "0101", hs_code="HS2")
        self.assertEqual(len(result), 2)
        self.assertTrue("0101" in result["Product category"].values)
        self.assertTrue("0102" in result["Product category"].values)

    def test_filter_description(self):
        data = {
            "Product category_description": ["Car", "Bicycle", "Truck", "Motorcycle"],
            "Value": [100, 200, 300, 400],
        }
        df = pd.DataFrame(data)
        result = filter_description(df, "Car")
        self.assertEqual(len(result), 1)
        self.assertTrue("Car" in result["Product category_description"].values)

    def test_merge_links(self):
        data = {
            "Exporter": ["A", "A", "B", "B"],
            "Importer": ["C", "C", "D", "D"],
            "Value": [100, 200, 300, 400],
        }
        df = pd.DataFrame(data)
        result = merge_links(df)
        self.assertEqual(len(result), 2)
        self.assertEqual(result.loc[result["Exporter"] == "A", "Value"].values[0], 300)
        self.assertEqual(result.loc[result["Exporter"] == "B", "Value"].values[0], 700)

    def test_add_metadata(self):
        df_left = pd.DataFrame({"Exporter": ["A", "B"], "Value": [100, 200]})
        df_right = pd.DataFrame(
            {"country_code": ["A", "B"], "country_name": ["Country A", "Country B"]}
        )
        result = add_metadata(df_left, df_right, ("Exporter", "country_code"))
        self.assertTrue("Exporter_country_name" in result.columns)
        self.assertEqual(
            result.loc[result["Exporter"] == "A", "Exporter_country_name"].values[0],
            "Country A",
        )
        self.assertEqual(
            result.loc[result["Exporter"] == "B", "Exporter_country_name"].values[0],
            "Country B",
        )

    def test_string2float(self):
        self.assertEqual(string2float("123.45"), 123.45)
        self.assertEqual(string2float("1,234.56"), 1234.56)
        self.assertEqual(string2float("text 123.45 text"), 123.45)

    def test_pandas_2_graph(self):
        data = {
            "Exporter": ["A", "A", "B"],
            "Importer": ["C", "D", "D"],
            "Value": [100, 200, 300],
        }
        df = pd.DataFrame(data)
        graph = pandas_2_graph(df)
        self.assertEqual(len(graph.nodes), 4)
        self.assertEqual(len(graph.edges), 3)


if __name__ == "__main__":
    unittest.main()
