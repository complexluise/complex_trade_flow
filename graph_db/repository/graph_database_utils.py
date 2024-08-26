class Neo4jQueryManager:
    @staticmethod
    def add_country():
        return """
        MERGE (c:Country {id: $id})
        ON CREATE SET c.iso2 = $iso2, c.name = $name, c.capital_city = $capital_city,
                      c.longitude = $longitude, c.latitude = $latitude
        ON MATCH SET c.iso2 = $iso2, c.name = $name, c.capital_city = $capital_city,
                     c.longitude = $longitude, c.latitude = $latitude
        """

    @staticmethod
    def create_or_merge_region():
        return """
        // Merge the region node and create or update its properties
        MERGE (r:Region {id: $id})
        ON CREATE SET r.iso2code = $iso2code, r.value = $value
        ON MATCH SET r.iso2code = $iso2code, r.value = $value
        
        // Establish a relationship from Country to Region
        // Assumes $country_id is provided correctly referencing an existing Country node
        MERGE (c:Country {id: $country_id})
        MERGE (c)-[:BELONGS_TO]->(r)
        """

    @staticmethod
    def create_or_merge_admin_region():
        return """
        // Merge the admin region node and create or update its properties
        MERGE (ar:AdminRegion {id: $id})
        ON CREATE SET ar.iso2code = $iso2code, ar.value = $value
        ON MATCH SET ar.iso2code = $iso2code, ar.value = $value

        // Establish a relationship from Country to AdminRegion
        // Assumes $country_id is provided correctly referencing an existing Country node
        MERGE (c:Country {id: $country_id})
        MERGE (c)-[:HAS_ADMIN_REGION]->(ar)
        """

    @staticmethod
    def create_or_merge_income_level():
        return """
        // Merge the admin region node and create or update its properties
        MERGE (il:IncomeLevel {id: $id})
        ON CREATE SET il.iso2code = $iso2code, il.value = $value
        ON MATCH SET il.iso2code = $iso2code, il.value = $value

        // Establish a relationship from Country to Income Level
        // Assumes $country_id is provided correctly referencing an existing Country node
        MERGE (c:Country {id: $country_id})
        MERGE (c)-[:HAS_INCOME]->(il)
        """

    @staticmethod
    def create_or_merge_lending_type():
        return """
        // Merge the lending type node and create or update its properties
        MERGE (lt:LendingType {id: $id})
        ON CREATE SET lt.iso2code = $iso2code, lt.value = $value
        ON MATCH SET lt.iso2code = $iso2code, lt.value = $value

        // Establish a relationship from Country to Lending Type
        // Assumes $country_id is provided correctly referencing an existing Country node
        MERGE (c:Country {id: $country_id})
        MERGE (c)-[:HAS_LENDING]->(lt)
        """

    @staticmethod
    def create_trade_data():
        return """
        MERGE (exporter)-[trade:EXPORTS_TO {year: row.year}]->(importer)
        ON CREATE SET trade.money = toFloat(row.money), trade.mass = toFloat(row.mass);
        """
