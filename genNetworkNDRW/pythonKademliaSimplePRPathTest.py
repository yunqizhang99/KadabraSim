import networkx as nx
import random
import matplotlib.pyplot as plt
import bucketOperations
import lookupOperations
import parametersPT as parameters 
import math
import time
from datetime import datetime
import copy
import sys
import tracemalloc
import hotspotsGeneration
import reinforcementLearning
import RLParameters

experimentCounter = 0
hotspotsList = []

# measure experiment time
startTime = time.time()

G = None

observationNode = 123

if parameters.USE_SAVED_GRAPH:
	G = nx.read_gpickle(parameters.SAVED_GRAPH_PATH)
	print("#Graph#: " + "Using saved graph " + str(parameters.SAVED_GRAPH_PATH))
else:
	# initialize networkx graph G
	G = nx.Graph()
	# generate nodes and add them to G
	nodeGenerationCounter = 0
	while nodeGenerationCounter < parameters.NETWORK_SIZE: 
		xCoord = random.uniform(parameters.MIN_X_COORD, parameters.MAX_X_COORD)
		yCoord = random.uniform(parameters.MIN_Y_COORD, parameters.MAX_Y_COORD)
		G.add_node(nodeGenerationCounter, pos=(xCoord,yCoord), id=format(nodeGenerationCounter, parameters.NODE_ID_LENGTH_STRING), nodeLatency=0, RLTables = [[[] for i in range(parameters.REINFORCEMENT_LEARNING_TABLE_COLUMNS)] for i in range(parameters.NODE_ID_LENGTH)], buckets=[[] for i in range(parameters.NODE_ID_LENGTH)], prevBuckets=[[] for i in range(parameters.NODE_ID_LENGTH)], prevScores=[-1]*parameters.NODE_ID_LENGTH, bucketChangeItemFlags=[parameters.RLCHANGEITEMFLAGS_INITIAL]*parameters.NODE_ID_LENGTH, epochCounters=[parameters.EPOCH_COUNTERS_INITIAL]*parameters.NODE_ID_LENGTH)
		if parameters.USE_AREA_WITH_HIGH_NODE_LATENCY:
			if xCoord >= parameters.HIGH_NODE_LATENCY_RECTANGLE[0] and xCoord <= parameters.HIGH_NODE_LATENCY_RECTANGLE[1] and yCoord >= parameters.HIGH_NODE_LATENCY_RECTANGLE[2] and yCoord <= parameters.HIGH_NODE_LATENCY_RECTANGLE[3]:
				G.nodes[nodeGenerationCounter]['nodeLatency'] = parameters.HIGH_NODE_LATENCY
				if observationNode == -1:
					observationNode = nodeGenerationCounter
			else:
				G.nodes[nodeGenerationCounter]['nodeLatency'] = random.choice(parameters.NODE_LATENCY_UNIFORM)
		else:
			G.nodes[nodeGenerationCounter]['nodeLatency'] = random.choice(parameters.NODE_LATENCY_UNIFORM)
		print("#Graph#: " + "Adding node " + str(nodeGenerationCounter) + " at " + str(xCoord) + ", " + str(yCoord) + " with ID " + G.nodes[nodeGenerationCounter]['id'] + ".\n")
		nodeGenerationCounter = nodeGenerationCounter + 1
	# save the graph if needed
	# nx.write_gpickle(G,'July30Graph_HighLatency.gpickle')

# plt.figure(3,figsize=(12,12)) 
# posDraw = nx.get_node_attributes(G,'pos')
# nx.draw(G,posDraw,node_size=30, node_color='red')
# plt.savefig("EDNS_Demo.pdf", format="PDF")

if parameters.USE_HOTSPOTS:
	print("#Hotspots#: using hotspots")
	if parameters.USE_SAVED_HOTSPOTS:
		hotspotsList = parameters.SAVED_HOTSPOTS_2048
		print("#Hotspots#: using saved hotspots")
	else:
		# generate hotspots 
		print("#Hotspots#: using random hotspots")
		hotspotsList = hotspotsGeneration.hotspotsGenerationFunc(parameters.HOTSPOTS_RANGE_LOWER_BOUND, parameters.HOTSPOTS_RANGE_UPPER_BOUND, parameters.HOTSPOTS_NUMBER)
		# save the hotspots if needed
		# print("#Hotspots#: List: " + str(hotspotsList))

# populate the buckets of G randomly (another option is to use PNS in bucketOperations.py)
if parameters.BUCKET_POPULATION_METHOD == "RANDOM":
	bucketOperations.fillAllBucketsRandom(G)
elif parameters.BUCKET_POPULATION_METHOD == "PNS":
	bucketOperations.fillAllBucketsPNS(G)

# keep running until enough epochs
srcDestPairFile = open('lookupSrcDestPairs1k.txt', 'r')
srcDestPairLines = srcDestPairFile.readlines()

