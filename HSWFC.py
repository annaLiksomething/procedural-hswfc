import networkx as nx
from matplotlib import pyplot as plt
from queue import Queue
import pygame
import random


dag = nx.DiGraph()
dag.add_edges_from([("root", "village"), ("root", "castle"), ("root", "land"), ("village", "house"), ("village", "road"), ("castle", "road"), ("land", "road"), ("land", "water"), ("house", "22"), ("house", "6"), ("house", "6"), ("house", "8"), ("house", "23"), ("road", "23"), ("road", "7"), ("road", "9"), ("house", "24"), ("road", "24"), ("water", "24"), ("road", "0"), ("castle", "0"), ("road", "1"), ("castle", "1"), ("road", "2"), ("castle", "2"), ("road", "5"), ("castle", "5"), ("road", "12"), ("castle", "12"), ("road", "14"), ("castle", "14"), ("road", "26"), ("castle", "26"), ("water", "26"), ("castle", "3"), ("castle", "4"), ("castle", "10"), ("castle", "11"), ("castle", "13"), ("castle", "15"), ("road", "21"), ("water", "21"), ("road", "25"), ("water", "25"), ("castle", "18"), ("water", "18"), ("castle", "20"), ("water", "20"), ("water", "16"), ("water", "17"), ("water", "19")])



terminal_q = Queue()

meta_q = Queue()

for i in range(27):
    terminal_q.put(str(i))

print (terminal_q.queue) 



print(dag.order())
    
print(nx.is_directed_acyclic_graph(dag))
plt.tight_layout()
nx.draw_networkx(dag, arrows=True)
plt.savefig("dag.png", format="PNG")
plt.clf()
terminalTiles = []
metaTiles = []

while terminalTiles != []:
    currentTile = terminalTiles[0]
    for meta in metaTiles:
        "this is not done yet"


# MODULES


# DD
RES = 128
DIMS = (60, 40)
SCREEN = (1700, 980)#(DIMS[0]*RES, DIMS[1]*RES) 
display = pygame.display.set_mode(SCREEN)
'''
TILES = "tiles"
PATH = f"TilesWFC/TilesWFC/{TILES}/res_{RES}/"
PATH_METADATA = f"TilesWFC/TilesWFC/{TILES}/metadata.txt"
'''


#for our tiles
TILES = "tiles"
PATH = f"{TILES}/res_{RES}/"
PATH_METADATA = f"{TILES}/metadata.txt"



#angle will be 0, 1, 2 or 3 for each 90 degree rotation 0 = no change 
def rotateSockets(sockets, angle):
    return [sockets[i-angle] for i in range(4)]


# DD. METADATA
# metadata = [Dict, ...]
# interp. a collection of metadata for the tiles that can be used in the WFC
metadata = []
with open(PATH_METADATA, "r") as file:
    file = file.readlines()
    for line in file:
        line = line.strip().split("\t")
        if line[5] == "1":
            metaEntry = {"ID": line[0], "SOCKETS": [
                line[1], line[2], line[3], line[4]], "FIXED": True, "ROTATION": 0}
            metadata.append(metaEntry)
        # for rotation, we create a new entry for each rotation of the tile
        else:
            for a in range(4):
                metaEntry = {"ID": line[0], "SOCKETS": rotateSockets(
                    [line[1], line[2], line[3], line[4]], a), "FIXED": False, "ROTATION": a}
                metadata.append(metaEntry)

#compares opposite ends of the string, see if they match
def socketMatch(socket, targetsocket):
    for idx_letter, _ in enumerate(socket):
        if socket[idx_letter] != targetsocket[-(idx_letter+1)]:
            return False
    return True

# DD. TILE
# tile = Tile()
# interp. a tile for the animation of WFC in a 2D grid

