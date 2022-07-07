import numpy as np
import matplotlib.pyplot as plt
import math, random, copy, pygame, sys

OMEGA =  5e-3
INCLINE = 2e-1
G = 9.8
coriolis = lambda v,p : 2 * OMEGA * v * math.sin(math.radians(p))

size = 4

def add_h(arg):
    h = 1e-6
    return int(arg/(size+h))

class PVector:
    def __init__(self,x,y) -> None:
        self.x = x
        self.y = y
    
    def __add__(self,other):
        x,y = self.x + other.x , self.y + other.y
        return PVector(x,y)

    def __sub__(self,other):
        x,y = self.x - other.x , self.y - other.y
        return PVector(x,y)
    
    def convert(self):
        theta = math.atan2(self.y,self.x) * 180 / math.pi
        value = (self.x**2 + self.y**2)**0.5
        return Vector(theta,value)
    
    def tuple(self):
        return self.x,self.y
    
    def __repr__(self) -> str:
        return f'Position({self.x},{self.y})'

class Vector:
    def __init__(self,theta,value) -> None:
        self.theta = theta
        self.value = value
    
    def __add__(self,other):
        S = self.convert()
        O = other.convert()
        return (S+O).convert()
    
    def __sub__(self,other):
        S = self.convert()
        O = other.convert()
        return (S-O).convert()
    
    def convert(self):
        x = math.cos(math.radians(self.theta)) * self.value
        y = math.sin(math.radians(self.theta)) * self.value
        return PVector(x,y)
    
    def __repr__(self) -> str:
        return f'Vector({self.theta},{self.value})'

class Wind:
    def __init__(self,strength) -> None:
        self.strength = strength
    
    def calculate(self,lat):
        return Vector(180,self.strength*math.cos(2 * lat))

class RubberDuck:
    def __init__(self,x,lat) -> None:
        self.x = x
        self.lat = lat
        self.speed = Vector(0,0)
    
    def move(self,wind):
        change = copy.copy(self.speed)
        change = Vector(0,0)
        change += wind.calculate(math.radians(self.lat)) # 바람
        change += Vector(180, G * INCLINE) # 수압 경도력
        change += Vector(90, -self.x/1e+4)
        #if 200 <self.x < 300:
        #    change += Vector(90, -self.x/1e+3)
        change += Vector(self.speed.theta-90,coriolis(change.value,self.lat)) # 전향력

        self.speed = change
        moving = self.speed.convert().tuple()
        self.x += moving[0]
        self.lat += moving[1]
        if self.x < -500*size :
            self.x = 500*size
        if self.x > 500*size :
            self.x = -500*size
        self.lat = max(self.lat, 0)
        self.lat = min(self.lat, 90)

    def draw(self,screen):
        x = add_h(self.x)+SCREEN_WIDTH/2
        y = -add_h(self.lat/90 * SCREEN_HEIGHT * size)+SCREEN_HEIGHT

        dx = int(math.cos(math.radians(self.speed.theta)) * 15)
        dy = int(math.sin(math.radians(self.speed.theta)) * 15)
        dx2 = int(math.cos(math.radians(self.speed.theta+120)) * 10)
        dy2 = int(math.sin(math.radians(self.speed.theta+120)) * 10)
        dx3 = int(math.cos(math.radians(self.speed.theta-120)) * 10)
        dy3 = int(math.sin(math.radians(self.speed.theta-120)) * 10)
        dx = add_h(math.cos(math.radians(self.speed.theta)) * 17)
        dy = add_h(math.sin(math.radians(self.speed.theta)) * 17)
        dx2 = add_h(math.cos(math.radians(self.speed.theta+120)) * 12)
        dy2 = add_h(math.sin(math.radians(self.speed.theta+120)) * 12)
        dx3 = add_h(math.cos(math.radians(self.speed.theta-120)) * 12)
        dy3 = add_h(math.sin(math.radians(self.speed.theta-120)) * 12)
        pygame.draw.line(screen, ORANGE, (x, y), (x + 10 * math.cos(math.radians(self.speed.theta)),y + 10 * math.sin(math.radians(self.speed.theta))), 5)

        pygame.draw.polygon(surface=screen, color=WHITE, points=[(x+dx,y+dy), (x+dx2,y+dy2), (x+dx3,y+dy3)])

wind = Wind(10e-0)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 500

WHITE = (255, 255, 255)
ORANGE = (255, 127, 0)
BLACK = (0, 0, 0)
pygame.init()
pygame.display.set_caption("")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
rubberDuckSet = [RubberDuck(random.randint(-500,500),random.randint(0,90)) for i in range(200)]
clock = pygame.time.Clock()

while True:
    #clock.tick(100000)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    screen.fill(BLACK)
    for j in range(len(rubberDuckSet)):
        rubberDuckSet[j].move(wind)
        rubberDuckSet[j].draw(screen)
    print(sum(tuple(map(lambda x : x.lat, rubberDuckSet))))
    pygame.display.update()

testcase = 100
sigmaData = []
setSaveData = []
for k in range(100):
    rubberDuckSet = [RubberDuck(random.randint(-500,500),random.randint(0,90)) for i in range(200)]
    sigma = math.inf
    setSave = None
    print(f'....{k/testcase * 100}%')
    for i in range(200):
        for j in range(len(rubberDuckSet)):
            rubberDuckSet[j].move(wind)
        temp = np.std(tuple(map(lambda x : math.sqrt(x.x**2 + x.lat**2), rubberDuckSet)))
        if temp < sigma : 
            sigma = temp
            setSave = rubberDuckSet
    sigmaData.append(sigma)
    setSaveData.append(setSave)
print(sigmaData)
print(sum(list(map(lambda setSave: sum(list(map(lambda rubberDuck : rubberDuck.x,setSave)))/len(setSave),setSaveData)))/len(setSaveData))
print(sum(list(map(lambda setSave: sum(list(map(lambda rubberDuck : rubberDuck.lat,setSave)))/len(setSave),setSaveData)))/len(setSaveData))