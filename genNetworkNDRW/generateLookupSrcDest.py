import random
import parameters

f = open("lookupSrcDestPairs.txt", "a")

n = 10000000

counter = 0
while counter < n:
	src = random.randint(0, parameters.NETWORK_SIZE-1)
	dest = random.randint(0, parameters.NETWORK_SIZE-1)
	while dest == src:
		dest = random.randint(0, parameters.NETWORK_SIZE-1)
	f.write(str(src) + " " + str(dest) + "\n")
	counter += 1