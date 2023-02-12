import random
import parameters
from math import dist

def binaryToDecimal(binary): 
    binary1 = binary
    decimal, i, n = 0, 0, 0
    while(binary != 0):
        dec = binary % 10
        decimal = decimal + dec * pow(2, i)
        binary = binary//10
        i += 1
    return decimal  

def fillAllBucketsRandom(G):
	nodeCounter = 0
	while nodeCounter < parameters.NETWORK_SIZE:
		current_id_str = str(G.nodes[nodeCounter]['id'])
		current_index_pos = 0
		while current_index_pos <= parameters.NODE_ID_LENGTH-1:
			if current_id_str[current_index_pos] == "0":
				temp = current_id_str[:current_index_pos]
				tempLow = temp + "1"
				tempUpp = temp + "1"
				while len(tempLow) != parameters.NODE_ID_LENGTH:
					tempLow = tempLow + "0"
					tempUpp = tempUpp + "1"
				lowerBound = binaryToDecimal(int(tempLow))
				upperBound = binaryToDecimal(int(tempUpp))
				bucketIndex = current_index_pos
				if (upperBound - lowerBound + 1) < parameters.BUCKET_SIZE:
					for j in range(lowerBound, upperBound+1):
						currentAdding = format(j, parameters.NODE_ID_LENGTH_STRING)
						G.nodes[nodeCounter]['buckets'][bucketIndex].append(currentAdding)
				else: 
					currentAdding = format(random.randint(lowerBound, upperBound), parameters.NODE_ID_LENGTH_STRING)
					candidateBucket = []
					while len(candidateBucket) < parameters.BUCKET_SIZE:
						while currentAdding in candidateBucket:
							currentAdding = format(random.randint(lowerBound, upperBound), parameters.NODE_ID_LENGTH_STRING)
						candidateBucket.append(currentAdding)
						currentAdding = format(random.randint(lowerBound, upperBound), parameters.NODE_ID_LENGTH_STRING)
					G.nodes[nodeCounter]['buckets'][bucketIndex] += candidateBucket
			else:
				temp = current_id_str[:current_index_pos]
				tempLow = temp + "0"
				tempUpp = temp + "0"
				while len(tempLow) != parameters.NODE_ID_LENGTH:
					tempLow = tempLow + "0"
					tempUpp = tempUpp + "1"
				lowerBound = binaryToDecimal(int(tempLow))
				upperBound = binaryToDecimal(int(tempUpp))
				bucketIndex = current_index_pos 
				if (upperBound - lowerBound + 1) < parameters.BUCKET_SIZE:
					for j in range(lowerBound, upperBound+1):
						currentAdding = format(j, parameters.NODE_ID_LENGTH_STRING)
						G.nodes[nodeCounter]['buckets'][bucketIndex].append(currentAdding)
				else: 
					currentAdding = format(random.randint(lowerBound, upperBound), parameters.NODE_ID_LENGTH_STRING)
					candidateBucket = []
					while len(candidateBucket) < parameters.BUCKET_SIZE:
						while currentAdding in candidateBucket:
							currentAdding = format(random.randint(lowerBound, upperBound), parameters.NODE_ID_LENGTH_STRING)
						candidateBucket.append(currentAdding)
						currentAdding = format(random.randint(lowerBound, upperBound), parameters.NODE_ID_LENGTH_STRING)
					G.nodes[nodeCounter]['buckets'][bucketIndex] += candidateBucket
			current_index_pos = current_index_pos + 1
		nodeCounter = nodeCounter + 1

