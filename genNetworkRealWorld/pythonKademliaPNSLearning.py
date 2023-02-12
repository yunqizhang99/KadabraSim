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
hotspotsList = []

# measure experiment time
startTime = time.time()

G = None

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
		G.add_node(nodeGenerationCounter, pos=(xCoord,yCoord), id=format(nodeGenerationCounter, parameters.NODE_ID_LENGTH_STRING), RLTables = [[[] for i in range(parameters.REINFORCEMENT_LEARNING_TABLE_COLUMNS)] for i in range(parameters.NODE_ID_LENGTH)], buckets=[[] for i in range(parameters.NODE_ID_LENGTH)], epochCounters=[parameters.EPOCH_COUNTERS_INITIAL]*parameters.NODE_ID_LENGTH)
		print("#Graph#: " + "Adding node " + str(nodeGenerationCounter) + " at " + str(xCoord) + ", " + str(yCoord) + " with ID " + G.nodes[nodeGenerationCounter]['id'] + ".\n")
		nodeGenerationCounter = nodeGenerationCounter + 1
	# save the graph if needed
	# nx.write_gpickle(G,'July15Graph.gpickle')

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
while True:
	randomSrc = random.randint(0, parameters.NETWORK_SIZE-1)
	randomDest = None
	if parameters.USE_HOTSPOTS:
		randDestSeed = random.uniform(0, 1)
		if randDestSeed <= parameters.HOTSPOTS_FREQ:
			randomDest = random.choice(hotspotsList)
		else:
			randomDest = random.randint(0, parameters.NETWORK_SIZE-1)
		while randomSrc == randomDest:
			randomDest = random.randint(0, parameters.NETWORK_SIZE-1)
	else:
		randomDest = random.randint(0, parameters.NETWORK_SIZE-1)
	while randomSrc == randomDest:
		randomDest = random.randint(0, parameters.NETWORK_SIZE-1)
	lookupResult = lookupOperations.simpleLookup(G, randomSrc, randomDest, parameters.ALPHA, parameters.LOOKUP_KBR, parameters.LOOKUP_DHT, parameters.DHT_COPIES_NUMBER)
	# while PNSLearningTableCounter < parameters.NODE_ID_LENGTH:
	# 	PNSLearningPathNodeCounter = 1 # first node (node 0) already in bucket
	# 	while PNSLearningPathNodeCounter < len(G.nodes[randomSrc]['RLTables'][PNSLearningTableCounter][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX]:
	# 		currentBucketMaxLatency = -1
	# 		currentBucketMaxLatencyNode = None 
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
					printScoreComputeFlag = 0
					currentScoreDict, currentBucketScore, avgLatency = reinforcementLearning.computeScoreFunc(currentBucketIndex, G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex], currentRLTableDeepCopy)
					currentDictValue = currentScoreDict.values()
					
					PNSLearningEntryCounter = 0
					while PNSLearningEntryCounter < len(G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX]):
						PNSLearningPathNodeCounter = 1 # first node already in bucket
						while PNSLearningPathNodeCounter < len(G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX][PNSLearningEntryCounter]):
							bucketItemCounter = 0
							bucketItemLatencies = {}
							while bucketItemCounter < parameters.BUCKET_SIZE:
								# print(G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex])
								bucketItemBinary = G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex][bucketItemCounter]
								bucketItemDecimal = bucketOperations.binaryToDecimal(int(bucketItemBinary))
								bucketItemLatencies[bucketItemBinary] = dist(G.nodes[RLLoopNodeCounter]['pos'], G.nodes[bucketItemDecimal]['pos'])
								bucketItemCounter += 1
							# print(G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX])
							PNSLearningCandidate = G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX][PNSLearningEntryCounter][PNSLearningPathNodeCounter]
							PNSLearningCandidateLatency = dist(G.nodes[RLLoopNodeCounter]['pos'], G.nodes[PNSLearningCandidate]['pos'])
							if PNSLearningCandidateLatency < max(bucketItemLatencies.values()) and format(PNSLearningCandidate, parameters.NODE_ID_LENGTH_STRING) not in G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex]:
								G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex] = list(map(lambda x: x.replace(max(bucketItemLatencies, key=bucketItemLatencies.get), format(PNSLearningCandidate, parameters.NODE_ID_LENGTH_STRING)), G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex]))
							PNSLearningPathNodeCounter += 1
						PNSLearningEntryCounter += 1

					# clear the tables
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_INITIATOR_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_LATENCY_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['epochCounters'][currentBucketIndex] += 1
					# add termination criteria below or the outer while loop NEVER STOPS
					if RLLoopNodeCounter == 123 and currentBucketIndex == 0:
						print("Node 123 Epoch score: " + str(currentBucketScore) + " latency: " + str(avgLatency) + " RLCounter 123: " + str(G.nodes[RLLoopNodeCounter]['epochCounters'][0]))
						f = open("../../../GitHubExperimentsResults/TestResultAug6_2048_PNSLearning.txt", "a")
						f.write(str(G.nodes[RLLoopNodeCounter]['epochCounters'][0]) + "	" + str(currentBucketScore) + "	" + str(avgLatency) + "\n")
						f.close()
						if G.nodes[RLLoopNodeCounter]['epochCounters'][0] > 100:
							print("100 Epochs for node 123 bucket 0")
							endTime = time.time()
							print("Time consumed: " + str(endTime - startTime))
							sys.exit("Enough Epochs!")  
					# add termination criteria above or the outer while loop NEVER STOPS
				RLLoopNodeCounter += 1








