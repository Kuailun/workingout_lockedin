# -*- coding: utf-8 -*-
# @File       : 06_descriptive analysis.py
# @Author     : Yuchen Chai
# @Date       : 2022/12/27 10:36
# @Description:


# ------------------------
# define global settings
# ------------------------
SETTING_PIPELINE_NAME = "130_strava network experiment"

# ------------------------
# import packages
# ------------------------
import traceback
import requests
import time
import os
import numpy as np
import json
import geopandas
import pandas as pd
import networkx as nx
import nxviz as nv
from tqdm import tqdm
import rasterio as rs
from multiprocessing import Process
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import collections

DIR_HOME = "XXXXXX"
DIR_CURRENT = os.getcwd()
DIR_PIPELINE = os.path.join(DIR_HOME, "2_pipeline", SETTING_PIPELINE_NAME)
if not os.path.exists(DIR_PIPELINE):
    os.mkdir(DIR_PIPELINE)
    os.mkdir(os.path.join(DIR_PIPELINE, "out"))
    os.mkdir(os.path.join(DIR_PIPELINE, "store"))
    os.mkdir(os.path.join(DIR_PIPELINE, "temp"))

# ------------------------
# read data
# ------------------------
dta = pd.read_csv(os.path.join(DIR_PIPELINE, 'store\\USA MA Middlesex cleaned.csv'))

# ------------------------
# process data
# ------------------------
gnw = nx.DiGraph()

# Establish network
for idx, row in dta.iterrows():
    gnw.add_edge(row['original_user_id'], row['target_user_id'])

# Graph properties
nodes = gnw.number_of_nodes()
edges = gnw.number_of_edges()
avg_deg = edges / nodes
edge_density = edges / (nodes * (nodes - 1))

print(f"Nodes: {nodes}")
print(f"Edges: {edges}")
print(f"Average degree: {avg_deg}")
print(f"Edge density: {edge_density}")


# Connected components
def generate_connected_components(g):
    c = nx.number_weakly_connected_components(g)
    print(f"Number of connected components: {c}")
    print(f"Average size of connected components: {nodes / c}")

    num_of_components = []
    for c in nx.weakly_connected_components(g):
        num_of_components.append(len(c))

    c = collections.Counter(num_of_components)
    x = c.keys()
    y = c.values()
    plt.figure(figsize=(16, 8))
    sns.set_style("ticks")
    sns.scatterplot(x=x, y=y)
    plt.title("Connected component distribution", fontsize=16)
    plt.xlabel("Component size", fontsize=16)
    plt.ylabel("Number of components", fontsize=16)
    plt.xscale('log')
    plt.yscale('log')
    # 移除上面及右边的黑色直线
    sns.despine(offset=10)
    plt.show()


# generate_connected_components(gnw)


# Degree distribution
def generate_degree_distribution(g):
    degree_sequence = sorted([d for n, d in g.in_degree], reverse=True)

    plt.figure(figsize=(16, 8))
    sns.set_style("ticks")
    sns.histplot(x=degree_sequence)
    plt.title("Degree distribution", fontsize=16)
    plt.xlabel("Number of in degrees", fontsize=16)
    plt.ylabel("Frequency", fontsize=16)
    plt.xscale('log')
    plt.yscale('log')
    # 移除上面及右边的黑色直线
    sns.despine(offset=10)
    plt.show()


# generate_degree_distribution(gnw)


# Centrality
def generate_centrality(g):
    # Degree centrality
    dc = nx.degree_centrality(g)

    # Closeness centrality
    cc = nx.closeness_centrality(g)

    # Betweenness centrality
    bc = nx.betweenness_centrality(g)

    # Eigenvector centrality
    ec = nx.eigenvector_centrality(g)

    # Katz centrality
    kc = nx.katz_centrality(g)

    print(1)

generate_centrality(gnw)
