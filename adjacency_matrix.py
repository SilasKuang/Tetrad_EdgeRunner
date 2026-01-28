# run in a Python env with pandas & networkx installed
import pandas as pd
import networkx as nx
from pathlib import Path
import re
import matplotlib as plt
import matplotlib.font_manager as fm

# Set font to Arial
fm.fontManager.addfont("ARIAL.TTF")
plt.rcParams['font.family'] = 'Arial'
# Save words as editable text 
plt.rcParams['pdf.fonttype'] = 42   # Use TrueType fonts
plt.rcParams['ps.fonttype'] = 42    # For PostScript too

inp = Path("tetrad_graph.txt")   # text export from Tetrad GUI
edges = []

# regex to remove leading "1. " or "12) "
leading_index_re = re.compile(r'^\s*\d+\s*[\.\)]\s*')

def clean_node(s):
    s = s.strip()
    s = leading_index_re.sub('', s)   # remove numbering
    s = s.rstrip(';, ')               # remove trailing semicolons/commas
    s = s.strip('"').strip("'")       # remove quotes
    return s

lines = inp.read_text().splitlines()

# -------- find where edges start --------
start_idx = 0
for i, L in enumerate(lines):
    if L.strip().lower().startswith("graph edges:"):
        start_idx = i + 1
        break

for line in lines[start_idx:]:
    line = line.strip()
    if not line:
        continue

    # stop if graph attributes start
    if line.lower().startswith("graph attributes"):
        break

for line in lines[start_idx:]:
    line = line.strip()
    if not line:
        continue
    if line.lower().startswith("graph nodes:"):
        continue

    if "-->" in line:
        a,b = [clean_node(s) for s in line.split("-->",1)]
        edges.append((a,b,"directed"))
    elif "<--" in line:
        b,a = [clean_node(s) for s in line.split("<--",1)]
        edges.append((a,b,"directed"))
    elif "---" in line:
        a,b = [clean_node(s) for s in line.split("---",1)]
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
        G.add_edge(s,t)
        G.add_edge(t,s)

adj = nx.to_pandas_adjacency(G, dtype=int)
adj.to_csv("tetrad_adjacency_matrix.csv")

print("Wrote tetrad_edges.csv and tetrad_adjacency_matrix.csv")
