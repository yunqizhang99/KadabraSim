import parameters
import bucketOperations
from math import dist
import copy
import random

# KBR or DHT Lookup
def simpleLookup(G, src, dest, alpha, useLookupKBR, useLookupDHT, DHTCopiesNumber):
	assert alpha <= len(G.nodes[0]['buckets'][0]), "Violation: parameter alpha smaller than bucket length!"
	assert alpha > 0, "Violation: alpha > 0!"

	RTTs_in_EucDist = []
	hopCounts = []
	pathsNodes = []
	binDestNode = format(dest, parameters.NODE_ID_LENGTH_STRING)
	binSrcNode = format(src, parameters.NODE_ID_LENGTH_STRING)
	nextHops = []
	currentNodes = []
	networkEdges = [[] for i in range(alpha)]

	# find the target bucket in the src node
	bucketIndex = 0
	while bucketIndex <= parameters.NODE_ID_LENGTH-1:
		if str(binSrcNode)[bucketIndex] == str(binDestNode)[bucketIndex]:
			bucketIndex += 1
		else:
			break
	
	# get XOR distances for items in the target bucket
	xorResultsInBucket = []
	xorResultsNodes = []
	for i in G.nodes[src]['buckets'][bucketIndex]:
		xorResultsInBucket.append(int(i, 2)^int(binDestNode,2))
		xorResultsNodes.append(i)

	# figure out alpha paths
	minXorResultValue = min(xorResultsInBucket)
	minXorResultNodePos = xorResultsInBucket.index(minXorResultValue)
	alphaCounter = 0
	while alphaCounter < alpha:
		currentPopNode = xorResultsNodes.pop(minXorResultNodePos)
		nextHops.append(currentPopNode)
		xorResultsInBucket.pop(minXorResultNodePos)
		currentNodes.append(bucketOperations.binaryToDecimal(int(currentPopNode)))
		alphaCounter += 1
		if len(xorResultsInBucket) == 0:
			break
		minXorResultValue = min(xorResultsInBucket)
		minXorResultNodePos = xorResultsInBucket.index(minXorResultValue)

	# perform lookup on each of the alpha paths
	alphaCounter = 0
	while alphaCounter < len(currentNodes):
		networkEdges[alphaCounter].append((src, currentNodes[alphaCounter]))
		currentRTT, currentHopCount, currentPathNodes = basicLookup(G, currentNodes[alphaCounter], dest, useLookupKBR, useLookupDHT, DHTCopiesNumber, networkEdges[alphaCounter])
		currentRTT += (dist(G.nodes[src]['pos'], G.nodes[currentNodes[alphaCounter]]['pos']) + G.nodes[currentNodes[alphaCounter]]['nodeLatency']) + random.choice(parameters.ADDED_EDGE_DELAY)
		currentHopCount += 1
		RTTs_in_EucDist.append(currentRTT)
		hopCounts.append(currentHopCount)
		pathsNodes.append(currentPathNodes)
		alphaCounter += 1

	minRTT = min(RTTs_in_EucDist)
	minRTTPos = RTTs_in_EucDist.index(minRTT)
	minPathNodes = pathsNodes[minRTTPos]

	# insert records to src node RLTable
	alphaCounter = 0
	while alphaCounter < len(currentNodes):
		G.nodes[src]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX].append(dest)
		G.nodes[src]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_INITIATOR_COLUMN_INDEX].append(parameters.LOOKUP_INITIATED_BY_ITSELF)
		G.nodes[src]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX].append(pathsNodes[alphaCounter])
		G.nodes[src]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_LATENCY_COLUMN_INDEX].append(RTTs_in_EucDist[alphaCounter])
		alphaCounter += 1

	return RTTs_in_EucDist, hopCounts, networkEdges


