import json
from queue import PriorityQueue
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
#     '2': ['1', '3', '4', '5'], 
#     '3': ['1', '2', '4', '5'], 
#     '4': ['2', '3', '5', '6'], 
#     '5': ['2', '3', '4', '6'], 
#     '6': ['4', '5']
# }

# Dist = {
#     '1,2': 1, 
#     '2,1': 1, 
#     '1,3': 10, 
#     '3,1': 10, 
#     '2,3': 1, 
#     '3,2': 1, 
#     '2,4': 1, 
#     '4,2': 1, 
#     '2,5': 2, 
#     '5,2': 2, 
#     '3,4': 5, 
#     '4,3': 5, 
#     '3,5': 12, 
#     '5,3': 12, 
#     '4,5': 10, 
#     '5,4': 10, 
#     '4,6': 1, 
#     '6,4': 1, 
#     '5,6': 2, 
#     '6,5': 2
# }

# Cost = {
#     '1,2': 10, 
#     '2,1': 10, 
#     '1,3': 3, 
#     '3,1': 3, 
#     '2,3': 2, 
#     '3,2': 2, 
#     '2,4': 1, 
#     '4,2': 1, 
#     '2,5': 3, 
#     '5,2': 3, 
#     '3,4': 7, 
#     '4,3': 7, 
#     '3,5': 3, 
#     '5,3': 3, 
#     '4,5': 1, 
#     '5,4': 1, 
#     '4,6': 7, 
#     '6,4': 7, 
#     '5,6': 2, 
#     '6,5': 2
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
    # Using Python's built-in implementation of priority queue
    # Queue entries are ordered in terms of priority (lowest first)
    pq = PriorityQueue()

    # Initialization
    pq.put((0, start))                  # Add start node to priority queue with priority 0
    explored = {}                       # Dict of explored nodes {node: parent node}
    explored[start] = None              # Start node has no parent node
    cumulative_distance = {}            # Dict of distance from start to node
    cumulative_distance[start] = 0      # Start to start distance should be 0
    cumulative_cost = {}                # Dict of cost from start to node
    cumulative_cost[start] = 0          # Start to start cost should be 0

    while not pq.empty():
        # Dequeue
        current_node = pq.get()[1]

        # Return solution when goal is reached
        if current_node == goal:
            path = reconstruct_path(explored, start, goal)
            return path, cumulative_distance[current_node], cumulative_cost[current_node]

        for neighbor in G[current_node]:
            # Calculate new cumulative distance based on current node
            new_distance = cumulative_distance[current_node] + Dist[','.join([current_node, neighbor])]
            if neighbor not in explored or new_distance < cumulative_distance[neighbor]:
                # Calculate new cumulative cost based on current node
                new_cost = cumulative_cost[current_node] + Cost[','.join([current_node, neighbor])]
                # Enqueue new node
                pq.put((new_distance, neighbor))
                # Mark as explored and assign current node as parent
                explored[neighbor] = current_node
                # Update cumulative distance
                cumulative_distance[neighbor] = new_distance
                # Update cumulative cost
                cumulative_cost[neighbor] = new_cost

    # Path not found
    return None


# [TASK 2]
# ====================================================================================================
# def ucs(start, goal):
#     """
#     Uniform cost search with energy constraint.

#     Return the shortest path, distance travelled and energy consumed.
#     """
#     # Using Python's built-in implementation of priority queue
#     # Queue entries are ordered in terms of priority (lowest first) 
#     pq = PriorityQueue()

#     # Initialization
#     pq.put((0, start))               # Add start node to priority queue with priority 0
#     explored = {}                       # Dict of explored nodes {node: parent node}
#     explored[start] = None              # Start node has no parent node
#     cumulative_distance = {}            # Dict of distance from start to node
#     cumulative_distance[start] = 0      # Start to start distance should be 0
#     cumulative_cost = {}                # Dict of cost from start to node
#     cumulative_cost[start] = 0          # Start to start cost should be 0

#     while not pq.empty():
#         # Dequeue
#         current_node = pq.get()[1]

#         # Return solution when goal is reached
#         if current_node == goal:
#             path = reconstruct_path(explored, start, goal)
#             return path, cumulative_distance[current_node], cumulative_cost[current_node]

#         for neighbor in G[current_node]:
#             # Calculate new cumulative distance based on current node
#             new_distance = cumulative_distance[current_node] + Dist[','.join([current_node, neighbor])]
#             if neighbor not in explored or new_distance < cumulative_distance[neighbor]:
#                 # Calculate new cumulative cost based on current node
#                 new_cost = cumulative_cost[current_node] + Cost[','.join([current_node, neighbor])]
#                 if new_cost <= BUDGET:
#                     # Enqueue new node
#                     pq.put((new_distance, neighbor))
#                     # Mark as explored and assign current node as parent
#                     explored[neighbor] = current_node
#                     # Update cumulative distance
#                     cumulative_distance[neighbor] = new_distance
#                     # Update cumulative cost
#                     cumulative_cost[neighbor] = new_cost
    
