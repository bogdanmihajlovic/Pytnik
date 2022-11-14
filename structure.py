import math


class Node:
    def __init__(self, parent, path):
        self.path = path
        self.cost = 0
        self.price = 0
        self.parent = parent
        self.toVisit = []
        self.lastCoin = 0
        self.len = 1


def findMST(graph):
    num = len(graph)
    mst = [[0 for i in range(num)] for j in range(num)]
    nodes = [False for i in range(num)]

    for iter in range(num):
        minCost = math.inf
        x = 0
        y = 0
        for i in range(num):
            if nodes[i]:
                for j in range(num):
                    if not nodes[j] and graph[i][j]:
                        if graph[i][j] < minCost:
                            minCost = graph[i][j]
                            x, y = i, j

        if minCost == math.inf:
            minCost = 0

        mst[x][y] = mst[y][x] = minCost
        nodes[y] = True

    return mst


def costMST(graph):
    left = 0
    cost = 0
    for i in range(len(graph)):
        for j in range(left, len(graph)):
            cost += graph[i][j]
        left += 1
    return cost


def makeGraph(graph, toAvoid):
    newGraph = [[j for j in i] for i in graph]
    for coin in toAvoid:
        for i in range(len(graph)):
            newGraph[coin][i] = 0
            newGraph[i][coin] = 0
    return newGraph


#graph1 = [[0, 7, 6, 10, 13], [7, 0, 7, 10, 10],[6, 7, 0, 8, 9], [10, 10, 8, 0, 6],  [13, 10, 9, 6, 0]]




