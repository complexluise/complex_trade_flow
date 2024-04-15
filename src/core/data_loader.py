import networkx as nx
from typing import List, Dict
from src.models.pydantic_models import TradeData


class DataLoader:
    @staticmethod
    def load_to_graph(data: List[Dict]) -> nx.DiGraph:
        G = nx.DiGraph()
        for item in data:
            # Here you'd load data into your graph database, for now we'll just build a NetworkX graph
            G.add_edge(item["exporter"], item["importer"], weight=item["value"])
        return G
