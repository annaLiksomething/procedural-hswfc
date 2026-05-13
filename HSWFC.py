import networkx as nx
from matplotlib import pyplot as plt
from queue import Queue
import pygame
import random


dag = nx.DiGraph()
dag.add_weighted_edges_from([("root", "village", 0.4), ("root", "castle", 0.2), ("root", "land", 0.4), ("village", "house", 0.6), ("village", "road", 0.4), ("castle", "road", 0.4), ("land", "road", 0.6), ("land", "water", 0.4), ("house", "22", 0.1), ("house", "6", 0.1), ("house", "6", 0.1), ("house", "8", 0.1), ("house", "23", 0.1), ("road", "23", 0.1), ("road", "7", 0.1), ("road", "9", 0.1), ("house", "24", 0.1), ("road", "24", 0.1), ("water", "24", 0.1), ("road", "0", 0.1), ("castle", "0", 0.1), ("road", "1", 0.1), ("castle", "1", 0.1), ("road", "2", 0.1), ("castle", "2", 0.1), ("road", "5", 0.1), ("castle", "5", 0.1), ("road", "12", 0.1), ("castle", "12", 0.1), ("road", "14", 0.1), ("castle", "14", 0.1), ("road", "26", 0.1), ("castle", "26", 0.1), ("water", "26", 0.1), ("castle", "3", 0.1), ("castle", "4", 0.1), ("castle", "10", 0.1), ("castle", "11", 0.1), ("castle", "13", 0.1), ("castle", "15", 0.1), ("road", "21", 0.1), ("water", "21", 0.1), ("road", "25", 0.1), ("water", "25", 0.1), ("castle", "18",0.1), ("water", "18", 0.1), ("castle", "20", 0.1), ("water", "20", 0.1), ("water", "16", 0.1), ("water", "17", 0.1), ("water", "19", 0.1), ("house", "27", 0.1)])

meta_tiles = ["village", "castle", "land", "road", "water", "house"]
# adjacency_constraints = {"house":[]}
terminal_q = Queue()
collapsed_tiles = Queue()
uncollapsed_q = Queue()


for i in range(28):
    terminal_q.put(str(i))
    

# MODULES


# DD
RES = 128
DIMS = (13, 7) #14x8)
SCREEN = (DIMS[0]*RES, DIMS[1]*RES) 
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

def metaConstraints(currentTile, neighborTile):
    if dag.has_edge("house", currentTile["ID"]) and dag.has_edge("castle", neighborTile["ID"]):
        return False
    if dag.has_edge("castle", currentTile["ID"]) and dag.has_edge("house", neighborTile["ID"]):
        return False
    return True

# DD. TILE
# tile = Tile()
# interp. a tile for the animation of WFC in a 2D grid

# c is column, r is row
class Tile:
    def __init__(self, c, r):
        # self.name = metadata[-1]['ID']
        self.c = c
        self.r = r
        self.x = self.c * RES
        self.y = self.r * RES
        self.img = pygame.image.load(PATH + f"{metadata[-1]['ID']}.png") 
        self.rect = self.img.get_rect()
        self.rect.topleft = self.x, self.y
        # attr. related to WFC
        self.metatile = None
        self.entropy = len(metadata)
        self.potentialTiles = list(metadata) #will be updated as WFC runs
        self.collapsed = False
        self.sockets = ["" for _ in range(4)] # created when collapsed
        self.id = ""
        self.RIGHT_neigh = {"COLLAPSED": None, "SOCKET": None, "ID": None}
        self.DOWN_neigh = {"COLLAPSED": None, "SOCKET": None, "ID": None}
        self.LEFT_neigh = {"COLLAPSED": None, "SOCKET": None, "ID": None}
        self.UP_neigh = {"COLLAPSED": None, "SOCKET": None, "ID": None}

    def draw(self):
        display.blit(self.img, self.rect)
       
    def updateEntropy(self, lowestEntropy):
        
        placeHolderTileSet = []   
        for potTile in self.potentialTiles:            
            # assume tile is valid until a neighbor proves otherwise
            validTile = True
            if self.RIGHT_neigh["COLLAPSED"] and not socketMatch(potTile["SOCKETS"][0], self.RIGHT_neigh["SOCKET"]) or not metaConstraints(potTile, self.RIGHT_neigh):
                validTile = False
            if self.DOWN_neigh["COLLAPSED"] and not socketMatch(potTile["SOCKETS"][1], self.DOWN_neigh["SOCKET"]) or not metaConstraints(potTile, self.DOWN_neigh):
                validTile = False
            if self.LEFT_neigh["COLLAPSED"] and not socketMatch(potTile["SOCKETS"][2], self.LEFT_neigh["SOCKET"]) or not metaConstraints(potTile, self.LEFT_neigh):
                validTile = False
            if self.UP_neigh["COLLAPSED"] and not socketMatch(potTile["SOCKETS"][3], self.UP_neigh["SOCKET"]) or not metaConstraints(potTile, self.UP_neigh):
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
                    "COLLAPSED": grid[r][c+1].collapsed, "SOCKET": grid[r][c+1].sockets[2], "ID": grid[r][c+1].id}
            if r < DIMS[1]-1:
                self.DOWN_neigh = {
                    "COLLAPSED": grid[r+1][c].collapsed, "SOCKET": grid[r+1][c].sockets[3], "ID": grid[r+1][c].id}
            if c > 0:
                self.LEFT_neigh = {
                    "COLLAPSED": grid[r][c-1].collapsed, "SOCKET": grid[r][c-1].sockets[0], "ID": grid[r][c-1].id}
            if r > 0:
                self.UP_neigh = {
                    "COLLAPSED": grid[r-1][c].collapsed, "SOCKET": grid[r-1][c].sockets[1], "ID": grid[r-1][c].id}

    

    def collapse(self):
        print("current tile:", self.c, self.r, "with entropy", self.entropy)
        self.collapsed = True
        # self.collapsed = True
        # collapsed_tiles.put(self)
        # uncollapsed_tiles.remove(self)
        # print("uncollapsed after collapse", uncollapsed_q.queue)
        # print("Collapsed tiles:", collapsed_tiles.qsize(), collapsed_tiles.queue)
        if len(self.potentialTiles) > 1:  
            weight = 0
            for potTile in self.potentialTiles:
            #print(candidate["ID"])
                identity = potTile["ID"]
                
                anc = dag.successors(str(identity))
                print("ancestors of", id, ":", anc)
            # root = [n for n in anc if G.in_degree(n) == 0] [0]          
            potTile = random.choice(self.potentialTiles)
            self.name = potTile["ID"]
            self.metatile =  list(dag.predecessors(self.name))
            # print("metatile", self.metatile)
            # print("collapsed tile", self.name)
            self.img = pygame.image.load(f"{PATH}/{self.name}.png")
            self.sockets = potTile["SOCKETS"]
            self.id = potTile["ID"]
            self.entropy = 0
            self.img = pygame.transform.rotate(self.img, -potTile["ROTATION"] * 90)            
        else:
            self.collapsed = False
            self.potentialTiles = list(metadata)
            print("no potential tiles left, backtracking")
            explode_neighbors(self)
        
        


