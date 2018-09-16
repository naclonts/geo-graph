import json
from pprint import pprint
import draw
import pygame
import math

class Vertex:
	def __init__(self, key, payload=None):
		self.id = key
		self.payload = payload
		# connectedTo - keys are Vertex objects and values are costs / weights
		self.connectedTo = {}
	
	def addNeighbor(self, nbr, cost=0):
		self.connectedTo[nbr] = cost

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


class Graph:
	def __init__(self):
		self.vertices = {}
		self.numVertices = 0

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
		self.vertices[f].addNeighbor(self.vertices[t], cost)
	
	def getVertices(self):
		return self.vertices.values()

	def print(self):
		for v1 in self.vertices.values():
			print(v1)

	def __iter__(self):
		return iter(self.vertices.values())


def distanceBetweenPoints(lat1, lon1, lat2, lon2):
	"""Miles between two points on the earth based in lat/lon (in degrees)."""
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
			if existingVertex.getId() != city['id']:
				city2 = existingVertex.payload
				d = distanceBetweenPoints(
					city['latitude'], city['longitude'],
					city2['latitude'], city2['longitude']
				)
				g.addEdge(i, existingVertex.getId(), d)
	return g


if __name__ == '__main__':
	with open('cities_partial.json') as f:
		cities = json.load(f)

	
	g = graphAllConnected(cities)
	g.print()


	# Display
	draw.init()
	screen = pygame.display.set_mode(draw.size)
	clock = pygame.time.Clock()
	pygame.font.init()
	font = pygame.font.SysFont('monospace', 15)

	draw.drawCities(g, screen, font)
	pygame.display.flip()

	done = False
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				done = True
		clock.tick(60)
