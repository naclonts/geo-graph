from enum import Enum
import collections, math

class VertexState(Enum):
	UNDISCOVERED = 0
	DISCOVERED = 1
	COMPLETELY_EXPLORED = 2


class Vertex:
	def __init__(self, key, payload=None):
		self.id = key
		self.payload = payload
		# connectedTo - keys are Vertex objects and values are costs / weights
		self.connectedTo = {}
		# search variables
		self.state = None
		self.parent = None
		# distance used in shortest-path algorithms
		self.distance = math.inf

	def addNeighbor(self, nbr, cost=0, directed=False):
		self.connectedTo[nbr] = cost
		# Connect neighbor if this is an undirected graph
		if not directed and not nbr.isConnectedTo(self):
			nbr.addNeighbor(self, cost, directed)

	def isConnectedTo(self, vertex):
		return vertex in self.connectedTo

	def getConnections(self):
		return self.connectedTo.keys()

	def getId(self):
		return self.id

	def getCost(self, nbr):
		return self.connectedTo[nbr]
	
	def setDistance(self, dist):
		self.distance = dist

	def getDistance(self):
		return self.distance

	def __str__(self):
		return str(self.id) + ' connectedTo: ' + \
			str([x.getId() for x in self.connectedTo])

	def __repr__(self):
		return 'Vertex ' + str(self.id)
	
	# comparisons for priority heap queue
	def __eq__(self, other):
		return self.distance == other.distance
	def __lt__(self, other):
		return self.distance < other.distance
	def __gt__(self, other):
		return self.distance > other.distance

	def __key(self):
		return self.id
	def __hash__(self):
		return hash(self.__key())


class Graph:
	def __init__(self):
		self.vertices = {}
		self.numVertices = 0
		self.directed = False
		self.searching = False

	def addVertex(self, key, payload=None):
		self.numVertices += 1
		newVertex = Vertex(key, payload)
		self.vertices[newVertex.getId()] = newVertex
		return newVertex

	def getVertex(self, n):
		if n in self.vertices:
			return self.vertices[n]
		else:
			return None

	def __contains__(self, n):
		return n in self.vertices

	def addEdge(self, f, t, cost=0):
		if f not in self.vertices:
			self.addVertex(f)
		if t not in self.vertices:
			self.addVertex(t)
		self.vertices[f].addNeighbor(self.vertices[t], cost, self.directed)

	def getVertices(self):
		return self.vertices.values()

	def print(self):
		for v1 in self.vertices.values():
			print(v1)

	def __iter__(self):
		return iter(self.vertices.values())

	def breadthFirstSearch(self, start, depthFirst=False):
		"""BFS generator yielding each vertex as it is explored."""
		self.searching = True

		# initialize structure
		for u in self:
			u.state = VertexState.UNDISCOVERED
			u.parent = None
		start.state = VertexState.DISCOVERED
		u = None

		discovered = collections.deque()
		discovered.append(start)
		while len(discovered) > 0:
			if depthFirst:
				u = discovered.pop()
			else:
				u = discovered.popleft()
			yield u

			for v in u.getConnections():
				# process edge (u, v) here
				if v.state == VertexState.UNDISCOVERED:
					v.state = VertexState.DISCOVERED
					v.parent = u
					discovered.append(v)
			u.state = VertexState.COMPLETELY_EXPLORED

		self.searching = False

	def depthFirstSearch(self, start):
		"""DFS generator. Yields each explored vertex."""
		self.searching = True

		# initialize structure
		for u in self:
			u.state = VertexState.UNDISCOVERED
		for u in self:
			if u.state == VertexState.UNDISCOVERED:
				# new component
				dfs = self._dfs(u)
				yield from dfs

		self.searching = False

	def _dfs(self, u):
		u.state = VertexState.DISCOVERED
		yield u
		for v in u.getConnections():
			if v.state == VertexState.UNDISCOVERED:
				v.parent = u
				yield from self._dfs(v)
		u.state = VertexState.COMPLETELY_EXPLORED