# DD. GRID
# grid = [[TILE, ..., n=DIMS[0]], ..., n=DIMS[1]]
# interp. 2D array of TILE
grid = []
for r in range(DIMS[1]):
    row = []
    for c in range(DIMS[0]):
        tile = Tile(c, r)
        row.append(tile)
        uncollapsed_q.put(tile)
        # print("uncollapsed tiles_grid", uncollapsed_q.queue)
    grid.append(row)

# TEMPLATE FOR GRID
# for row in grid:
#   ... row
#   for tile in row:
#       ... tile

# CODE

grid[0][0].collapse()
# grid[0][0].check_meta_constraints()
# print("predecessors of 26:", list(dag.predecessors("26")))

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
                # tile.check_meta_constraints()
                lowestEntropy = tile.updateEntropy(lowestEntropy)

    candidates = []
    for row in grid:
        for tile in row:
            if not tile.collapsed and tile.entropy == lowestEntropy:
                candidates.append(tile)
    # print("candidates", len(candidates))
    if len(candidates) > 0:
        random.choice(candidates).collapse() # Can change to random, or pick the last
            
    # propagation(collapsed_tiles, lowestEntropy)
    
def explode_neighbors(tile):
    print("exploding neighbors of tile", tile.c, tile.r)   
    if tile.RIGHT_neigh["COLLAPSED"]==True:
        if tile.c < DIMS[0]-1:
            print("exploding right neighbor", grid[tile.r][tile.c+1].c, grid[tile.r][tile.c+1].r)
            grid[tile.r][tile.c+1].collapsed = False
            grid[tile.r][tile.c+1].potentialTiles = list(metadata)
            # collapsed_tiles.get(grid[tile.r][tile.c+1])
            # grid[tile.r][tile.c+1].updateEntropy(lowestEntropy)
     
    if tile.DOWN_neigh["COLLAPSED"]==True:                    
        if tile.r < DIMS[1]-1:   
            print("exploding down neighbor", grid[tile.r+1][tile.c].c, grid[tile.r+1][tile.c].r)
            grid[tile.r+1][tile.c].collapsed = False
            grid[tile.r+1][tile.c].potentialTiles = list(metadata)
            # grid[tile.r+1][tile.c].updateEntropy(lowestEntropy)
            # uncollapsed_tiles.append(grid[tile.r+1][tile.c])
    
    if tile.LEFT_neigh["COLLAPSED"]==True: 
        if tile.c > 0:       
            print("exploding left neighbor", grid[tile.r][tile.c-1].c, grid[tile.r][tile.c-1].r)
            grid[tile.r][tile.c-1].collapsed = False
            grid[tile.r][tile.c-1].potentialTiles = list(metadata)
            # grid[tile.r][tile.c-1].updateEntropy(lowestEntropy)
            # uncollapsed_tiles.append(grid[tile.r][tile.c-1])
    
    if tile.UP_neigh["COLLAPSED"]==True:
        if tile.r > 0:
            print("exploding up neighbor", grid[tile.r-1][tile.c].c, grid[tile.r-1][tile.c].r)
            grid[tile.r-1][tile.c].collapsed = False
            grid[tile.r-1][tile.c].potentialTiles = list(metadata)
            # grid[tile.r-1][tile.c].updateEntropy(lowestEntropy)
            # uncollapsed_tiles.append(grid[tile.r-1][tile.c])