#     # Path not found
#     return None

def ucs(start, goal):
    """
    Uniform cost search with energy constraint.

    Return the shortest path, distance travelled and energy consumed.
    """
    # Using Python's built-in implementation of priority queue
    # Queue entries are ordered in terms of priority (lowest first) 
    # pq = PriorityQueue()
    pq = [(0, 0, start)]

    # pq.put((0, 0, start))
    came_from = {}
    came_from[start] = None
    cumulative_distance = {}
    cumulative_distance[start] = 0
    cumulative_cost = {}
    cumulative_cost[start] = 0

    while pq:
        cur_dist, cur_cost, cur_node = heapq.heappop(pq)

        if cur_node == goal:
            path = reconstruct_path(came_from, start, goal)
            return path, cur_dist, cur_cost

        for next_node in G[cur_node]:
            next_dist = cur_dist + Dist[','.join([cur_node, next_node])]
            next_cost = cur_cost + Cost[','.join([cur_node, next_node])]
            if (next_node not in came_from or next_cost < cumulative_cost[next_node]) and next_cost <= BUDGET:
                entry = (next_dist, next_cost, next_node)
                heapq.heappush(pq, entry)
                cumulative_cost[next_node] = next_cost
                came_from[next_node] = cur_node


# [TASK 3]
# ====================================================================================================
def heuristic(node1, node2):
    """
    Heuristic function for A* search.
    
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
    # Using Python's built-in implementation of priority queue
    # Queue entries are ordered in terms of priority (lowest first) 
    # pq = PriorityQueue()
    pq = [(0, 0, start)]

    # pq.put((0, 0, start))
    came_from = {}
    came_from[start] = None
    cumulative_distance = {}
    cumulative_distance[start] = 0
    cumulative_cost = {}
    cumulative_cost[start] = 0

    while pq:
        cur_dist, cur_cost, cur_node = heapq.heappop(pq)

        if cur_node == goal:
            path = reconstruct_path(came_from, start, goal)
            return path, cur_dist, cur_cost

        for next_node in G[cur_node]:
            next_dist = cur_dist + Dist[','.join([cur_node, next_node])]
            next_cost = cur_cost + Cost[','.join([cur_node, next_node])]
            if (next_node not in came_from or next_cost < cumulative_cost[next_node]) and next_cost <= BUDGET:
                entry = (next_dist + heuristic(next_node, goal), next_cost, next_node)
                heapq.heappush(pq, entry)
                cumulative_distance[next_node] = next_dist
                cumulative_cost[next_node] = next_cost
                came_from[next_node] = cur_node


# def astar(start, goal):
#     """
#     A* search with energy constraint.

#     Return the shortest path, distance travelled and energy consumed.
#     """
#     # Using Python's built-in implementation of priority queue
#     # Queue entries are ordered in terms of priority (lowest first)
#     pq = PriorityQueue()

#     # Initialization
#     pq.put((0, start))                  # Add start node to priority queue with priority 0
#     explored = {}                       # Dict of explored nodes {node: parent node}
#     explored[start] = None              # Start node has no parent node
#     cumulative_distance = {}            # Dict of distance from start to node
#     cumulative_distance[start] = 0      # Start to start distance should be 0
#     cumulative_cost = {}                # Dict of cost from start to node
#     cumulative_cost[start] = 0          # Start to start cost should be 0

#     while not pq.empty():
#         # Dequeue
#         current_node = pq.get()[1]

#         # Return solution when goal is reached
#         if current_node == goal:
#             path = reconstruct_path(explored, start, goal)
#             return path, cumulative_distance[current_node], cumulative_cost[current_node]

#         for neighbor in G[current_node]:
#             # Calculate new cumulative distance based on current node
#             new_distance = cumulative_distance[current_node] + Dist[','.join([current_node, neighbor])]
#             if neighbor not in explored or new_distance < cumulative_distance[neighbor]:
#                 # Calculate new cumulative cost based on current node
#                 new_cost = cumulative_cost[current_node] + Cost[','.join([current_node, neighbor])]
#                 if new_cost <= BUDGET:
#                     # Set priority as new distance + distance from goal
#                     priority = new_distance + heuristic(neighbor, goal)
#                     # Enqueue new node
#                     pq.put((priority, neighbor))
#                     # Mark as explored and assign current node as parent
#                     explored[neighbor] = current_node
#                     # Update cumulative distance
#                     cumulative_distance[neighbor] = new_distance
#                     # Update cumulative cost
#                     cumulative_cost[neighbor] = new_cost
    
#     # Path not found
#     return None


def reconstruct_path(explored, start, goal):
    """
    Reconstruct the path from the dictionary of explored nodes by backtracking.

    Return the list of nodes (start and goal inclusive) along the path.
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
    