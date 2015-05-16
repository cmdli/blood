#!/usr/bin/python
import math
import random
import json
from sys import argv

class Cell:
    def __init__(self, maxHunger):
        self.food = 0
        self.maxHunger = maxHunger
        self.hunger = maxHunger
        self.store = 0

    def give(self, neighbors):
        if self.hunger == 0:
            food_per = math.floor(self.food/len(neighbors))
            for n in self.neighbors:
                n.recieve(food_per)
                food = food - food_per

    def eat(self):
        # Move recieved food into local food amount
        self.food += self.store
        self.store = 0
        # Eat food up to hunger levels
        if self.hunger > 0:
            if self.food >= self.hunger:
                self.food -= self.hunger
                self.hunger = 0
            else:
                self.hunger -= self.food
                self.food = 0
            
    def recieve(self, amount):
        self.store += amount

    def reset(self):
        self.hunger = self.maxHunger

class World:
    def __init__(self, width, height, genome):
        self.width = width
        self.height = height
        self.grid = [[Cell(genome[x + y*height]) for x in range(width)] for y in range(height)]
        self.reset()

    def tick(self):
        grid = self.grid
        for y in range(self.height):
            for x in range(self.width):
                neighbors = [grid[cy][cx] for cy in range(x-1,x+1) for cx in range(y-1,y+1) if not (cx == x and cy == y)]
                grid[y][x].give(neighbors)

        for y in range(self.height):                
            for x in range(self.width):
                grid[y][x].eat()

    def reset(self):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x].reset()
            
    def alive(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x].hunger > 0:
                    return True
        return False

def runRound(world):
    world.reset()
    i = 0
    while world.alive():
        world.tick()
        i = i + 1
    return i

def mutate(genome, width, height):
    for x in range(width):
        for y in range(height):
            if random.random() > 0.1: #Take a hunger unit from a neighbor
                while True:
                    dx = random.randint(-1,1)
                    dy = random.randint(-1,1)
                    if not (dy == 0 and dx == 0) and genome[(x+dy) + (y+dy)*width] > 1:
                        break
                genome[x + y*width] += 1
                genome[(x+dx) + (y+dy)*width] -= 1

def evolve(genomes, width, height):
    scores = []
    for g in genomes:
        world = World(width, height, g)
        scores.append((runRound(world), g))
    ranked = sorted(scores)
    cutoff = int(len(ranked)*0.5) - 1
    parents = [g[1] for g in ranked[cutoff:]]
    updated = list(parents)
    for i in range(cutoff):
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)
        child = []
        split = random.randint(0,len(parent1))
        for i in range(len(parent2)):
            if i > split:
                child.append(parent1[i])
            else:
                child.append(parent2[i])
        updated.append(child)

def readWorldFile(name):
    f = open(name, 'r')
    text = f.read()
    f.close()
    obj = json.loads(text)
    return obj[0], obj[1], obj[2]

def writeWorldFile(genome, name, width, height):
    out = json.dumps([width, height, genome])
    f = open(name, 'w')
    f.write(out)
    f.close()

def main():
    genomes = []
    rounds = 0
    width = 0
    height = 0
    if len(argv) == 2:
        for i in range(10):
            width, height, genome = readWorldFile(str(i) + ".world")
            genomes.append(genome)
        rounds = int(argv[1])
    elif len(argv) == 3:
        assert(argv[1] == "test")
        i = int(argv[2])
        width, height, genome = readWorldFile(str(i) + ".world")
        world = World(width, height, genome)
        print "Num rounds for " + str(i) + ".world: " + str(runRound(world))
    elif len(argv) == 4:
        rounds = int(argv[1])
        width = int(argv[2])
        height = int(argv[3])
        for i in range(10):
            genomes.append([100+random.choice(range(-10,10)) for i in range(width*height)])
    else:
        print "Wrong usage! (TODO: ADD USAGE)"
        return
    
    for i in range(rounds):
        evolve(genomes, width, height)

    for i,g in enumerate(genomes):
        writeWorldFile(g, str(i) + ".world", width, height)

if __name__ == "__main__":
    main()
        