# def depropagation(list_uncollapsed_tiles):
#     P = []
#     while len(list_uncollapsed_tiles) > 0:
#         tile = list_uncollapsed_tiles[0]
#         list_uncollapsed_tiles.remove(tile)
#         for neighbor in [tile.RIGHT_neigh, tile.DOWN_neigh, tile.LEFT_neigh, tile.UP_neigh]:
#             pre = []
#             post = []
#             if neighbor == tile.RIGHT_neigh:
#                 # print("right neighbor")               
#                 if tile.c < DIMS[0]-1:
#                     pre = grid[tile.r][tile.c+1].potentialTiles   
#                     post = neighbor["ID"]         
#             if neighbor == tile.DOWN_neigh:
#                 if tile.r < DIMS[1]-1:
#                         pre = grid[tile.r+1][tile.c].potentialTiles
#                         post = neighbor["ID"] 
#             if neighbor == tile.LEFT_neigh:
#                 if tile.c > 0:
#                     pre = grid[tile.r][tile.c-1].potentialTiles
#                     post = neighbor["ID"] 
#             if neighbor == tile.UP_neigh:
#                 if tile.r > 0:
#                     pre = grid[tile.r-1][tile.c].potentialTiles
#                     post = neighbor["ID"] 
#             # print("pre", [tile["ID"] for tile in pre])
            


def propagation(queue_collapsed_tiles, lowestEntropy):
    while not queue_collapsed_tiles.empty():
        tile = queue_collapsed_tiles.get()
        for neighbor in [tile.RIGHT_neigh, tile.DOWN_neigh, tile.LEFT_neigh, tile.UP_neigh]:
            adj = list(metadata)
            # print("all tiles", [tile["ID"] for tile in adj])
            cur = tile.potentialTiles #allowed tiles for tile'
            pre = [] #allowed tiles for neighbor
            if neighbor == tile.RIGHT_neigh:
                # print("right neighbor")               
                if tile.c < DIMS[0]-1:
                    pre = grid[tile.r][tile.c+1].potentialTiles                  
            if neighbor == tile.DOWN_neigh:
                if tile.r < DIMS[1]-1:
                        pre = grid[tile.r+1][tile.c].potentialTiles
            if neighbor == tile.LEFT_neigh:
                if tile.c > 0:
                    pre = grid[tile.r][tile.c-1].potentialTiles
            if neighbor == tile.UP_neigh:
                if tile.r > 0:
                    pre = grid[tile.r-1][tile.c].potentialTiles
            # print("pre", [tile["ID"] for tile in pre])
            for tile_cur in cur:                
                placeHolderTileSet = []      
                for potTile in adj:
                    validTile = True
                    if neighbor == tile.RIGHT_neigh:
                        if not socketMatch(potTile["SOCKETS"][2], tile_cur["SOCKETS"][0]):
                            validTile = False
                    if neighbor == tile.DOWN_neigh:
                        if not socketMatch(potTile["SOCKETS"][3], tile_cur["SOCKETS"][1]):
                            validTile = False
                    if neighbor == tile.LEFT_neigh:
                        if not socketMatch(potTile["SOCKETS"][0], tile_cur["SOCKETS"][2]):
                            validTile = False
                    if neighbor == tile.UP_neigh:
                        if not socketMatch(potTile["SOCKETS"][1], tile_cur["SOCKETS"][3]):
                            validTile = False
                    if validTile:
                        placeHolderTileSet.append(potTile)

                adj = placeHolderTileSet
                # print("adj", [tile["ID"] for tile in adj])

            post = []    
            for tile_pre in pre:
                if tile_pre in adj:
                    post.append(tile_pre)
            
            n = None
            if neighbor == tile.RIGHT_neigh:               
                if tile.c < DIMS[0]-1:
                    n = grid[tile.r][tile.c+1]
            if neighbor == tile.DOWN_neigh:
                if tile.r < DIMS[1]-1:
                        n = grid[tile.r+1][tile.c]
            if neighbor == tile.LEFT_neigh:
                if tile.c > 0:
                    n = grid[tile.r][tile.c-1]
            if neighbor == tile.UP_neigh:
                if tile.r > 0:
                    n = grid[tile.r-1][tile.c]
            # print("post", [tile["ID"] for tile in post])   

            if n!= None:
                # n.collapsed = False
                # print("updating neighbor", n)
                n.potentialTiles = post
                n.updateEntropy(lowestEntropy)
                # n.collapse()

                if len(post) < len(pre) and n.collapsed:
                    queue_collapsed_tiles.put(n)


while True:

    draw()
    update()