def fillAllBucketsPNS(G):
	nodeCounter = 0
	while nodeCounter < parameters.NETWORK_SIZE:
		current_id_str = str(G.nodes[nodeCounter]['id'])
		current_index_pos = 0
		while current_index_pos <= parameters.NODE_ID_LENGTH-1:
			if current_id_str[current_index_pos] == "0":
				temp = current_id_str[:current_index_pos]
				tempLow = temp + "1"
				tempUpp = temp + "1"
				while len(tempLow) != parameters.NODE_ID_LENGTH:
					tempLow = tempLow + "0"
					tempUpp = tempUpp + "1"
				lowerBound = binaryToDecimal(int(tempLow))
				upperBound = binaryToDecimal(int(tempUpp))
				bucketIndex = current_index_pos
				if (upperBound - lowerBound + 1) < parameters.BUCKET_SIZE:
					for j in range(lowerBound, upperBound+1):
						currentAdding = format(j, parameters.NODE_ID_LENGTH_STRING)
						G.nodes[nodeCounter]['buckets'][bucketIndex].append(currentAdding)
				else: 
					PNScandidateBucket = []
					PNScandidateLatencyBucket = []
					equalRTTPeerCounter = 0
					for j in range(lowerBound, upperBound+1):
						jLatency = G[j][nodeCounter]['weight']
						if len(PNScandidateBucket) < parameters.BUCKET_SIZE:
							PNScandidateBucket.append(format(j, parameters.NODE_ID_LENGTH_STRING))
							PNScandidateLatencyBucket.append(jLatency)
						else:
							maxLatencyInBucket = max(PNScandidateLatencyBucket)
							if jLatency < maxLatencyInBucket:
								pos = PNScandidateLatencyBucket.index(maxLatencyInBucket)
								PNScandidateBucket[pos] = format(j, parameters.NODE_ID_LENGTH_STRING)
								PNScandidateLatencyBucket[pos] = jLatency
							elif jLatency == maxLatencyInBucket:
								equalRTTPeerCounter += 1
								if random.uniform(0, 1) <= 1/equalRTTPeerCounter:
									pos = PNScandidateLatencyBucket.index(maxLatencyInBucket)
									PNScandidateBucket[pos] = format(j, parameters.NODE_ID_LENGTH_STRING)
									PNScandidateLatencyBucket[pos] = jLatency
					G.nodes[nodeCounter]['buckets'][bucketIndex] += PNScandidateBucket
			else:
				temp = current_id_str[:current_index_pos]
				tempLow = temp + "0"
				tempUpp = temp + "0"
				while len(tempLow) != parameters.NODE_ID_LENGTH:
					tempLow = tempLow + "0"
					tempUpp = tempUpp + "1"
				lowerBound = binaryToDecimal(int(tempLow))
				upperBound = binaryToDecimal(int(tempUpp))
				bucketIndex = current_index_pos 
				if (upperBound - lowerBound + 1) < parameters.BUCKET_SIZE:
					for j in range(lowerBound, upperBound+1):
						currentAdding = format(j, parameters.NODE_ID_LENGTH_STRING)
						G.nodes[nodeCounter]['buckets'][bucketIndex].append(currentAdding)
				else: 
					PNScandidateBucket = []
					PNScandidateLatencyBucket = []
					equalRTTPeerCounter = 0
					for j in range(lowerBound, upperBound+1):
						jLatency = G[j][nodeCounter]['weight']
						if len(PNScandidateBucket) < parameters.BUCKET_SIZE:
							PNScandidateBucket.append(format(j, parameters.NODE_ID_LENGTH_STRING))
							PNScandidateLatencyBucket.append(jLatency)
						else:
							maxLatencyInBucket = max(PNScandidateLatencyBucket)
							if jLatency < maxLatencyInBucket:
								pos = PNScandidateLatencyBucket.index(maxLatencyInBucket)
								PNScandidateBucket[pos] = format(j, parameters.NODE_ID_LENGTH_STRING)
								PNScandidateLatencyBucket[pos] = jLatency
							elif jLatency == maxLatencyInBucket:
								equalRTTPeerCounter += 1
								if random.uniform(0, 1) <= 1/equalRTTPeerCounter:
									pos = PNScandidateLatencyBucket.index(maxLatencyInBucket)
									PNScandidateBucket[pos] = format(j, parameters.NODE_ID_LENGTH_STRING)
									PNScandidateLatencyBucket[pos] = jLatency
					G.nodes[nodeCounter]['buckets'][bucketIndex] += PNScandidateBucket
			current_index_pos = current_index_pos + 1
		nodeCounter = nodeCounter + 1

















