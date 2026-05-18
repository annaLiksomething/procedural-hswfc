import networkx as nx
from matplotlib import pyplot as plt
from queue import Queue
import pygame
import random



dag = nx.DiGraph()
dag.add_weighted_edges_from([("root", "village", 0.3), ("root", "castle", 0.4), ("root", "land", 0.3), ("village", "house", 0.1), ("village", "road", 0.1), ("land", "road", 0.1), ("land", "water", 0.1), ("house", "22", 0.1), ("house", "6", 0.1), ("house", "6", 0.1), ("house", "8", 0.1), ("house", "23", 0.1), ("road", "7", 0.1), ("road", "9", 0.1), ("house", "24", 0.1), ("water", "24", 0.1), ("castle", "0", 0.1), ("castle", "1", 0.1), ("castle", "2", 0.1), ("castle", "5", 0.1), ("castle", "12", 0.1), ("castle", "14", 0.1), ("castle", "26", 0.1), ("water", "26", 0.1), ("castle", "3", 0.1), ("castle", "4", 0.1), ("castle", "10", 0.1), ("castle", "11", 0.1), ("castle", "13", 0.1), ("castle", "15", 0.1), ("road", "21", 0.1), ("water", "21", 0.1), ("road", "25", 0.1), ("water", "25", 0.1), ("castle", "18",0.1), ("water", "18", 0.1), ("castle", "20", 0.1), ("water", "20", 0.1), ("water", "16", 0.1), ("water", "17", 0.1), ("water", "19", 0.1), ("house", "27", 0.1)])


meta_tiles = ["village", "castle", "land", "road", "water", "house"]


terminal_q = Queue()
collapsed_tiles = Queue()
tiles_collapsed =[]


for i in range(28):
    terminal_q.put(str(i))
    

# MODULES


# DD
RES = 128
DIMS = (14, 8) #14x8
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
        self.collapsed = True
        if len(self.potentialTiles) > 0:  
            #decide which tile depending on their weight 
            weight = 0 
            potTiles=[]
            for tile in self.potentialTiles:
                id = str(tile["ID"])
                predec = list(dag.predecessors(id))
                for pre in predec:
                    w = dag[pre][id]["weight"]
                    predec_l2 = list(dag.predecessors(pre))
                    if predec_l2 != []:
                        for pre_l2 in predec_l2:
                            f = w
                            w+=dag[pre_l2][pre]["weight"]
                            predec_l3 = list(dag.predecessors(pre_l2))
                            if predec_l3 == []:
                                if w > weight: 
                                    weight = w
                                    potTiles = [tile]
                                elif w == weight:
                                    weight = w
                                    potTiles.append(tile)
                            else:
                                pre_l3 = predec_l3[0] #based on how our graph look there should only be one here
                                w+=dag[pre_l3][pre_l2]["weight"]
                                if w > weight:
                                    weight = w
                                    potTiles = [tile]
                                elif w == weight: 
                                    weight = w
                                    potTiles.append(tile)

                                w = f #reset to what it was in the beginning of this loop
      
            potTile = random.choice(potTiles) #if there are more tiles with the same weight, choose randomly
            self.name = potTile["ID"]
            self.metatile =  list(dag.predecessors(self.name))
            self.img = pygame.image.load(f"{PATH}/{self.name}.png")
            self.sockets = potTile["SOCKETS"]
            self.id = potTile["ID"]
            self.entropy = 0
            self.img = pygame.transform.rotate(self.img, -potTile["ROTATION"] * 90)
            tiles_collapsed.append(self)           
        else:
            self.collapsed = False
            self.potentialTiles = list(metadata)
            explode_neighbors(self)
            last_collapsed = tiles_collapsed.pop()
            explode_neighbors(last_collapsed)
        
        
# DD. GRID
# grid = [[TILE, ..., n=DIMS[0]], ..., n=DIMS[1]]
# interp. 2D array of TILE
grid = []
for r in range(DIMS[1]):
    row = []
    for c in range(DIMS[0]):
        tile = Tile(c, r)
        row.append(tile)
        # uncollapsed_q.put(tile)
    grid.append(row)

# TEMPLATE FOR GRID
# for row in grid:
#   ... row
#   for tile in row:
#       ... tile

# CODE

grid[0][0].collapse()

all_tiles_collapsed = False #variable to check when to end the algorithm

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
    all_tiles_collapsed = True
    for row in grid:
        for tile in row:
            if not tile.collapsed:
                lowestEntropy = tile.updateEntropy(lowestEntropy)
                all_tiles_collapsed = False #if there is an uncollapsed tile this is set to false so update will be run again

    candidates = []
    for row in grid:
        for tile in row:
            if not tile.collapsed and tile.entropy == lowestEntropy:
                candidates.append(tile)
   
    if len(candidates) > 0:
        random.choice(candidates).collapse() 

    return all_tiles_collapsed

    
def explode_neighbors(tile):
    if tile.RIGHT_neigh["COLLAPSED"]==True:
        if tile.c < DIMS[0]-1:
            grid[tile.r][tile.c+1].collapsed = False
            grid[tile.r][tile.c+1].potentialTiles = list(metadata)

     
    if tile.DOWN_neigh["COLLAPSED"]==True:                    
        if tile.r < DIMS[1]-1:   
            grid[tile.r+1][tile.c].collapsed = False
            grid[tile.r+1][tile.c].potentialTiles = list(metadata)

    
    if tile.LEFT_neigh["COLLAPSED"]==True: 
        if tile.c > 0:       
            grid[tile.r][tile.c-1].collapsed = False
            grid[tile.r][tile.c-1].potentialTiles = list(metadata)

    
    if tile.UP_neigh["COLLAPSED"]==True:
        if tile.r > 0:
            grid[tile.r-1][tile.c].collapsed = False
            grid[tile.r-1][tile.c].potentialTiles = list(metadata)

            
def propagation(queue_collapsed_tiles, lowestEntropy):
    while not queue_collapsed_tiles.empty():
        tile = queue_collapsed_tiles.get()
        for neighbor in [tile.RIGHT_neigh, tile.DOWN_neigh, tile.LEFT_neigh, tile.UP_neigh]:
            adj = list(metadata)
            cur = tile.potentialTiles #allowed tiles for tile'
            pre = [] #allowed tiles for neighbor
            if neighbor == tile.RIGHT_neigh:
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

            if n!= None:
                n.potentialTiles = post
                n.updateEntropy(lowestEntropy)
                if len(post) < len(pre) and n.collapsed:
                    queue_collapsed_tiles.put(n)

#this will run until all tiles are collapsed
while not all_tiles_collapsed: 

    draw()
    all_tiles_collapsed = update()
    if all_tiles_collapsed:
        pygame.image.save(display, "finalresult.png")
        pygame.quit()
