import networkx as nx
from matplotlib import pyplot as plt

dag = nx.DiGraph()
dag.add_edges_from([("root", "village"), ("root", "castle"), ("root", "land"), ("village", "house"), ("village", "road"), ("castle", "road"), ("land", "road"), ("land", "water"), ("house", "22"), ("house", "6"), ("house", "6"), ("house", "8"), ("house", "23"), ("road", "23"), ("road", "7"), ("road", "9"), ("house", "24"), ("road", "24"), ("water", "24"), ("road", "0"), ("castle", "0"), ("road", "1"), ("castle", "1"), ("road", "2"), ("castle", "2"), ("road", "5"), ("castle", "5"), ("road", "12"), ("castle", "12"), ("road", "14"), ("castle", "14"), ("road", "26"), ("castle", "26"), ("water", "26"), ("castle", "3"), ("castle", "4"), ("castle", "10"), ("castle", "11"), ("castle", "13"), ("castle", "15"), ("road", "21"), ("water", "21"), ("road", "25"), ("water", "25"), ("castle", "18"), ("water", "18"), ("castle", "20"), ("water", "20"), ("water", "16"), ("water", "17"), ("water", "19")])

print(nx.is_directed_acyclic_graph(dag))
plt.tight_layout()
nx.draw_networkx(dag, arrows=True)
plt.savefig("dag.png", format="PNG")
plt.clf()
terminalTiles = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"]
metaTiles = ["village", "castle", "land", "house", "road", "water"]

while terminalTiles != []:
    currentTile = terminalTiles[0]
    for meta in metaTiles:
        if (meta, currentTile) in dag.edges:
            print(f"{currentTile} is a child of {meta}")
