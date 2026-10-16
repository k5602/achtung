# cspell:disable
import heapq


def dijkstra(graph, start, end):
    queue = [(0, start)]
    distances = {start: 0}
    came_from = {}
    expanded = 0

    while queue:
        current_distance, current_node = heapq.heappop(queue)
        expanded += 1

        if current_node == end:
            break

        if current_distance > distances.get(current_node, float("inf")):
            continue

        for neighbor, weight in graph.get(current_node, {}).items():
            distance = current_distance + weight
            if distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = distance
                came_from[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    if end not in came_from and end != start:
        return [], float("inf"), expanded

    path = []
    curr = end
    while curr in came_from:
        path.append(curr)
        curr = came_from[curr]
    path.append(start)
    path.reverse()

    return path, distances.get(end, float("inf")), expanded


def astar(graph, start, end, coords=None):
    import math

    def haversine(u, v):
        if not coords or u not in coords or v not in coords:
            return 0
        lat1, lon1 = coords[u]
        lat2, lon2 = coords[v]
        r = 6371.0
        dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    queue = [(0, start)]
    distances = {start: 0}
    came_from = {}
    expanded = 0

    while queue:
        _, current_node = heapq.heappop(queue)
        expanded += 1

        if current_node == end:
            break

        for neighbor, weight in graph.get(current_node, {}).items():
            distance = distances[current_node] + weight
            if distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = distance
                came_from[neighbor] = current_node
                priority = distance + haversine(neighbor, end)
                heapq.heappush(queue, (priority, neighbor))

    if end not in came_from and end != start:
        return [], float("inf"), expanded

    path = []
    curr = end
    while curr in came_from:
        path.append(curr)
        curr = came_from[curr]
    path.append(start)
    path.reverse()

    return path, distances.get(end, float("inf")), expanded  