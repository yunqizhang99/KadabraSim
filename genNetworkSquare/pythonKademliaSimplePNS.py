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

experimentCounter = 0
hotspotsList = []

# measure experiment time
startTime = time.time()

G = None

observationNode = 78

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
	nx.write_gpickle(G,'Aug11Graph_2048_HighLatency.gpickle')

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

# bucket debug
# print("node 123 buckets: " + str(G.nodes[123]['buckets']))
# print("node 234 buckets: " + str(G.nodes[234]['buckets']))
# print("node 345 buckets: " + str(G.nodes[345]['buckets']))
# print("node 456 buckets: " + str(G.nodes[456]['buckets']))

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
					# if G.nodes[RLLoopNodeCounter]['prevScores'][currentBucketIndex] > 0: # not first epoch
					# 	# parameterOne = RLParameters.determineParameterOne(currentBucketIndex, parameters.NODE_ID_LENGTH, currentBucketScore)
					# 	parameterOne = 1.01
					# 	if currentBucketScore * parameterOne > G.nodes[RLLoopNodeCounter]['prevScores'][currentBucketIndex] and G.nodes[RLLoopNodeCounter]['bucketChangeItemFlags'][currentBucketIndex] == False: # roll back when new epoch performs badly
					# 		G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex] = G.nodes[RLLoopNodeCounter]['prevBuckets'][currentBucketIndex]
					# 		G.nodes[RLLoopNodeCounter]['bucketChangeItemFlags'][currentBucketIndex] = True
					# 	elif currentBucketScore * parameterOne <= G.nodes[RLLoopNodeCounter]['prevScores'][currentBucketIndex] and G.nodes[RLLoopNodeCounter]['bucketChangeItemFlags'][currentBucketIndex] == False: # ready to change
					# 		G.nodes[RLLoopNodeCounter]['bucketChangeItemFlags'][currentBucketIndex] = True
					# 	elif currentBucketScore * parameterOne <= G.nodes[RLLoopNodeCounter]['prevScores'][currentBucketIndex] and G.nodes[RLLoopNodeCounter]['bucketChangeItemFlags'][currentBucketIndex]: # change
					# 		G.nodes[RLLoopNodeCounter]['prevScores'][currentBucketIndex] = currentBucketScore
					# 		G.nodes[RLLoopNodeCounter]['prevBuckets'][currentBucketIndex] = copy.deepcopy(G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex])

					# 		tempV = list(currentScoreDict.values())
					# 		tempK = list(currentScoreDict.keys())
					# 		worstBucketItemBinary = tempK[tempV.index(max(tempV))]

					# 		worstBucketItemBinary_str = str(worstBucketItemBinary)
					# 		bucketItemCandidate_str = worstBucketItemBinary_str[:(currentBucketIndex+1)]
					# 		while len(bucketItemCandidate_str) < parameters.NODE_ID_LENGTH:
					# 			randCandidateSeed = random.uniform(0, 1)
					# 			if randCandidateSeed > 0.5:
					# 				bucketItemCandidate_str = bucketItemCandidate_str + "0"
					# 			else:
					# 				bucketItemCandidate_str = bucketItemCandidate_str + "1"
					# 			if len(bucketItemCandidate_str) == parameters.NODE_ID_LENGTH and bucketItemCandidate_str in G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex]:
					# 				bucketItemCandidate_str = worstBucketItemBinary_str[:(currentBucketIndex+1)]

					# 		G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex] = list(map(lambda x: x.replace(worstBucketItemBinary, bucketItemCandidate_str), G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex]))
					# 		G.nodes[RLLoopNodeCounter]['bucketChangeItemFlags'][currentBucketIndex] = False
					# else: # first epoch 
					# 	G.nodes[RLLoopNodeCounter]['prevScores'][currentBucketIndex] = currentBucketScore
					# 	G.nodes[RLLoopNodeCounter]['prevBuckets'][currentBucketIndex] = copy.deepcopy(G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex])

					# 	tempV = list(currentScoreDict.values())
					# 	tempK = list(currentScoreDict.keys())
					# 	worstBucketItemBinary = tempK[tempV.index(max(tempV))]

					# 	worstBucketItemBinary_str = str(worstBucketItemBinary)
					# 	bucketItemCandidate_str = worstBucketItemBinary_str[:(currentBucketIndex+1)]
					# 	while len(bucketItemCandidate_str) < parameters.NODE_ID_LENGTH:
					# 		randCandidateSeed = random.uniform(0, 1)
					# 		if randCandidateSeed > 0.5:
					# 			bucketItemCandidate_str = bucketItemCandidate_str + "0"
					# 		else:
					# 			bucketItemCandidate_str = bucketItemCandidate_str + "1"
					# 		if len(bucketItemCandidate_str) == parameters.NODE_ID_LENGTH and bucketItemCandidate_str in G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex]:
					# 			bucketItemCandidate_str = worstBucketItemBinary_str[:(currentBucketIndex+1)]

					# 	G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex] = list(map(lambda x: x.replace(worstBucketItemBinary, bucketItemCandidate_str), G.nodes[RLLoopNodeCounter]['buckets'][currentBucketIndex]))

					# clear the tables
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_INITIATOR_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['RLTables'][currentBucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_LATENCY_COLUMN_INDEX].clear()
					G.nodes[RLLoopNodeCounter]['epochCounters'][currentBucketIndex] += 1
					# add termination criteria below or the outer while loop NEVER STOPS
					if RLLoopNodeCounter == observationNode and currentBucketIndex == 0:
						print("Node " + str(observationNode) + " Epoch score: " + str(currentBucketScore) + " latency: " + str(avgLatency) + " RLCounter: " + str(G.nodes[RLLoopNodeCounter]['epochCounters'][0]))
						f = open("../../../GitHubExperimentsResults/TestResultJuly30_2048_50_HNL_SimplePNS.txt", "a")
						f.write(str(G.nodes[RLLoopNodeCounter]['epochCounters'][0]) + "	" + str(currentBucketScore) + "	" + str(avgLatency) + "\n")
						f.close()
						if G.nodes[RLLoopNodeCounter]['epochCounters'][0] > 100:
							print("100 Epochs for node bucket 0")
							endTime = time.time()
							print("Time consumed: " + str(endTime - startTime))
							sys.exit("Enough Epochs!")  
					# add termination criteria above or the outer while loop NEVER STOPS
				RLLoopNodeCounter += 1








