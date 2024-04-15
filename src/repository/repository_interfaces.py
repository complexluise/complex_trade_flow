"""This module defines interfaces for the repositories to ensure decoupling between data access and business logic."""

from abc import ABC, abstractmethod

class IGraphDatabaseRepository(ABC):
    """
    Interface for a graph database repository, defining the essential data access operations 
    that can be performed on a graph database.
    """
    
    @abstractmethod
    def add_node(self, node_data):
        pass

    @abstractmethod
    def add_edge(self, start_node, end_node, edge_data):
        pass

    # Add more abstract methods as needed
