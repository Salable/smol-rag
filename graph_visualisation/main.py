import pandas as pd
from jaal import Jaal

from app.definitions import KG_DB
from app.graph_store import NetworkXGraphStore

if __name__ == "__main__":
    store = NetworkXGraphStore(KG_DB)
    G = store.graph  # NetworkX graph

    # Convert to edge DataFrame with columns 'from', 'to' (and optionally edge attributes)
    edge_df = pd.DataFrame(
        [(u, v, *d.values()) for u, v, d in G.edges(data=True)],
        columns=['from', 'to'] + list(next(iter(G.edges(data=True)))[2].keys()) if G.number_of_edges() > 0 else ['from', 'to']
    )

    # Convert to node DataFrame with at least "id" column (and optionally node attributes)
    node_df = pd.DataFrame(
        [(n, *d.values()) for n, d in G.nodes(data=True)],
        columns=['id'] + list(next(iter(G.nodes(data=True)))[1].keys()) if G.number_of_nodes() > 0 else ['id']
    )

    # Pass DataFrames to Jaal
    Jaal(edge_df, node_df).plot()