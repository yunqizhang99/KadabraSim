import parameters
import pandas

def buildEdges(G):

	latencyData = pandas.read_csv("latencyInfo03122022.csv")
	cityListWithFirstEmpty = latencyData.columns.to_list()
	print(latencyData)

	edgeAddingCounter0 = 0
	while edgeAddingCounter0 < parameters.NETWORK_SIZE:
		edgeAddingCounter1 = edgeAddingCounter0 + 1
		currentRowPosition = cityListWithFirstEmpty.index(G.nodes[edgeAddingCounter0]['city']) - 1
		while edgeAddingCounter1 < parameters.NETWORK_SIZE:
			currentLatency = latencyData[G.nodes[edgeAddingCounter1]['city']][currentRowPosition]
			print (G.nodes[edgeAddingCounter0]['city'] + " and " + G.nodes[edgeAddingCounter1]['city'] + " latency: " + str(currentLatency) + ".")
			e = (edgeAddingCounter0, edgeAddingCounter1)
			G.add_edge(*e, weight=currentLatency)  # single edge as tuple of two nodes

			edgeAddingCounter1 += 1
		edgeAddingCounter0 += 1
