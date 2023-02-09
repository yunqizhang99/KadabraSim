import networkx as nx
import random
import matplotlib.pyplot as plt
import parameters 
import time
import edgeOperations as eo
import pandas
import sys
# from mpl_toolkits.basemap import Basemap

G = nx.Graph()
GPNS = nx.Graph()

terminalCounter = 0
nodeIDsCollector = []
terminalIDDic = {}
observationNode = -1

citiesCSVRead = pandas.read_csv("cityAndLoc2500Nodes03012022UpdatedWonderNetwork.csv")
citiesUniqueCSVRead = pandas.read_csv("cityUnique.csv")
cities = citiesCSVRead['City'].tolist()
citiesUnique = citiesUniqueCSVRead['CityUnique'].tolist()
citiesUniqueLat = citiesUniqueCSVRead['Lat'].tolist()
citiesUniqueLon = citiesUniqueCSVRead['Lon'].tolist()
print("CITYUNIQUE: " + str(citiesUnique))
locationDic = {}
citiesUniqueCounter = 0
while citiesUniqueCounter < len(citiesUnique):
	locationDic[citiesUnique[citiesUniqueCounter]] = [citiesUniqueLat[citiesUniqueCounter], citiesUniqueLon[citiesUniqueCounter]]
	citiesUniqueCounter += 1
print("LOCATIONDIC: " + str(locationDic))

# m = Basemap(projection='robin',lon_0=0,resolution='c')

# Generate nodes 
while terminalCounter < parameters.NETWORK_SIZE:
	currentCity = cities.pop(0)
	location = locationDic[currentCity]
	# xpt,ypt = m(float(location[1]),float(location[0]))
	G.add_node(terminalCounter, id=format(terminalCounter, parameters.NODE_ID_LENGTH_STRING), city=currentCity, nodeLatency=0, RLTables = [[[] for i in range(parameters.REINFORCEMENT_LEARNING_TABLE_COLUMNS)] for i in range(parameters.NODE_ID_LENGTH)], buckets=[[] for i in range(parameters.NODE_ID_LENGTH)], prevBuckets=[[] for i in range(parameters.NODE_ID_LENGTH)], prevScores=[-1]*parameters.NODE_ID_LENGTH, bucketChangeItemFlags=[parameters.RLCHANGEITEMFLAGS_INITIAL]*parameters.NODE_ID_LENGTH, epochCounters=[parameters.EPOCH_COUNTERS_INITIAL]*parameters.NODE_ID_LENGTH)
	# GPNS.add_node(terminalCounter, id=format(currentNodeID, "0160b"), city=currentCity, pos=(xpt, ypt), buckets=[[] for i in range(160)])
	# terminalIDDic[format(currentNodeID, "0160b")] = terminalCounter
	if parameters.USE_AREA_WITH_HIGH_NODE_LATENCY:
		if currentCity == parameters.HNL_CITY:
			G.nodes[terminalCounter]['nodeLatency'] = parameters.HIGH_NODE_LATENCY
			if observationNode == -1:
				observationNode = terminalCounter
		else:
			G.nodes[terminalCounter]['nodeLatency'] = random.choice(parameters.NODE_LATENCY_UNIFORM)
	else:
		G.nodes[terminalCounter]['nodeLatency'] = random.choice(parameters.NODE_LATENCY_UNIFORM)
	print("---------Node Generation---------")
	print(str(terminalCounter))
	print(G.nodes[terminalCounter]['id'])
	print(G.nodes[terminalCounter]['city'])
	# print(G.nodes[terminalCounter]['pos'])
	terminalCounter += 1

eo.buildEdges(G)

print("!observationNode: " + str(observationNode))

nx.write_gpickle(G,'Aug18Graph_2048_NDRW_HNL.gpickle')
