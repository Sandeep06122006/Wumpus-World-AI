from collections import deque
import heapq

def manhattan_distance(pos1, pos2):
    """Calculates the Manhattan distance heuristic h(n) between two cells."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_neighbors(pos, grid_size):
    """Generates orthogonal adjacent grid neighbors."""
    x, y = pos
    neighbors = []
    for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            neighbors.append((nx, ny))
    return neighbors

def bfs(start, goal, safe_cells, grid_size=4):
    """
    Breadth-First Search (BFS) to find the shortest path from start to goal.
    Only traverses cells in safe_cells.
    Returns list of positions [start, ..., goal] or None if no safe path exists.
    """
    if start == goal:
        return [start]
        
    queue = deque([[start]])
    visited = {start}
    
    while queue:
        path = queue.popleft()
        current = path[-1]
        
        if current == goal:
            return path
            
        for neighbor in get_neighbors(current, grid_size):
            # Must be safe to step onto, or must be the goal
            if neighbor in safe_cells and neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
                
    return None

def a_star(start, goal, safe_cells, grid_size=4):
    """
    A* Search using Manhattan distance as the heuristic.
    Formula: f(n) = g(n) + h(n)
    - g(n): cost from start to current node (number of steps)
    - h(n): Manhattan distance from current node to goal
    Only traverses cells in safe_cells.
    Returns list of positions [start, ..., goal] or None if no safe path exists.
    """
    if start == goal:
        return [start]
        
    # Priority Queue stores: (f_score, g_score, current_cell, path)
    counter = 0 # tie-breaker for heap
    open_set = []
    initial_h = manhattan_distance(start, goal)
    heapq.heappush(open_set, (initial_h, 0, counter, start, [start]))
    
    g_scores = {start: 0}
    
    while open_set:
        f, g, _, current, path = heapq.heappop(open_set)
        
        if current == goal:
            return path
            
        for neighbor in get_neighbors(current, grid_size):
            if neighbor in safe_cells:
                tentative_g = g + 1
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    h = manhattan_distance(neighbor, goal)
                    f_score = tentative_g + h
                    counter += 1
                    heapq.heappush(open_set, (f_score, tentative_g, counter, neighbor, path + [neighbor]))
                    
    return None

