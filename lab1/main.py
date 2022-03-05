import json
import math
import heapq

# Example 1 (from lab manual)
# ====================================================================================================
# # Constants
# START = 'S'
# END = 'T'
# BUDGET = 11

# # Dictionaries
# G = {
#     'S': ['1', '2', '3'], 
#     '1': ['S', 'T'], 
#     '2': ['S', 'T'], 
#     '3': ['S', 'T'], 
#     'T': ['1', '2', '3']
# }

# Dist = {
#     'S,1': 4, 
#     '1,S': 4, 
#     'S,2': 2, 
#     '2,S': 2, 
#     'S,3': 4, 
#     '3,S': 4, 
#     '1,T': 8, 
#     'T,1': 8, 
#     '2,T': 8, 
#     'T,2': 8, 
#     '3,T': 12, 
#     'T,3': 12
# }

# Cost = {
#     'S,1': 7, 
#     '1,S': 7, 
#     'S,2': 6, 
#     '2,S': 6, 
#     'S,3': 3, 
#     '3,S': 3, 
#     '1,T': 3, 
#     'T,1': 3, 
#     '2,T': 6, 
#     'T,2': 6, 
#     '3,T': 2, 
#     'T,3': 2
# }


# Example 2
# ====================================================================================================
# # Constants
# START = '1'
# END = '6'
# BUDGET = 17

# # Dictionaries
# G = {
#     '1': ['2', '3'], 
#     '2': ['4', '5'], 
#     '3': ['2', '4', '5'], 
#     '4': ['5', '6'], 
#     '5': ['6'], 
#     '6': []
# }

# Dist = {
#     '1,2': 1, 
#     '1,3': 10, 
#     '2,4': 1, 
#     '2,5': 2, 
#     '3,2': 1, 
#     '3,4': 5, 
#     '3,5': 12, 
#     '4,5': 10, 
#     '4,6': 1, 
#     '5,6': 2
# }

# Cost = {
#     '1,2': 10, 
#     '1,3': 3, 
#     '2,4': 1, 
#     '2,5': 3, 
#     '3,2': 2, 
#     '3,4': 7, 
#     '3,5': 3, 
#     '4,5': 1, 
#     '4,6': 7, 
#     '5,6': 2
# }


# NYC instance
# ====================================================================================================
# Constants
START = '1'
END = '50'
BUDGET = 287932
NO_PATH = (START, 0, 0)  # Output to print if no path

# Dictionaries
G = {}
Dist = {}
Cost = {}
Coord = {}


def init():
    """
    Initialize by loading the instance files (JSON) into dictionaries.
    """
    global G, Dist, Cost, Coord
    with open('G.json') as f:
        G = json.load(f)
    with open('Dist.json') as f:
        Dist = json.load(f)
    with open('Cost.json') as f:
        Cost = json.load(f)
    with open('Coord.json') as f:
        Coord = json.load(f)


# [TASK 1]
# ====================================================================================================
def ucs_noconstraint(start, goal):
    """
    Uniform cost search with no energy constraint.

    Return the shortest path, distance travelled and energy consumed.
    """
    # Initialization
    pq = [(0, 0, start)]        # Min-heap priority queue (dist, cost, node)
    came_from = {start: None}   # Dict of predecessors {node: predecessor}
    distances = {start: 0}      # Dict of distance from start to node
    visited = set()             # Set of visited nodes

    while pq:
        # Dequeue
        dist, cost, node = heapq.heappop(pq)
        
        if node in visited:
            continue

        # Return solution when goal is reached
        if node == goal:
            path = reconstruct_path(came_from, start, goal)
            return path, dist, cost

        # Mark as visited
        visited.add(node)

        for neighbor in G[node]:
            # Calculate new distance based on current node
            new_dist = dist + Dist[','.join([node, neighbor])]
            # Return infinity as value if key not in dict (to avoid KeyError)
            # so new distance will always be lower for first time visited nodes
            if new_dist < distances.get(neighbor, float('inf')):
                # Update distances dict
                distances[neighbor] = new_dist
                # Calculate new cost based on current node
                new_cost = cost + Cost[','.join([node, neighbor])]
                # Assign current node as predecessor
                came_from[neighbor] = node
                # Enqueue
                entry = (new_dist, new_cost, neighbor)
                heapq.heappush(pq, entry)
                
    # Path not found
    return None


