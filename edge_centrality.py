# Requires: networkx, pandas, numpy, matplotlib, scipy (optional), seaborn (optional)
import networkx as nx
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter
from matplotlib.ticker import MaxNLocator
import matplotlib as plt
import matplotlib.font_manager as fm

# Set font to Arial
fm.fontManager.addfont("ARIAL.TTF")
plt.rcParams['font.family'] = 'Arial'
# Save words as editable text 
plt.rcParams['pdf.fonttype'] = 42   # Use TrueType fonts
plt.rcParams['ps.fonttype'] = 42    # For PostScript too

# -------------- load edge list (adapt names/formats as needed) ------------
edges = pd.read_csv("tetrad_edges.csv")  # columns: source,target[,weight]
# If your file has 'A -> B' strings, preprocess into two columns first.

# detect directed/weighted
directed = False  # set True if you want directed only
if 'weight' in edges.columns:
    weighted = True
else:
    weighted = False

if directed:
    G = nx.DiGraph()
else:
    G = nx.Graph()

if weighted:
    for r in edges.itertuples(index=False):
        G.add_edge(r[0], r[1], weight=r[2])
else:
    for r in edges.itertuples(index=False):
        G.add_edge(r[0], r[1])

# -------------- centralities / hub stats --------------------------------
if weighted:
    # weighted degree (sum of edge weights)
    degree_dict = dict(G.degree(weight='weight'))
else:
    degree_dict = dict(G.degree())

# other centralities (compute a subset for publication)
betw = nx.betweenness_centrality(G)           # may be slow for very large graphs
try:
    eig = nx.eigenvector_centrality_numpy(G)  # fast numeric
except Exception:
    eig = {n: np.nan for n in G.nodes()}

# assemble table
df = pd.DataFrame({
    'node': list(degree_dict.keys()),
    'degree': list(degree_dict.values()),
    'betweenness': [betw[n] for n in degree_dict.keys()],
    'eig': [eig.get(n, np.nan) for n in degree_dict.keys()]
})
df = df.sort_values('degree', ascending=False).reset_index(drop=True)
df.to_csv("node_centrality_table.csv", index=False)
print("Saved node_centrality_table.csv")

# -------------- top-N barplot --------------------------------------------
topN = 20
top_df = df.head(topN).iloc[::-1]

plt.figure(figsize=(5,3.5))
bars = plt.barh(top_df['node'], top_df['degree'])

plt.xlabel('Degree')
plt.title(f'Top {topN} hub nodes by degree')

# force integer ticks
plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))

# add value labels to bars
for bar in bars:
    w = bar.get_width()
    plt.text(w + 0.1, bar.get_y() + bar.get_height()/2,
             f'{int(w)}', va='center', fontsize=8)

plt.tight_layout()
plt.savefig("topN_hubs_barplot.pdf", dpi=300)
plt.close()

# -------------- network diagram (publication ready) ----------------------
# node sizes scaled from degree
deg = np.array([degree_dict[n] for n in G.nodes()])
# simple scaling: min size 50, max size 2000 (tweak)
min_s, max_s = 60, 2000
if deg.max()==deg.min():
    sizes = np.full_like(deg, 200)
else:
    sizes = min_s + (deg - deg.min())/(deg.max()-deg.min())*(max_s-min_s)

# position: spring layout is common; for reproducibility set seed
pos = nx.spring_layout(G, seed=42, k=None)  # k=None lets algorithm choose
plt.figure(figsize=(8,8))
nx.draw_networkx_nodes(G, pos, node_size=sizes, alpha=0.85)
nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.5)
# label only top few hubs to avoid clutter:
label_nodes = list(df['node'].head(20))
nx.draw_networkx_labels(G, pos, labels={n:n for n in label_nodes}, font_size=8)
plt.axis('off')
plt.title('Network with node size ∝ degree (top hubs labeled)')
plt.tight_layout()
plt.savefig("network_hubs_plot.pdf", dpi=300)
plt.close()

# -------------- adjacency heatmap sorted by degree (optional) ------------
nodes_sorted = list(df['node'])  # already sorted by degree descending
A = nx.to_numpy_array(G, nodelist=nodes_sorted)  # adjacency matrix
# use matplotlib imshow (or seaborn.heatmap) for a publication-ready image
plt.figure(figsize=(6,6))
plt.imshow(A, interpolation='nearest', aspect='auto')
plt.colorbar(label='edge presence (or weight)')
plt.title('Adjacency matrix (nodes sorted by degree)')
plt.xticks(range(len(nodes_sorted)), nodes_sorted, rotation=90, fontsize=6)
plt.yticks(range(len(nodes_sorted)), nodes_sorted, fontsize=6)
plt.tight_layout()
plt.savefig("adjacency_heatmap_sorted.pdf", dpi=300)
plt.close()
