from py2neo import Graph, Node, Relationship

from src.repository.graph_database_repository import Neo4jQueryManager


class GraphDatabaseRepository:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="test"):
        self.graph = Graph(uri, auth=(user, password))

    def add_country(self, iso3: str, name: str):
        country = Node("Country", iso3=iso3, name=name)
        self.graph.merge(country, "Country", "iso3")

    def add_trade_relation(
        self,
        exporter_iso3: str,
        importer_iso3: str,
        product_category: str,
        year: int,
        value: float,
        quantity: float,
    ):
        exporter = Node("Country", iso3=exporter_iso3)
        importer = Node("Country", iso3=importer_iso3)
        relationship = Relationship(
            exporter,
            "EXPORTS_TO",
            importer,
            product_category=product_category,
            year=year,
            value=value,
            quantity=quantity,
        )
        self.graph.merge(relationship, "EXPORTS_TO", "product_category", "year")

    def find_trades(self, iso3: str):
        return self.graph.run(Neo4jQueryManager.find_trades, iso3=iso3).data()


# Usage of the repository
if __name__ == "__main__":
    repo = GraphDatabaseRepository()
    repo.add_country("USA", "United States of America")
    repo.add_country("CAN", "Canada")
    repo.add_trade_relation("USA", "CAN", "Electronics", 2021, 500000, 400)

    print(repo.find_trades("USA"))