# [TASK 2]
# ====================================================================================================
def ucs(start, goal):
    """
    Uniform cost search with energy constraint.

    Return the shortest path, distance travelled and energy consumed.
    """
    # Initialization
    pq = [(0, 0, start)]        # Min-heap priority queue (dist, cost, node)
    came_from = {start: None}   # Dict of predecessors {node: predecessor}
    distances = {start: 0}      # Dict of distance from start to node
    costs = {start: 0}          # Dict of cost from start to node

    while pq:
        # Dequeue
        dist, cost, node = heapq.heappop(pq)

        # Return solution when goal is reached
        if node == goal:
            path = reconstruct_path(came_from, start, goal)
            return path, dist, cost

        for neighbor in G[node]:
            # Calculate new distance and cost based on current node
            new_dist = dist + Dist[','.join([node, neighbor])]
            new_cost = cost + Cost[','.join([node, neighbor])]
            if new_cost > BUDGET:
                continue
            # Return infinity as value if key not in dict (to avoid KeyError)
            # so new distance and cost will always be lower for first time visited nodes
            if new_dist < distances.get(neighbor, float('inf')) or new_cost < costs.get(neighbor, float('inf')):
                # If new distance is shorter, update distances dict
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                # If new cost is lower, update costs dict
                if new_cost < costs.get(neighbor, float('inf')):
                    costs[neighbor] = new_cost
                # Assign current node as predecessor
                came_from[neighbor] = node
                # Enqueue
                entry = (new_dist, new_cost, neighbor)
                heapq.heappush(pq, entry)
    
    # Path not found
    return None


# [TASK 3]
# ====================================================================================================
def heuristic(node1, node2):
    """
    Heuristic function for A* search to get estimated shortest distance from node to goal.
    
    Return the straight-line distance between two nodes based on their coordinates.
    """
    x1, y1 = Coord[node1]
    x2, y2 = Coord[node2]
    return math.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))


def astar(start, goal):
    """
    A* search with energy constraint.

    Return the shortest path, distance travelled and energy consumed.
    """
    # Initialization
    pq = [(0, 0, 0, start)]     # Min-heap priority queue (fscore, dist, cost, node)
    came_from = {start: None}   # Dict of predecessors {node: predecessor}
    distances = {start: 0}      # Dict of distance from start to node
    costs = {start: 0}          # Dict of cost from start to node

    while pq:
        # Dequeue
        fscore, dist, cost, node = heapq.heappop(pq)

        # Return solution when goal is reached
        if node == goal:
            path = reconstruct_path(came_from, start, goal)
            return path, dist, cost

        for neighbor in G[node]:
            # Calculate new distance and cost based on current node
            new_dist = dist + Dist[','.join([node, neighbor])]
            new_cost = cost + Cost[','.join([node, neighbor])]
            if new_cost > BUDGET:
                continue
            # Return infinity as value if key not in dict (to avoid KeyError)
            # so new distance and cost will always be lower for first time visited nodes
            if new_dist < distances.get(neighbor, float('inf')) or new_cost < costs.get(neighbor, float('inf')):
                # If new distance is lower, update distances dict
                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                # If new cost is lower, update costs dict
                if new_cost < costs.get(neighbor, float('inf')):
                    costs[neighbor] = new_cost
                # Assign current node as predecessor
                came_from[neighbor] = node
                # Calculate new fscore
                new_fscore = new_dist + heuristic(neighbor, goal)
                # Enqueue
                entry = (new_fscore, new_dist, new_cost, neighbor)
                heapq.heappush(pq, entry)

    # Path not found
    return None


def reconstruct_path(came_from, start, goal):
    """
    Reconstruct the path from the dictionary of predecessors by backtracking.

    Return the list of nodes (start and goal inclusive) along the path.
    """
    # Start from goal node
    current = goal
    path = [current]

    # Backtrack until start node
    while current != start:
        current = came_from[current]
        path.append(current)

    # Return reversed path
    return path[::-1]


if __name__ == '__main__':
    # Initialize
    init()

    # Task 1
    path, distance, cost = ucs_noconstraint(START, END) or NO_PATH
    print('\n[TASK 1]')
    print('Shortest path: {}.'.format('->'.join(path)))
    print('Shortest distance: {}.'.format(str(distance)))
    print('Total energy cost: {}.'.format(str(cost)))
    print()

    # Task 2
    path, distance, cost = ucs(START, END) or NO_PATH
    print('\n[TASK 2]')
    print('Shortest path: {}.'.format('->'.join(path)))
    print('Shortest distance: {}.'.format(str(distance)))
    print('Total energy cost: {}.'.format(str(cost)))
    print()

    # Task 3
    path, distance, cost = astar(START, END) or NO_PATH
    print('\n[TASK 3]')
    print('Shortest path: {}.'.format('->'.join(path)))
    print('Shortest distance: {}.'.format(str(distance)))
    print('Total energy cost: {}.'.format(str(cost)))
    print()
    