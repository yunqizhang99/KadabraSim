import random
import parameters

# simple hotspot generation
def hotspotsGenerationFunc(lowerBound, upperBound, hotspotsNumber):
	hotspotsList = [] 
	hotspotsAddingCounter = 0
	while hotspotsAddingCounter < hotspotsNumber:
		hotspotCandidate = random.randint(lowerBound, upperBound)
		while hotspotCandidate in hotspotsList:
			hotspotCandidate = random.randint(lowerBound, upperBound)
		hotspotsList.append(hotspotCandidate)
		hotspotsAddingCounter += 1
	return hotspotsList