import json
from queue import PriorityQueue

# Example instance
G = {
    'S': ['1', '2', '3'], 
    '1': ['S', 'T'], 
    '2': ['S', 'T'], 
    '3': ['S', 'T'], 
    'T': ['1', '2', '3']
}

Dist = {
    'S,1': 4, 
    '1,S': 4, 
    'S,2': 2, 
    '2,S': 2, 
    'S,3': 4, 
    '3,S': 4, 
    '1,T': 8, 
    'T,1': 8, 
    '2,T': 8, 
    'T,2': 8, 
    '3,T': 12, 
    'T,3': 12
}

Cost = {
    'S,1': 7, 
    '1,S': 7, 
    'S,2': 6, 
    '2,S': 6, 
    'S,3': 3, 
    '3,S': 3, 
    '1,T': 3, 
    'T,1': 3, 
    '2,T': 6, 
    'T,2': 6, 
    '3,T': 2, 
    'T,3': 2
}

# # Problem instance dictionaries
# G = {}
# Dist = {}
# Cost = {}
# Coord = {}

# Constants
START = 'S'
END = 'T'
BUDGET = 11


# Load instance files
def init():
    global G, Dist, Cost
    with open('G.json') as f:
        G = json.load(f)
    with open('Dist.json') as f:
        Dist = json.load(f)
    with open('Cost.json') as f:
        Cost = json.load(f)
    # with open('Coord.json') as f:
    #     Coord = json.load(f)


# Uniform cost search (no energy constraint)
def ucs_noconstraint(start, goal):
    queue = PriorityQueue()

    # Initialization
    queue.put((0, start))       # Add start node to queue with priority 0
    explored = {}               # Dict of explored nodes {node: parent node}
    explored[start] = None      # Start node has no parent node
    path_distance = {}          # Dict of distance from start to node
    path_distance[start] = 0    # Start to start distance should be 0
    path_cost = {}
    path_cost[start] = 0

    while not queue.empty():
        # Deqeue
        current_node = queue.get()[1]

        # Stop when goal is reached
        if current_node == goal:
            path = construct_path(explored, start, goal)
            return path, path_distance[current_node], path_cost[current_node]

        # Explore every single neighbor of current node
        for neighbor in G[current_node]:
            # Calculate new path distance based on current node
            new_distance = path_distance[current_node] + Dist[','.join([current_node, neighbor])]
            if neighbor not in explored or new_distance < path_distance[neighbor]:
                # Enqueue with new priority
                queue.put((new_distance, neighbor))
                # Assign current node as parent
                explored[neighbor] = current_node
                # Update path distance
                path_distance[neighbor] = new_distance
                # Update path cost
                path_cost[neighbor] = path_cost[current_node] + Cost[','.join([current_node, neighbor])]


# def calculate_cost(path):
#     cost = 0
#     for i in range(len(path)-1):
#         cost += Cost[','.join([path[i], path[i+1]])]
#     return cost


def construct_path(explored, start, goal):
    # Start from goal node
    current_node = goal
    path = []

    # Backtrack until start node
    while current_node != start:
        path.append(current_node)
        current_node = explored[current_node]
    
    # Append start node and reverse path
    path.append(start)
    return path[::-1]


if __name__ == '__main__':
    # init()
    path, distance, cost = ucs_noconstraint(START, END)
    print('Shortest path: {}.'.format('->'.join(path)))
    print('Shortest distance: {}.'.format(str(distance)))
    print('Total energy cost: {}.'.format(str(cost)))
