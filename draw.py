import sys, pygame, math

size = width, height = 1600, 950

BLUE = (10, 125, 200)
RED = (235, 40, 20)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def drawCities(graph, screen, font):
	for v in graph.getVertices():
		city = v.payload

		x, y = pointToCoords(city['latitude'], city['longitude'])
		
		pygame.draw.circle(screen, BLUE, (x, y), 10)
		drawText(city['city'], (x, y), font, screen)

		for v2 in v.getConnections():
			city2 = v2.payload
			x2, y2 = pointToCoords(city2['latitude'], city2['longitude'])

			midPoint = ((x+x2)/2, (y+y2)/2)

			lineColor = BLUE
			distance = v.getCost(v2)
			if distance < 1000:
				lineColor = RED

			pygame.draw.line(screen, lineColor, (x, y), (x2, y2), 1)
			drawText(str(round(distance)), midPoint, font, screen)

def pointToCoords(lat, lon):
	x = round(translate(lon, -130, -70, 0, width))
	y = round(translate(lat, 45, 25, 0, height))
	return (x, y)

def drawText(text, coords, font, screen):
	x, y = coords
	textSurface = font.render(text, True, WHITE)
	textRect = textSurface.get_rect()
	textRect.center = (x, y + 15)
	screen.blit(textSurface, textRect)


def init():
	ball = pygame.image.load('intro_ball.gif')
	ballrect = ball.get_rect()


def loop():
	speed = [2, 2]

	while 1:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				return

		ballrect = ballrect.move(speed)
		if ballrect.left < 0 or ballrect.right > width:
			speed[0] = -speed[0]
		if ballrect.top < 0 or ballrect.bottom > height:
			speed[1] = -speed[1]

		screen.fill(black)
		screen.blit(ball, ballrect)
		pygame.display.flip()

		clock.tick(60)

def translate(value, startMin, startMax, endMin, endMax):
	return (value - startMin) / (startMax - startMin) * (endMax - endMin) + endMin
