import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

from src.models.pydantic_models import Country, HarmonizedCategory
from src.repository.graph_database_utils import Neo4jQueryManager

load_dotenv()


class GraphDatabaseRepository:
    def __init__(self,
                 uri=os.getenv("NEO4J_URI"),
                 user=os.getenv("NEO4J_USERNAME"),
                 password=os.getenv("NEO4J_PASSWORD")
                 ):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def _execute_query(self, query: str, parameters=None):
        with self.driver.session() as session:
            session.write_transaction(lambda tx: tx.run(query, parameters))

    def _add_country(self, country: Country):
        query = Neo4jQueryManager.add_country()
        self._execute_query(query, country.dict())

    def _create_or_merge_region(self, country: Country):
        if country.region:
            params = {**country.region.dict(), "country_id": country.id}
            query = Neo4jQueryManager.create_or_merge_region()
            self._execute_query(query, params)

    def _create_or_merge_admin_region(self, country: Country):
        if country.admin_region.id:
            params = {**country.admin_region.dict(), "country_id": country.id}
            query = Neo4jQueryManager.create_or_merge_admin_region()
            self._execute_query(query, params)

    def _create_or_merge_income_level(self, country: Country):
        if country.income_level.id:
            params = {**country.income_level.dict(), "country_id": country.id}
            query = Neo4jQueryManager.create_or_merge_income_level()
            self._execute_query(query, params)

    def _create_or_merge_lending_type(self, country: Country):
        if country.lending_type.id:
            params = {**country.lending_type.dict(), "country_id": country.id}
            query = Neo4jQueryManager.create_or_merge_lending_type()
            self._execute_query(query, params)

    def add_country(self, country: Country):
        self._add_country(country)
        self._create_or_merge_region(country)
        # Only Region
        #self._create_or_merge_admin_region(country)
        #self._create_or_merge_income_level(country)
        #self._create_or_merge_lending_type(country)

    def add_product(self, product: HarmonizedCategory):
        pass



    def close(self):
        self.driver.close()
