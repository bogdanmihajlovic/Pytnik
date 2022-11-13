class Node:
    def __init__(self, parent, path):
        self.path = path
        self.cost = 0
        self.parent = parent
        self.children = []
        self.toVisit = []