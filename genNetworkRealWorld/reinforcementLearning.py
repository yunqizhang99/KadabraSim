import parameters

def computeScoreFunc(currentBucketIndex, currentBucket, currentRLTable):
	scoreDict = {}

	totalLatency = 0
	bucketScore = 0

	bucketItemCounter = 0
	while bucketItemCounter < len(currentBucket):
		scoreDict[currentBucket[bucketItemCounter]] = 0
		bucketItemCounter += 1

	biasForNoPassing = parameters.BIAS_FOR_NOT_PASSING_SCORE_COMPUTATION[currentBucketIndex]

	while len(currentRLTable[parameters.REINFORCEMENT_LEARNING_TABLE_LATENCY_COLUMN_INDEX]) > 0:
		currentPath = currentRLTable[parameters.REINFORCEMENT_LEARNING_TABLE_PATH_COLUMN_INDEX].pop(0)
		currentLatency = currentRLTable[parameters.REINFORCEMENT_LEARNING_TABLE_LATENCY_COLUMN_INDEX].pop(0)
		currentBucketItem = currentPath.pop(0)
		totalLatency += currentLatency

		bucketItemCounter = 0
		while bucketItemCounter < len(currentBucket):
			if format(currentBucketItem, parameters.NODE_ID_LENGTH_STRING) == currentBucket[bucketItemCounter]:
				scoreDict[currentBucket[bucketItemCounter]] += currentLatency
			else:
				scoreDict[currentBucket[bucketItemCounter]] += biasForNoPassing
			bucketItemCounter += 1

	bucketItemCounter = 0
	while bucketItemCounter < len(currentBucket):
		scoreDict[currentBucket[bucketItemCounter]] /= len(currentRLTable[parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX])
		bucketItemCounter += 1

	scoreValues = scoreDict.values()
	bucketScore = sum(scoreValues)

	avgLatency = totalLatency/len(currentRLTable[parameters.REINFORCEMENT_LEARNING_TABLE_DEST_COLUMN_INDEX])

	return scoreDict, bucketScore, avgLatency 
