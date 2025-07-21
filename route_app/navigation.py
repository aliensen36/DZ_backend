import heapq
from collections import defaultdict


def find_shortest_path(start_location, end_location):
    # Строим граф: {location_id: [(neighbor_id, cost), ...]}
    graph = defaultdict(list)

    from route_app.models import Connection

    connections = Connection.objects.all()
    for conn in connections:
        graph[conn.from_location_id].append((conn.to_location_id, conn.cost))
        if conn.bidirectional:
            graph[conn.to_location_id].append((conn.from_location_id, conn.cost))

    # Алгоритм Дейкстры
    queue = [(0, start_location.id, [])]  # (общая стоимость, текущая локация, путь)
    visited = set()

    while queue:
        cost, current_id, path = heapq.heappop(queue)
        if current_id in visited:
            continue
        visited.add(current_id)
        path = path + [current_id]

        if current_id == end_location.id:
            return path  # список id локаций

        for neighbor_id, edge_cost in graph[current_id]:
            if neighbor_id not in visited:
                heapq.heappush(queue, (cost + edge_cost, neighbor_id, path))

    return None  # пути нет
