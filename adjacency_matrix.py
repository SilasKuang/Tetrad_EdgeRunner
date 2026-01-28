# run in a Python env with pandas & networkx installed
import pandas as pd
import networkx as nx
from pathlib import Path

inp = Path("tetrad_graph.txt")   # text export from Tetrad GUI
edges = []
with inp.open() as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # handle forms like: A -> B  or  A <-- B  or  A - B
        if "->" in line:
            a,b = [s.strip() for s in line.split("->",1)]
            edges.append((a,b,"directed"))
        elif "<-" in line:
            b,a = [s.strip() for s in line.split("<-",1)]
            edges.append((a,b,"directed"))
        elif "-" in line:
            a,b = [s.strip() for s in line.split("-",1)]
            edges.append((a,b,"undirected"))
# save edge list
edge_df = pd.DataFrame(edges, columns=["source","target","type"])
edge_df.to_csv("tetrad_edges.csv", index=False)

# build adjacency matrix (directed)
G = nx.DiGraph()
G.add_nodes_from(sorted(set(edge_df["source"]).union(edge_df["target"])))
for s,t,typ in edges:
    if typ == "directed":
        G.add_edge(s,t)
    else:
        G.add_edge(s,t); G.add_edge(t,s)
adj = nx.to_pandas_adjacency(G, dtype=int)
adj.to_csv("tetrad_adjacency_matrix.csv")
print("Wrote tetrad_edges.csv and tetrad_adjacency_matrix.csv")
