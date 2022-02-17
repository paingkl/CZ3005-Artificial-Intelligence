import json
from queue import PriorityQueue
import math

# Example instance
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


# NYC instance
# ====================================================================================================
# Constants
START = '1'
END = '50'
BUDGET = 287932

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
    queue = PriorityQueue()

    # Initialization
    queue.put((0, start))               # Add start node to queue with priority 0
    explored = {}                       # Dict of explored nodes {node: parent node}
    explored[start] = None              # Start node has no parent node
    cumulative_distance = {}            # Dict of distance from start to node
    cumulative_distance[start] = 0      # Start to start distance should be 0
    cumulative_cost = {}                # Dict of cost from start to node
    cumulative_cost[start] = 0          # Start to start cost should be 0

    while not queue.empty():
        # Dequeue
        current_node = queue.get()[1]

        # Stop when goal is reached
        if current_node == goal:
            path = reconstruct_path(explored, start, goal)
            return path, cumulative_distance[current_node], cumulative_cost[current_node]

        # Explore every single neighbor of current node
        for neighbor in G[current_node]:
            # Calculate new cumulative distance based on current node
            new_distance = cumulative_distance[current_node] + Dist[','.join([current_node, neighbor])]
            if neighbor not in explored or new_distance < cumulative_distance[neighbor]:
                # Calculate new cumulative cost based on current node
                new_cost = cumulative_cost[current_node] + Cost[','.join([current_node, neighbor])]
                # Enqueue new node
                queue.put((new_distance, neighbor))
                # Mark as explored and assign current node as parent
                explored[neighbor] = current_node
                # Update cumulative distance
                cumulative_distance[neighbor] = new_distance
                # Update cumulative cost
                cumulative_cost[neighbor] = new_cost


# [TASK 2]
# ====================================================================================================
def ucs(start, goal):
    """
    Uniform cost search with energy constraint.

    Return the shortest path, distance travelled and energy consumed.
    """
    queue = PriorityQueue()

    # Initialization
    queue.put((0, start))               # Add start node to queue with priority 0
    explored = {}                       # Dict of explored nodes {node: parent node}
    explored[start] = None              # Start node has no parent node
    cumulative_distance = {}            # Dict of distance from start to node
    cumulative_distance[start] = 0      # Start to start distance should be 0
    cumulative_cost = {}                # Dict of cost from start to node
    cumulative_cost[start] = 0          # Start to start cost should be 0

    while not queue.empty():
        # Dequeue
        current_node = queue.get()[1]

        # Stop when goal is reached
        if current_node == goal:
            path = reconstruct_path(explored, start, goal)
            return path, cumulative_distance[current_node], cumulative_cost[current_node]

        # Explore every single neighbor of current node
        for neighbor in G[current_node]:
            # Calculate new cumulative distance based on current node
            new_distance = cumulative_distance[current_node] + Dist[','.join([current_node, neighbor])]
            if neighbor not in explored or new_distance < cumulative_distance[neighbor]:
                # Calculate new cumulative cost based on current node
                new_cost = cumulative_cost[current_node] + Cost[','.join([current_node, neighbor])]
                if new_cost <= BUDGET:
                    # Enqueue new node
                    queue.put((new_distance, neighbor))
                    # Mark as explored and assign current node as parent
                    explored[neighbor] = current_node
                    # Update cumulative distance
                    cumulative_distance[neighbor] = new_distance
                    # Update cumulative cost
                    cumulative_cost[neighbor] = new_cost


# [TASK 3]
# ====================================================================================================
def heuristic(node1, node2):
    """
    Heuristic function to calculate the straight-line distance between two coordinates.
    """
    x1, y1 = Coord[node1]
    x2, y2 = Coord[node2]
    return math.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))


def astar(start, goal):
    """
    A* search with energy constraint.

    Return the shortest path, distance travelled and energy consumed.
    """
    queue = PriorityQueue()

    # Initialization
    queue.put((0, start))               # Add start node to queue with priority 0
    explored = {}                       # Dict of explored nodes {node: parent node}
    explored[start] = None              # Start node has no parent node
    cumulative_distance = {}            # Dict of distance from start to node
    cumulative_distance[start] = 0      # Start to start distance should be 0
    cumulative_cost = {}                # Dict of cost from start to node
    cumulative_cost[start] = 0          # Start to start cost should be 0

    while not queue.empty():
        # Dequeue
        current_node = queue.get()[1]

        # Stop when goal is reached
        if current_node == goal:
            path = reconstruct_path(explored, start, goal)
            return path, cumulative_distance[current_node], cumulative_cost[current_node]

        # Explore every single neighbor of current node
        for neighbor in G[current_node]:
            # Calculate new cumulative distance based on current node
            new_distance = cumulative_distance[current_node] + Dist[','.join([current_node, neighbor])]
            if neighbor not in explored or new_distance < cumulative_distance[neighbor]:
                # Calculate new cumulative cost based on current node
                new_cost = cumulative_cost[current_node] + Cost[','.join([current_node, neighbor])]
                if new_cost <= BUDGET:
                    # Set priority as new distance + distance from goal
                    priority = new_distance + heuristic(neighbor, goal)
                    # Enqueue new node
                    queue.put((priority, neighbor))
                    # Mark as explored and assign current node as parent
                    explored[neighbor] = current_node
                    # Update cumulative distance
                    cumulative_distance[neighbor] = new_distance
                    # Update cumulative cost
                    cumulative_cost[neighbor] = new_cost


def reconstruct_path(explored, start, goal):
    """
    Reconstruct the path from the dictionary of explored nodes.
    """
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
    # Initialize
    init()

    # Task 1
    path, distance, cost = ucs_noconstraint(START, END)
    print('\n[TASK 1]')
    print('Shortest path: {}.'.format('->'.join(path)))
    print('Shortest distance: {}.'.format(str(distance)))
    print('Total energy cost: {}.'.format(str(cost)))
    print()

    # Task 2
    path, distance, cost = ucs(START, END)
    print('\n[TASK 2]')
    print('Shortest path: {}.'.format('->'.join(path)))
    print('Shortest distance: {}.'.format(str(distance)))
    print('Total energy cost: {}.'.format(str(cost)))
    print()

    # Task 3
    path, distance, cost = astar(START, END)
    print('\n[TASK 3]')
    print('Shortest path: {}.'.format('->'.join(path)))
    print('Shortest distance: {}.'.format(str(distance)))
    print('Total energy cost: {}.'.format(str(cost)))
    print()