def basicLookup(G, src, dest, useLookupKBR, useLookupDHT, DHTCopiesNumber, edgesForThisLookup):
	RTT_in_EucDist = -1
	nextHop = None
	currentNode = src
	binCurrentNode = format(currentNode, parameters.NODE_ID_LENGTH_STRING)
	binDestNode = format(dest, parameters.NODE_ID_LENGTH_STRING)
	hopCount = 0
	destList = []

	if useLookupDHT and DHTCopiesNumber > 0:
		DHTCopyCounter = 0
		while DHTCopyCounter < DHTCopiesNumber:
			tempLow = dest - DHTCopyCounter
			tempHigh = dest + DHTCopyCounter
			if tempLow < 0:
				tempLow = parameters.NETWORK_SIZE - 1 + tempLow
			if tempHigh > parameters.NETWORK_SIZE - 1:
				tempHigh = tempHigh - (parameters.NETWORK_SIZE - 1)
			destList.append(tempLow)
			destList.append(tempHigh)
			DHTCopyCounter += 1

	destList.append(dest)

	pathNodes = []
	pathNodesCopy = []
	pathLatencies = []
	pathNodes.append(currentNode)
	pathNodesCopy.append(currentNode)
	pathLatencies.append(0)

	while not (currentNode in destList):
		bucketIndex = 0
		while bucketIndex <= parameters.NODE_ID_LENGTH-1:
			if str(binCurrentNode)[bucketIndex] == str(binDestNode)[bucketIndex]:
				bucketIndex += 1
			else:
				break

		G.nodes[currentNode]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX].append(dest)
		G.nodes[currentNode]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_INITIATOR_COLUMN_INDEX].append(parameters.LOOKUP_INITIATED_BY_OTHERS)

		min = -1
		for i in G.nodes[currentNode]['buckets'][bucketIndex]:
			xorResult = int(i, 2)^int(binDestNode,2)
			if min < 0:
				min = xorResult
				nextHop = i
			elif min >= xorResult:
				min = xorResult
				nextHop = i
		thisHopDist = dist(G.nodes[bucketOperations.binaryToDecimal(int(nextHop))]['pos'], G.nodes[currentNode]['pos']) + G.nodes[bucketOperations.binaryToDecimal(int(nextHop))]['nodeLatency'] + random.choice(parameters.ADDED_EDGE_DELAY)
		edgesForThisLookup.append((currentNode, bucketOperations.binaryToDecimal(int(nextHop))))
		RTT_in_EucDist += thisHopDist
		pathLatencies.append(RTT_in_EucDist)
		binCurrentNode = nextHop
		currentNode = bucketOperations.binaryToDecimal(int(binCurrentNode))
		pathNodes.append(currentNode)
		pathNodesCopy.append(currentNode)
		hopCount = hopCount + 1

	while len(pathNodes) > 1:
		currentPopHead = pathNodes.pop(0)
		tempPathNodes = copy.deepcopy(pathNodes)
		
		bucketIndex = 0
		while bucketIndex < parameters.NODE_ID_LENGTH-1:
			if format(tempPathNodes[0], parameters.NODE_ID_LENGTH_STRING) in G.nodes[currentPopHead]['buckets'][bucketIndex]:
				break
			else:
				bucketIndex += 1
		G.nodes[currentPopHead]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX].append(tempPathNodes)

		currentPopHeadLatencyToBeSubstracted = pathLatencies.pop(0)
		currentPopHeadLatency = RTT_in_EucDist - currentPopHeadLatencyToBeSubstracted
		G.nodes[currentPopHead]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_LATENCY_COLUMN_INDEX].append(currentPopHeadLatency)

	return RTT_in_EucDist, hopCount, pathNodesCopy


# KBR or DHT Lookup for Proximity Routing
def simpleLookupPR(G, src, dest, alpha, useLookupKBR, useLookupDHT, DHTCopiesNumber):
	assert alpha <= len(G.nodes[0]['buckets'][0]), "Violation: parameter alpha smaller than bucket length!"
	assert alpha > 0, "Violation: alpha > 0!"

	RTTs_in_EucDist = []
	hopCounts = []
	pathsNodes = []
	binDestNode = format(dest, parameters.NODE_ID_LENGTH_STRING)
	binSrcNode = format(src, parameters.NODE_ID_LENGTH_STRING)
	nextHops = []
	currentNodes = []
	networkEdges = [[] for i in range(alpha)]

	# find the target bucket in the src node
	bucketIndex = 0
	while bucketIndex <= parameters.NODE_ID_LENGTH-1:
		if str(binSrcNode)[bucketIndex] == str(binDestNode)[bucketIndex]:
			bucketIndex += 1
		else:
			break
	
	# get XOR distances for items in the target bucket
	xorResultsInBucket = []
	xorResultsNodes = []
	for i in G.nodes[src]['buckets'][bucketIndex]:
		xorResultsInBucket.append(dist(G.nodes[bucketOperations.binaryToDecimal(int(i))]['pos'], G.nodes[src]['pos'])) # PR
		xorResultsNodes.append(i)

	# figure out alpha paths
	minXorResultValue = min(xorResultsInBucket)
	minXorResultNodePos = xorResultsInBucket.index(minXorResultValue)
	alphaCounter = 0
	while alphaCounter < alpha:
		currentPopNode = xorResultsNodes.pop(minXorResultNodePos)
		nextHops.append(currentPopNode)
		xorResultsInBucket.pop(minXorResultNodePos)
		currentNodes.append(bucketOperations.binaryToDecimal(int(currentPopNode)))
		alphaCounter += 1
		if len(xorResultsInBucket) == 0:
			break
		minXorResultValue = min(xorResultsInBucket)
		minXorResultNodePos = xorResultsInBucket.index(minXorResultValue)

	# perform lookup on each of the alpha paths
	alphaCounter = 0
	while alphaCounter < len(currentNodes):
		networkEdges[alphaCounter].append((src, currentNodes[alphaCounter]))
		currentRTT, currentHopCount, currentPathNodes = basicLookup(G, currentNodes[alphaCounter], dest, useLookupKBR, useLookupDHT, DHTCopiesNumber, networkEdges[alphaCounter])
		currentRTT += (dist(G.nodes[src]['pos'], G.nodes[currentNodes[alphaCounter]]['pos']) + G.nodes[currentNodes[alphaCounter]]['nodeLatency']) + random.choice(parameters.ADDED_EDGE_DELAY)
		currentHopCount += 1
		RTTs_in_EucDist.append(currentRTT)
		hopCounts.append(currentHopCount)
		pathsNodes.append(currentPathNodes)
		alphaCounter += 1

	minRTT = min(RTTs_in_EucDist)
	minRTTPos = RTTs_in_EucDist.index(minRTT)
	minPathNodes = pathsNodes[minRTTPos]

	# insert records to src node RLTable
	alphaCounter = 0
	while alphaCounter < len(currentNodes):
		G.nodes[src]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX].append(dest)
		G.nodes[src]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_INITIATOR_COLUMN_INDEX].append(parameters.LOOKUP_INITIATED_BY_ITSELF)
		G.nodes[src]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX].append(pathsNodes[alphaCounter])
		G.nodes[src]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_LATENCY_COLUMN_INDEX].append(RTTs_in_EucDist[alphaCounter])
		alphaCounter += 1

	return RTTs_in_EucDist, hopCounts, networkEdges


