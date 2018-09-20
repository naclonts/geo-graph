import json
from pprint import pprint
import collections
import draw
import graph
import pygame
import random
import math
import heapq # Priority queue



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
	g = graph.Graph()
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


# def dijkstra(graph, initial):
# 	# Check reading bookmarks
# 	visited = {initial: 0}
# 	path = {}

# 	vertices = set(graph.getVertices())
# 	while vertices:
# 		minVertice = None
# 		for v in vertices:
# 			if v in visited:
# 				if minVertice is None:
# 					minVertice = v
# 				elif visited[v] < visited[minVertice]:
# 					minVertice = v

# 			if minVertice is None:
# 				break
			
# 			vertices.remove(minVertice)
# 			currentWeight = visited[minVertice]

# 			for u in minVertice.getConnections():
# 				weight = currentWeight + minVertice.getCost(u)
# 				if u not in visited or weight < visited[u]:
# 					visited[u] = weight
# 					path[u] = minVertice

# 	return visited, path

class PriorityQueue:
	def __init__(self):
		self.heap = []
	
	def buildHeap(self, initial):
		"""Accepts list of key-value pairs."""
		pq


def dijkstra(g, start):
	pq = []
	start.setDistance(0)
	pq = [v for v in g.getVertices()]
	heapq.heapify(pq)
	print(pq)





def findCityVertice(graph, cityName):
	for v in graph:
		if v.payload['city'] == cityName:
			return v
	return None


MODE = 'partial' # or 'all'

if __name__ == '__main__':
	if MODE == 'partial':
		citiesFile = 'cities_partial.json'
		distanceThreshold = 1000
		fps = 10
	else:
		citiesFile = 'cities.json'
		distanceThreshold = 250
		fps = 60

	with open(citiesFile) as f:
		cities = json.load(f)

	
	
	# g = graphAllConnected(cities)
	def withinMiles(city1, city2):
		return distanceBetweenPoints(
                    city1['latitude'], city1['longitude'],
                    city2['latitude'], city2['longitude']
                ) < distanceThreshold

	g = graphConnectConditional(cities, withinMiles)

	# Origin point for the traversal
	start = findCityVertice(g, 'Virginia Beach')

	# visited, path = dijkstra(g, start)
	# print(path)



	############################################################################
	# Below here is the graphics


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
	bfs = g.breadthFirstSearch(start)
	# dfs = g.depthFirstSearch(start)
	dijkstra(g, start)


	done = False
	finishedDrawing = False
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				done = True

		# process vertex u here
		u = next(bfs, None)
		if u and u.parent:
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

		# # muddy up the screen a bit
		# for v in g.getVertices():
		# 	threshold = math.sin(pygame.time.get_ticks() * 10)
		# 	if random.random() < threshold:
		# 		sign = 1
		# 	else:
		# 		sign = -1
		# 	print(sign)
		# 	# v.payload['latitude'] += (0.02 * sign)
		# draw.drawCities(g, highlightEdge, screen, font)
		# draw.screenCheck(screen)
		pygame.display.flip()
		clock.tick(fps)
