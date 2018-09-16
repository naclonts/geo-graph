import json
from pprint import pprint
import collections
import draw
from enum import Enum
import pygame
import math

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

	def __str__(self):
		return str(self.id) + ' connectedTo: ' + \
			str([x.getId() for x in self.connectedTo])
	
	def __repr__(self):
		return 'Vertex ' + str(self.id)


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


def distanceBetweenPoints(lat1, lon1, lat2, lon2):
	"""Returns miles between two points on the earth based on lat/lon (in degrees)."""
	r = 6371e3  # earth's radius in meters
	p1 = math.radians(lat1)
	p2 = math.radians(lat2)
	delta_p = math.radians(lat2 - lat1)
	delta_l = math.radians(lon2 - lon1)

	a = math.sin(delta_p / 2) * math.sin(delta_p / 2) + \
		math.cos(p1) * math.cos(p2) * \
		math.sin(delta_l / 2) * math.sin(delta_l / 2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

	return r * c * 0.0006214  # convert to miles


def graphAllConnected(cities):
	g = Graph()
	for i, city in enumerate(cities):
		city['id'] = i
		g.addVertex(i, city)
		for existingVertex in g.getVertices():
			city2 = existingVertex.payload
			if city2['id'] != city['id']:
				d = distanceBetweenPoints(
					city['latitude'], city['longitude'],
					city2['latitude'], city2['longitude']
				)
				g.addEdge(i, existingVertex.getId(), d)
	return g


def graphConnectConditional(cities, connectionCheck):
	g = Graph()
	for i, city in enumerate(cities):
		city['id'] = i
		g.addVertex(i, city)
		for existingVertex in g.getVertices():
			city2 = existingVertex.payload
			if city2['id'] != city['id'] and connectionCheck(city, city2):
				d = distanceBetweenPoints(
					city['latitude'], city['longitude'],
					city2['latitude'], city2['longitude']
				)
				g.addEdge(i, existingVertex.getId(), d)
	return g


def findCityVertice(graph, cityName):
	for v in graph:
		if v.payload['city'] == cityName:
			return v
	return None


if __name__ == '__main__':
	with open('cities_partial.json') as f:
		cities = json.load(f)

	
	# g = graphAllConnected(cities)
	def withinMiles(city1, city2):
		return distanceBetweenPoints(
                    city1['latitude'], city1['longitude'],
                    city2['latitude'], city2['longitude']
                ) < 1000

	g = graphConnectConditional(cities, withinMiles)


	# Display
	screen = pygame.display.set_mode(draw.size)
	clock = pygame.time.Clock()
	pygame.font.init()
	font = pygame.font.SysFont('monospace', 15)

	def highlightEdge(v1, v2):
		return False
		distance = v1.getCost(v2)
		if distance < 1000:
			return True
		return False

	draw.drawCities(g, highlightEdge, screen, font)
	pygame.display.flip()

	# initialize search
	start = findCityVertice(g, 'New York')
	# bfs = g.breadthFirstSearch(start)
	dfs = g.depthFirstSearch(start)

	done = False
	finishedDrawing = False
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				done = True

		# process vertex u here
		u = next(dfs, None)
		if u and u.parent:
			print(u)
			draw.lineBetweenCities(u.payload, u.parent.payload, screen, draw.RED)

		# Draw shortest path from destination to start
		elif not g.searching and not finishedDrawing:
			destination = findCityVertice(g, 'Los Angeles')
			v = destination
			while v.parent is not None:
				old = v
				new = v.parent
				draw.lineBetweenCities(old.payload, new.payload, screen, draw.GREEN)
				v = new
			finishedDrawing = True


		pygame.display.flip()
		clock.tick(1)