def basicLookupPR(G, src, dest, useLookupKBR, useLookupDHT, DHTCopiesNumber, edgesForThisLookup):
	RTT_in_EucDist = -1
	nextHop = None
	currentNode = src
	binCurrentNode = format(currentNode, parameters.NODE_ID_LENGTH_STRING)
	binDestNode = format(dest, parameters.NODE_ID_LENGTH_STRING)
	hopCount = 0
	destList = []

	if useLookupDHT and DHTCopiesNumber > 0:
		DHTCopyCounter = 0
		while DHTCopyCounter < DHTCopiesNumber:
			tempLow = dest - DHTCopyCounter
			tempHigh = dest + DHTCopyCounter
			if tempLow < 0:
				tempLow = parameters.NETWORK_SIZE - 1 + tempLow
			if tempHigh > parameters.NETWORK_SIZE - 1:
				tempHigh = tempHigh - (parameters.NETWORK_SIZE - 1)
			destList.append(tempLow)
			destList.append(tempHigh)
			DHTCopyCounter += 1

	destList.append(dest)

	pathNodes = []
	pathNodesCopy = []
	pathLatencies = []
	pathNodes.append(currentNode)
	pathNodesCopy.append(currentNode)
	pathLatencies.append(0)

	while not (currentNode in destList):
		bucketIndex = 0
		while bucketIndex <= parameters.NODE_ID_LENGTH-1:
			if str(binCurrentNode)[bucketIndex] == str(binDestNode)[bucketIndex]:
				bucketIndex += 1
			else:
				break

		G.nodes[currentNode]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX].append(dest)
		G.nodes[currentNode]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_INITIATOR_COLUMN_INDEX].append(parameters.LOOKUP_INITIATED_BY_OTHERS)

		min = -1
		for i in G.nodes[currentNode]['buckets'][bucketIndex]:
			xorResult = dist(G.nodes[bucketOperations.binaryToDecimal(int(i))]['pos'], G.nodes[currentNode]['pos'])
			if min < 0:
				min = xorResult
				nextHop = i
			elif min >= xorResult:
				min = xorResult
				nextHop = i
		thisHopDist = dist(G.nodes[bucketOperations.binaryToDecimal(int(nextHop))]['pos'], G.nodes[currentNode]['pos']) + G.nodes[bucketOperations.binaryToDecimal(int(nextHop))]['nodeLatency'] + random.choice(parameters.ADDED_EDGE_DELAY)
		edgesForThisLookup.append((currentNode, bucketOperations.binaryToDecimal(int(nextHop))))
		RTT_in_EucDist += thisHopDist
		pathLatencies.append(RTT_in_EucDist)
		binCurrentNode = nextHop
		currentNode = bucketOperations.binaryToDecimal(int(binCurrentNode))
		pathNodes.append(currentNode)
		pathNodesCopy.append(currentNode)
		hopCount = hopCount + 1

	while len(pathNodes) > 1:
		currentPopHead = pathNodes.pop(0)
		tempPathNodes = copy.deepcopy(pathNodes)
		
		bucketIndex = 0
		while bucketIndex < parameters.NODE_ID_LENGTH-1:
			if format(tempPathNodes[0], parameters.NODE_ID_LENGTH_STRING) in G.nodes[currentPopHead]['buckets'][bucketIndex]:
				break
			else:
				bucketIndex += 1
		G.nodes[currentPopHead]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX].append(tempPathNodes)

		currentPopHeadLatencyToBeSubstracted = pathLatencies.pop(0)
		currentPopHeadLatency = RTT_in_EucDist - currentPopHeadLatencyToBeSubstracted
		G.nodes[currentPopHead]['RLTables'][bucketIndex][parameters.REINFORCEMENT_LEARNING_TABLE_LATENCY_COLUMN_INDEX].append(currentPopHeadLatency)

	return RTT_in_EucDist, hopCount, pathNodesCopy








