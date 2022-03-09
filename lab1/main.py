import json
import math
import heapq

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


class Node:
    def __init__(self, id, parent, dist, cost):
        self.id = id
        self.parent = parent  # Store a Node object
        self.dist = dist
        self.cost = cost

    # Overriding the comparison operator 
    # to order nodes in priority queue based on cumulative distance
    def __lt__(self, next):
        return self.dist < next.dist


# [TASK 1]
# ====================================================================================================
def ucs_noconstraint(start, goal):
    """
    Uniform cost search with no energy constraint.

    Return the shortest path, distance travelled and energy consumed.
    """
    # Initialization
    startNode = Node(start, None, 0, 0)     # Node(id, parent, dist, cost)
    pq = [startNode]                        # Min-heap priority queue
    distances = {start: 0}                  # Dict of distance from start to node
    visited = set()                         # Set of visited nodes

    while pq:
        # Dequeue
        curNode = heapq.heappop(pq)

        if curNode.id in visited:
            continue

        # Return solution when goal is reached
        if curNode.id == goal:
            dist = curNode.dist
            cost = curNode.cost
            # Backtracking to reconstruct path
            path = [goal]
            while curNode.id != start:
                curNode = curNode.parent
                path.append(curNode.id)
            return path[::-1], dist, cost

        # Mark as visited
        visited.add(curNode.id)

        for neighbor in G[curNode.id]:
            # Calculate new distance based on current node
            new_dist = curNode.dist + Dist[','.join([curNode.id, neighbor])]
            # Return infinity as value if key not in dict (to avoid KeyError)
            # so new distance will always be lower for first time visited nodes
            if new_dist < distances.get(neighbor, float('inf')):
                # Update distances dict
                distances[neighbor] = new_dist
                # Calculate new cost based on current node
                new_cost = curNode.cost + Cost[','.join([curNode.id, neighbor])]
                # Create a Node object to push into priority queue
                neighborNode = Node(neighbor, curNode, new_dist, new_cost)
                # Enqueue
                entry = neighborNode
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
    startNode = Node(start, None, 0, 0)     # Node(id, parent, dist, cost)
    pq = [startNode]                        # Min-heap priority queue
    distances = {start: 0}                  # Dict of distance from start to node
    costs = {start: 0}                      # Dict of cost from start to node

    while pq:
        # Dequeue
        curNode = heapq.heappop(pq)

        # Return solution when goal is reached
        if curNode.id == goal:
            dist = curNode.dist
            cost = curNode.cost
            # Backtracking to reconstruct path
            path = [goal]
            while curNode.id != start:
                curNode = curNode.parent
                path.append(curNode.id)
            return path[::-1], dist, cost

        for neighbor in G[curNode.id]:
            # Calculate new distance and cost based on current node
            new_dist = curNode.dist + Dist[','.join([curNode.id, neighbor])]
            new_cost = curNode.cost + Cost[','.join([curNode.id, neighbor])]
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
                # Create a Node object to push into priority queue
                neighborNode = Node(neighbor, curNode, new_dist, new_cost)
                # Enqueue
                entry = neighborNode
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
    startNode = Node(start, None, 0, 0)     # Node(id, parent, dist, cost)
    pq = [(0, startNode)]                   # Min-heap priority queue (f_score, Node)
    distances = {start: 0}                  # Dict of distance from start to node
    costs = {start: 0}                      # Dict of cost from start to node

    while pq:
        # Dequeue
        fscore, curNode = heapq.heappop(pq)

        # Return solution when goal is reached
        if curNode.id == goal:
            dist = curNode.dist
            cost = curNode.cost
            # Backtracking to reconstruct path
            path = [goal]
            while curNode.id != start:
                curNode = curNode.parent
                path.append(curNode.id)
            return path[::-1], dist, cost

        for neighbor in G[curNode.id]:
            # Calculate new distance and cost based on current node
            new_dist = curNode.dist + Dist[','.join([curNode.id, neighbor])]
            new_cost = curNode.cost + Cost[','.join([curNode.id, neighbor])]
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
                # Calculate new fscore
                new_fscore = new_dist + heuristic(neighbor, goal)
                # Create a Node object to push into priority queue
                neighborNode = Node(neighbor, curNode, new_dist, new_cost)
                # Enqueue
                entry = (new_fscore, neighborNode)  # Nodes will be ordered based on fscore
                heapq.heappush(pq, entry)

    # Path not found
    return None


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
    