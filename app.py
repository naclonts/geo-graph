import json
from pprint import pprint
import collections, enum
import draw
import graph
import itertools
import pygame
import random
import math
import sys
import heapq # Priority queue
from priorityQueue import PriorityQueue



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
	g = graph.Graph()
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




def dijkstra(g, start):
	# print('Finding shortest paths to ' + start.payload['city'])
	g.reset()
	pq = PriorityQueue()
	start.setDistance(0)
	pq.buildHeap([(v.getDistance(), v) for v in g])
	while not pq.isEmpty():
		currentVert = pq.delMin()
		for nextVert in currentVert.getConnections():
			newDist = currentVert.getDistance() \
					+ currentVert.getCost(nextVert)
			if newDist < nextVert.getDistance():
				# print('Setting {0}s predecessor to {1} (distance {2})'.format(nextVert.payload['city'], currentVert.payload['city'], round(newDist)))
				nextVert.setDistance(newDist)
				nextVert.parent = currentVert
				pq.decreaseKey(nextVert, newDist)



def findCityVertice(graph, cityName):
	for v in graph:
		if v.payload['city'] == cityName:
			return v
	return None


def findNearestCity(g, lat, lon):
	"""Find city nearest the given latitude and longitude."""
	closest = None
	minDistance = math.inf
	for v in g:
		d = distanceBetweenPoints(lat, lon, v.payload['latitude'], v.payload['longitude'])
		if d < minDistance:
			minDistance = d
			closest = v
	return closest


Modes = enum.Enum('Modes', 'ALL PARTIAL')
mode = Modes.ALL

if __name__ == '__main__':
	populationThreshold = 75000

	if mode == Modes.PARTIAL:
		citiesFile = 'cities_partial.json'
		distanceThreshold = 500
		fps = 5
	else:
		citiesFile = 'cities.json'
		distanceThreshold = 190
		fps = 60

	with open(citiesFile) as f:
		cities = json.load(f)

	cities = [city for city in cities if int(city['population']) > populationThreshold]

	# g = graphAllConnected(cities)
	def withinMiles(city1, city2):
		return distanceBetweenPoints(
                    city1['latitude'], city1['longitude'],
                    city2['latitude'], city2['longitude']
                ) < distanceThreshold

	g = graphConnectConditional(cities, withinMiles)


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
	# bfs = g.breadthFirstSearch(start)
	# dfs = g.depthFirstSearch(start)
	start = findCityVertice(g, 'Boston')
	dijkstra(g, start)
	destination = findCityVertice(g, 'Denver')


	done = False
	finishedDrawing = False
	listenForDestination = False
	v = destination
	colors = itertools.cycle(draw.highlightColors)
	color = draw.GREEN
	while not done:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				print('Quitting!')
				pygame.display.quit()
				pygame.quit()
				done = True
				continue
			elif event.type == pygame.MOUSEBUTTONDOWN:
				lat, lon = draw.coordsToPoint(event.pos[0], event.pos[1])
				u = findNearestCity(g, lat, lon)
				if listenForDestination:
					v = u
					listenForDestination = False
					city = v.payload
					print('From ' + city['city'])
					x, y = draw.pointToCoords(city['latitude'], city['longitude'])
					pygame.draw.circle(screen, color, (x, y), 10)

				else:
					start = u
					dijkstra(g, start)
					listenForDestination = True
					color = next(colors)
					city = start.payload
					print('Going to ' + city['city'])
					x, y = draw.pointToCoords(city['latitude'], city['longitude'])
					pygame.draw.circle(screen, color, (x, y), 10)

		# process vertex u here
		# u = next(bfs, None)
		# if u and u.parent:
		# 	draw.lineBetweenCities(u.payload, u.parent.payload, screen, draw.RED)

		# Draw shortest path from destination to start
		# elif not g.searching and not finishedDrawing:
		# 	v = destination
		# 	while v.parent is not None:
		# 		old = v
		# 		new = v.parent
		# 		draw.lineBetweenCities(old.payload, new.payload, screen, draw.GREEN)
		# 		v = new
		# 	finishedDrawing = True

		if v.parent is not None and not listenForDestination:
			old = v
			new = v.parent
			draw.lineBetweenCities(old.payload, new.payload, screen, color)
			v = new

		pygame.display.flip()
		clock.tick(fps)
