import pandas as pd
import networkx as nx
import numpy as np

# Read the edge list and convert it to a network
edges = pd.read_csv("all_edges.csv")
F = nx.from_pandas_dataframe(edges, 'node_1', 'node_2')

# Read node lists
officers = pd.read_csv("Officers.csv").set_index('node_id')
intermediaries = pd.read_csv("Intermediaries.csv").set_index('node_id')
addresses = pd.read_csv("Addresses.csv").set_index('node_id')
entities = pd.read_csv("Entities.csv", low_memory=False).set_index('node_id')

# Combine the node lists into one dataframe
officers["type"] = "officer"
intermediaries["type"] = "intermediary"
addresses["type"] = "address"
entities["type"] = "entity"

all_nodes = pd.concat([officers, intermediaries, addresses, entities])

# Do some cleanup of names
all_nodes['name'] = all_nodes['name'].str.upper()
all_nodes['name'] = all_nodes['name'].str.strip()

all_nodes['name'].replace(to_replace=[r'MRS?\.\s+', r'\.', r'\s+', 'LIMITED'], 
                          value=['', '', ' ', 'LTD'], inplace=True, 
                          regex=True)
# Ensure that all "Bearers" do not become a single node
all_nodes.loc[all_nodes.name == 'THE BEARER']['name'] = np.nan

# The network is ready to use
# As an exercise, let's have a look at Mr.Roldugin's or Mr. Poroshenko's assets
seeds = [12079386, 12096275, 12180773] # Roldugin
seeds = [12129717, 13001828] # Poroshenko
nodes_of_interest = set.union(*[set(nx.single_source_shortest_path_length(F, x, cutoff=4).keys()) for x in seeds])

# Extract the subgraph and relabel it
ego = nx.subgraph(F, nodes_of_interest)

nodes = all_nodes.ix[ego.nodes()]
nx.set_node_attributes(ego, "cc", nodes.country_codes)
ego = nx.relabel_nodes(ego, nodes[nodes.name.notnull()].name)
ego = nx.relabel_nodes(ego, nodes[nodes.address.notnull() 
                                    & nodes.name.isnull()].address)

# Must be negative: that's what OFFSHORES are about!
print("Country code assortativity:",
      nx.attribute_assortativity_coefficient(ego,'cc'))

# Save and proceed to Gephi
with open('ego.graphml', 'wb') as ofile: 
    nx.write_graphml(ego, ofile)
