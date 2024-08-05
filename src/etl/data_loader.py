import networkx as nx
from src.models.pydantic_models import Country, HarmonizedCategory
from src.repository.graph_database_repository import GraphDatabaseRepository


class DataLoader:
    @staticmethod
    def load_countries_to_neo4j(countries: list[Country]):
        graph_db = GraphDatabaseRepository()
        for country in countries:
            print("Processing", country.id)
            graph_db.add_country(country)

    @staticmethod
    def load_products_categories_to_neo4j(products: list[HarmonizedCategory]):
        graph_db = GraphDatabaseRepository()
        for product in products:
            print("Processing", product.code)
            graph_db.add_product(product)
        pass
