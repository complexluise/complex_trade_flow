class Neo4jQueryManager:

    @staticmethod
    def find_trades() -> str:
        return """
        MATCH (c:Country {iso3: $iso3})-[r:EXPORTS_TO]->(other)
        RETURN other.iso3 AS country, r.product_category AS product, r.year AS year, r.value AS value, r.quantity AS quantity
        """

    @staticmethod
    def get_trading_partners() -> str:
        """
        Retrieves all trading partners for a given country.

        Args:
        country_iso3 (str): The ISO3 code of the country.

        Returns:
        list of dicts: Trading partners and the details of the trades.
        """
        return """
        MATCH (c:Country {iso3: $iso3})-[r:EXPORTS_TO]->(partner:Country)
        RETURN partner.name AS partner_country, collect({product_category: r.product_category, year: r.year, value: r.value, quantity: r.quantity}) AS trades
        """

    @staticmethod
    def summarize_trade_by_product() -> str:
        """
        Summarizes trade values by product categories for a given country.

        Args:
        country_iso3 (str): The ISO3 code of the country.

        Returns:
        list of dicts: Sum of values and quantities grouped by product categories.
        """
        return """
        MATCH (c:Country {iso3: $iso3})-[r:EXPORTS_TO]->(partner:Country)
        RETURN r.product_category AS product_category, sum(r.value) AS total_value, sum(r.quantity) AS total_quantity
        GROUP BY r.product_category
        ORDER BY total_value DESC
        """

    @staticmethod
    def get_country_trade_volume() -> str:
        """
        Retrieves the total trade volume for all countries for a given year.

        Args:
        year (int): The year of the trade.

        Returns:
        list of dicts: Countries and their total trade volume in the given year.
        """
        return """
        MATCH (c:Country)-[r:EXPORTS_TO {year: $year}]->(partner:Country)
        RETURN c.name AS country, sum(r.value) AS total_exports
        GROUP BY c.name
        ORDER BY total_exports DESC
        """
