# Pathfinding module implementing A* algorithm for enemy movement
import heapq

# A* pathfinding algorithm to find the shortest path between two points
def astar_pathfinding(start, goal, grid):
    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {}
    cost_so_far = {start: 0}

    # Process nodes by estimated total cost until goal is reached
    while open_list:
        _, current = heapq.heappop(open_list)

        if current == goal:
            break

        # Check each neighbor and update path if a better route is found
        for neighbor in get_neighbors(current, grid):
            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal, neighbor)
                heapq.heappush(open_list, (priority, neighbor))
                came_from[neighbor] = current

    return reconstruct_path(came_from, start, goal)

# Calculate Manhattan distance heuristic between two points
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) # Find valid neighboring cells that are walkable (value 0 in grid)

def get_neighbors(pos, grid):
    neighbors = []
    x, y = pos

    # Check all four adjacent directions (up, right, down, left)
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] == 0:
            neighbors.append((nx, ny))
    return neighbors

# Reconstruct the final path from the goal back to the start
def reconstruct_path(came_from, start, goal):
    current = goal
    path = []

    # Trace back from goal to start using the came_from dictionary
    while current != start:
        path.append(current)
        current = came_from.get(current)
        if current is None:
            return []
    path.reverse()
    # Reverse the path to get it in start-to-goal order
    return path