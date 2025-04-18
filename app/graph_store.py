import os

import networkx as nx

from app.logger import logger


class NetworkXGraphStore:
    def __init__(self, file_path):
        self.file_path = file_path
        if os.path.exists(file_path):
            try:
                self.graph = nx.read_graphml(file_path)
                logger.info(f"Knowledge graph loaded from {file_path}")
            except Exception as e:
                logger.error(f"Error loading knowledge graph from {file_path}: {e}")
                self.graph = nx.Graph()
        else:
            self.graph = nx.Graph()
            logger.info("No existing knowledge graph found; creating a new one.")

    def get_node(self, name):
        logger.info(f"Getting node {name}")
        return self.graph.nodes.get(name)

    def get_edge(self, edge):
        logger.info(f"Getting edge {edge}")
        return self.graph.edges.get(edge)

    def get_node_edges(self, name):
        return self.graph.edges(name)

    def add_node(self, name, **kwargs):
        logger.info(f"Adding node {name}")
        self.graph.add_node(name, **kwargs)

    def add_edge(self, source, destination, **kwargs):
        logger.info(f"Adding edge {(source, destination)}")
        self.graph.add_edge(source, destination, **kwargs)

    def degree(self, name):
        return self.graph.degree(name)

    def set_field(self, key, value):
        self.graph.graph[key] = value
        logger.info(f"Graph metadata '{key}' updated to: {value}")

    def save(self):
        nx.write_graphml(self.graph, self.file_path)