for line in srcDestPairLines:
	srcDestList = line.split()
	randomSrc = int(srcDestList[0])
	randomDest = int(srcDestList[1])
	
	lookupResult = lookupOperations.simpleLookup(G, randomSrc, randomDest, parameters.ALPHA, parameters.LOOKUP_KBR, parameters.LOOKUP_DHT, parameters.DHT_COPIES_NUMBER)
	f = open("PathTestPROct9_Case2.txt", "a")
	# f1 = open("../../../GitHubExperimentsResults/TestResultSep5_2048_SimplePNS_10NL_TestNodeLatency.txt", "a")
	# f.write(str(randomSrc) + "	" + str(randomDest) + "	" + str(lookupResult[2]) + "	" + str(min(len(lookupResult[2][0]), len(lookupResult[2][1]))) + "\n")
	minLatencyIndex = lookupResult[0].index(min(lookupResult[0]))
	citiesString = ""
	citiesStringCounter = 0
	latenciesString = ""
	nodeLatenciesString = ""
	while citiesStringCounter < len(lookupResult[2][minLatencyIndex]):
		if citiesStringCounter == 0:
			citiesString += str(G.nodes[lookupResult[2][minLatencyIndex][0][0]]['city'])
			citiesString += "	"
			citiesString += str(G.nodes[lookupResult[2][minLatencyIndex][0][1]]['city'])
			citiesString += "	"
			latenciesString += str(G[lookupResult[2][minLatencyIndex][0][0]][lookupResult[2][minLatencyIndex][0][1]]['weight'])
			latenciesString += "	"
			nodeLatenciesString += str(G.nodes[lookupResult[2][minLatencyIndex][0][1]]['nodeLatency'])
			nodeLatenciesString += "	"
		else:
			citiesString +=  str(G.nodes[lookupResult[2][minLatencyIndex][citiesStringCounter][1]]['city'])
			citiesString += "	"
			latenciesString += str(G[lookupResult[2][minLatencyIndex][citiesStringCounter][0]][lookupResult[2][minLatencyIndex][citiesStringCounter][1]]['weight'])
			latenciesString += "	"
			nodeLatenciesString += str(G.nodes[lookupResult[2][minLatencyIndex][citiesStringCounter][1]]['nodeLatency'])
			nodeLatenciesString += "	"
		citiesStringCounter += 1
	f.write(str(min(lookupResult[0])) + "	" + citiesString + "	" + latenciesString + "	" + nodeLatenciesString + "\n")
	# sumNodeLatency = 0
	# for node in lookupResult[2][minLatencyIndex]:
	# 	sumNodeLatency += G.nodes[node[1]]['nodeLatency']
	# avgNodeLatency = sumNodeLatency/len(lookupResult[2][minLatencyIndex])
	# f1.write(str(avgNodeLatency) + "\n")
	# f.write(str(lookupResult) + "\n")
	f.close()
	# f1.close()
	experimentCounter += 1
	if experimentCounter == parameters.CHECK_BUCKETS_FREQ:
		experimentCounter = 0
		bucketsToRunRL = copy.deepcopy(parameters.BUCKETS_TO_RUN_RL)
		while len(bucketsToRunRL) > 0:
			currentBucketIndex = bucketsToRunRL.pop()
			RLLoopNodeCounter = 0
			while RLLoopNodeCounter < parameters.NETWORK_SIZE:
				if len(G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX]) >= parameters.EPOCH_QUERIES_NUMBER:
					currentRLTableDeepCopy = copy.deepcopy(G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex])
					currentScoreDict, currentBucketScore, avgLatency = reinforcementLearning.computeScoreFunc(currentBucketIndex, G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex], currentRLTableDeepCopy)
					currentDictValue = currentScoreDict.values()

					# clear the tables
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_INITIATOR_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_LATENCY_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['epochCounters'][currentBucketIndex] += 1
					# add termination criteria below or the outer while loop NEVER STOPS
					if RLLoopNodeCounter == observationNode and currentBucketIndex == 0:
						print("Node " + str(RLLoopNodeCounter) + " Epoch score: " + str(currentBucketScore) + " latency: " + str(avgLatency) + " RLCounter: " + str(G.nodes[RLLoopNodeCounter]['epochCounters'][0]))
						f = open("../../../GitHubExperimentsResults/TestResultSep4_2048_SimplePR_KBR_10NLTest.txt", "a")
						f.write(str(G.nodes[RLLoopNodeCounter]['epochCounters'][0]) + "	" + str(currentBucketScore) + "	" + str(avgLatency) + "\n")
						f.close()
						if G.nodes[RLLoopNodeCounter]['epochCounters'][0] > 100:
							print("100 Epochs for node " + str(RLLoopNodeCounter) + " bucket 0")
							endTime = time.time()
							print("Time consumed: " + str(endTime - startTime))
							sys.exit("Enough Epochs!")  
					# add termination criteria above or the outer while loop NEVER STOPS
				RLLoopNodeCounter += 1