# c is column, r is row
class Tile:
    def __init__(self, c, r):
        self.c = c
        self.r = r
        self.x = self.c * RES
        self.y = self.r * RES
        self.img = pygame.image.load(PATH + f"{metadata[-1]['ID']}.png") 
        self.rect = self.img.get_rect()
        self.rect.topleft = self.x, self.y
        # attr. related to WFC
        self.entropy = len(metadata)
        self.potentialTiles = list(metadata) #will be updated as WFC runs
        self.collapsed = False
        self.sockets = ["" for _ in range(4)] # created when collapsed
        self.RIGHT_neigh = {"COLLAPSED": None, "SOCKET": None}
        self.DOWN_neigh = {"COLLAPSED": None, "SOCKET": None}
        self.LEFT_neigh = {"COLLAPSED": None, "SOCKET": None}
        self.UP_neigh = {"COLLAPSED": None, "SOCKET": None}

    def draw(self):
        display.blit(self.img, self.rect)

    def updateEntropy(self, lowestEntropy):
        placeHolderTileSet = []
        for potTile in self.potentialTiles:
            # assume tile is valid until a neighbor proves otherwise
            validTile = True
            if self.RIGHT_neigh["COLLAPSED"] and not socketMatch(potTile["SOCKETS"][0], self.RIGHT_neigh["SOCKET"]):
                validTile = False
            if self.DOWN_neigh["COLLAPSED"] and not socketMatch(potTile["SOCKETS"][1], self.DOWN_neigh["SOCKET"]):
                validTile = False
            if self.LEFT_neigh["COLLAPSED"] and not socketMatch(potTile["SOCKETS"][2], self.LEFT_neigh["SOCKET"]):
                validTile = False
            if self.UP_neigh["COLLAPSED"] and not socketMatch(potTile["SOCKETS"][3], self.UP_neigh["SOCKET"]):
                validTile = False

            if validTile:
                placeHolderTileSet.append(potTile)
        self.potentialTiles = placeHolderTileSet

        # Only goes through each single tile once
        seenTile = []
        for tile in self.potentialTiles:
            if tile["ID"] not in seenTile:
                seenTile.append(tile["ID"])
        self.entropy = len(seenTile)
        if lowestEntropy == None or self.entropy < lowestEntropy: # if it is none it is the first tile
            return self.entropy
        return lowestEntropy

    def updateNeighbors(self):
        if not self.collapsed:
            c = self.c
            r = self.r

            if c < DIMS[0]-1:
                self.RIGHT_neigh = {
                    "COLLAPSED": grid[r][c+1].collapsed, "SOCKET": grid[r][c+1].sockets[2]}
            if r < DIMS[1]-1:
                self.DOWN_neigh = {
                    "COLLAPSED": grid[r+1][c].collapsed, "SOCKET": grid[r+1][c].sockets[3]}
            if c > 0:
                self.LEFT_neigh = {
                    "COLLAPSED": grid[r][c-1].collapsed, "SOCKET": grid[r][c-1].sockets[0]}
            if r > 0:
                self.UP_neigh = {
                    "COLLAPSED": grid[r-1][c].collapsed, "SOCKET": grid[r-1][c].sockets[1]}

    def collapse(self):
        self.collapsed = True
        if len(self.potentialTiles) > 0:
            potTile = random.choice(self.potentialTiles)
        else:
            potTile = metadata[-1]
        self.name = potTile["ID"]
        self.img = pygame.image.load(f"{PATH}/{self.name}.png")
        self.sockets = potTile["SOCKETS"]
        self.entropy = 0
        self.img = pygame.transform.rotate(self.img, -potTile["ROTATION"] * 90)


# DD. GRID
# grid = [[TILE, ..., n=DIMS[0]], ..., n=DIMS[1]]
# interp. 2D array of TILE
grid = []
for r in range(DIMS[1]):
    row = []
    for c in range(DIMS[0]):
        tile = Tile(c, r)
        row.append(tile)
    grid.append(row)

# TEMPLATE FOR GRID
# for row in grid:
#   ... row
#   for tile in row:
#       ... tile

# CODE

grid[0][0].collapse()


def draw():
    display.fill("#1e1e1e")
    for row in grid:
        for tile in row:
            tile.draw()
    pygame.display.flip()


def update():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()


    for row in grid:
        for tile in row:
            tile.updateNeighbors()

    lowestEntropy = None
    for row in grid:
        for tile in row:
            if not tile.collapsed:
                lowestEntropy = tile.updateEntropy(lowestEntropy)

    candidates = []
    for row in grid:
        for tile in row:
            if not tile.collapsed and tile.entropy == lowestEntropy:
                candidates.append(tile)

    if len(candidates) > 0:
        candidates[0].collapse() # Can change to random, or pick the last

while True:
    draw()
    update()