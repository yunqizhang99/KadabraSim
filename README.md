# KadabraSim 
Kadabra: Adapting Kademlia for the Decentralized Web (Financial Cryptography and Data Security 2023)
https://arxiv.org/abs/2210.12858

Blockchains have become the catalyst for a growing movement to create a more decentralized Internet. A fundamental operation of applications in a decentralized Internet is data storage and retrieval. As today's blockchains are limited in their storage functionalities, in recent years a number of peer-to-peer data storage networks have emerged based on the Kademlia distributed hash table protocol. However, existing Kademlia implementations are not efficient enough to support fast data storage and retrieval operations necessary for (decentralized) Web applications. In this paper, we present Kadabra, a decentralized protocol for computing the routing table entries in Kademlia to accelerate lookups. Kadabra is motivated by the multi-armed bandit problem, and can automatically adapt to heterogeneity and dynamism in the network. Experimental results show Kadabra achieving between 15-50% lower lookup latencies compared to state-of-the-art baselines.

/genNetworkSquare contains source code for nodes in a square simulation.<br>
/genNetworkRealWorld contains source code for nodes in the real world simulation.
