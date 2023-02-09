import networkx as nx
import random
import matplotlib.pyplot as plt
import bucketOperations
import lookupOperations
import parameters
import math
import time
from datetime import datetime
import copy
import sys
import tracemalloc
import hotspotsGeneration
import reinforcementLearning
import RLParameters
from math import dist

experimentCounter = 0
experimentCounter1 = 0
hotspotsList = []

# measure experiment time
startTime = time.time()
NYCNodes = []

G = nx.read_gpickle(parameters.SAVED_GRAPH_PATH)
print("#Graph#: " + "Using saved graph " + str(parameters.SAVED_GRAPH_PATH))
sum = 0

for node in G:
	if G.nodes[node]['city'] == "NewYork":
		NYCNodes.append(node)
	print(str(node) + "	" + G.nodes[node]['city'] + " " + str(G.nodes[node]['nodeLatency']))
	sum += G.nodes[node]['nodeLatency']

print("Test: " + str(sum/2048))
