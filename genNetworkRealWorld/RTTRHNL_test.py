import networkx as nx
import random
import matplotlib.pyplot as plt
import bucketOperations
import lookupOperations
import parametersCase5CDF as parameters 
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

for node in G:
	if G.nodes[node]['city'] == "NewYork":
		NYCNodes.append(node)
	print(str(node) + "	" + G.nodes[node]['city'] + " " + str(G.nodes[node]['nodeLatency']))

print(NYCNodes)

srcDestPairFileHNL_NewYork = open('lookupSrcDestPairs_HNL_NewYork.txt', 'a')

pairFileCounter = 0
while pairFileCounter < 10000000:
	src = random.choice(NYCNodes)
	dest = random.randint(0, parameters.NETWORK_SIZE-1)
	while src == dest:
		dest = random.randint(0, parameters.NETWORK_SIZE-1)
	srcDestPairFileHNL_NewYork.write(str(src) + "	" + str(dest) + "\n")
	pairFileCounter += 1