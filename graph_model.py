from collections import deque
import heapq


class Vertex:  # Lớp đỉnh
    def __init__(self, vid, x, y):
        self.id = vid  # Mã đỉnh(A, B, 1, 2)
        self.x = x
        self.y = y


class Edge:  # Lớp cạnh
    def __init__(self, u, v, weight=1, directed=False):
        self.u = u
        self.v = v
        self.weight = weight
        self.directed = directed


class Graph:  # Lớp lưu tạm thời đồ thị
    def __init__(self, directed=False):
        self.directed = directed
        self.vertices = {}
        self.edges = {}

    # Thêm đỉnh
    def add_vertex(self, vid, x, y):
        self.vertices[vid] = Vertex(vid, x, y)

    # Thêm cạnh
    def add_edge(self, src, dst, weight=1):
        if self.directed:
            self.edges[(src, dst)] = weight
        else:
            key = tuple(sorted([src, dst]))
            self.edges[key] = weight

    # Ma trận kề
    def adjacency_matrix(self):
        keys = list(self.vertices.keys())
        index = {k: i for i, k in enumerate(keys)}
        n = len(keys)

        matrix = [[0] * n for _ in range(n)]
        for (u, v), w in self.edges.items():
            i, j = index[u], index[v]
            matrix[i][j] = w
            if not self.directed:
                matrix[j][i] = w
        return keys, matrix


class Algorithm:
    def __init__(self, directed=False):
        self.directed = directed
        self.vertices = []
        self.edges = {}

    def get_neighbors(self, u):
        neighbors = []
        for (x, y), w in self.edges.items():
            if x == u:
                neighbors.append((y, w))
            elif not self.directed and y == u:
                neighbors.append((x, w))
        return neighbors

    # thuật toán bfs
    def bfs(self, start):
        if start not in self.vertices:
            return {}, {}

        predecessor = {start: None}
        distances = {start: 0}
        queue = deque([start])
        visited = set([start])

        while queue:
            current = queue.popleft()

            # Duyệt các đỉnh kề
            for neighbor, weight in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    predecessor[neighbor] = current
                    distances[neighbor] = distances[current] + weight
        return predecessor, distances

    # thuật toán kruskal
    def kruskal(self):
        if self.directed:
            raise ValueError("Kruskal không áp dụng cho đồ thị có hướng")

        parent = {}
        rank = {}
        for vid in self.vertices:
            parent[vid] = vid
            rank[vid] = 0

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x, y):
            rx = find(x)
            ry = find(y)
            if rx == ry:
                return False
            if rank[rx] < rank[ry]:
                parent[rx] = ry
            elif rank[rx] > rank[ry]:
                parent[ry] = rx
            else:
                parent[ry] = rx
                rank[rx] += 1
            return True

        sorted_edges = []
        for (u, v), w in self.edges.items():
            sorted_edges.append((w, u, v))
        sorted_edges.sort()

        mst = []
        total_weight = 0
        for w, u, v in sorted_edges:
            if union(u, v):
                mst.append((u, v, w))
                total_weight += w

        return mst, total_weight

    # thuật toán Sequential Coloring
    def sequential_coloring(self):
        colors = {}

        for v in self.vertices:
            neighbor_colors = set()
            for neighbor, _ in self.get_neighbors(v):
                if neighbor in colors:
                    neighbor_colors.add(colors[neighbor])
            color = 1
            while color in neighbor_colors:
                color += 1
            colors[v] = color
        return colors

    # duyệt dfs
    def dfs(self, start):
        if start not in self.vertices:
            return {}, {}
        visited = set()
        stack = [start]
        predecessor = {start: None}
        distances = {start: 0}

        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            # duyệt hàng xóm
            for neighbor, weight in reversed(list(self.get_neighbors(u))):
                if neighbor not in visited:
                    stack.append(neighbor)
                    if neighbor not in predecessor:
                        predecessor[neighbor] = u
                        distances[neighbor] = distances[u] + weight

        return predecessor, distances

    # duyệt bellman
    def bellman_ford(self, vertices, start):
        if not self.directed:
            raise ValueError("Bellman-Ford chỉ áp dụng cho đồ thị có hướng")
        distance = {v: float("inf") for v in vertices}
        distance[start] = 0
        for _ in range(len(vertices) - 1):
            for (u, v), w in self.edges.items():
                if distance[u] != float("inf") and distance[u] + w < distance[v]:
                    distance[v] = distance[u] + w
        for (u, v), w in self.edges.items():
            if distance[u] != float("inf") and distance[u] + w < distance[v]:
                return None
        return distance

    # thuật toán dijkistra
    def dijkstra(self, start):
        if start not in self.vertices:
            return {}
        dist = {v: float('inf') for v in self.vertices}
        dist[start] = 0
        pq = [(0, start)]  # (khoảng cách, đỉnh)

        while pq:
            current_dist, u = heapq.heappop(pq)

            if current_dist > dist[u]:
                continue

            for v, w in self.get_neighbors(u):
                alt = dist[u] + w
                if alt < dist[v]:
                    dist[v] = alt
                    heapq.heappush(pq, (alt, v))
        return dist

    # thuật toán prim
    def prim(self, start):
        if self.directed:
            raise ValueError("Prim không áp dụng cho đồ thị có hướng")
        if start not in self.vertices:
            return None, 0, []
        visited = set([start])
        mst_edges = []
        total_weight = 0
        order = [start]
        heap = []

        # đưa cạnh kề với start vào heap
        for neighbor, weight in self.get_neighbors(start):
            heapq.heappush(heap, (weight, start, neighbor))

        while heap and len(visited) < len(self.vertices):
            weight, u, v = heapq.heappop(heap)

            if v in visited:
                continue

            visited.add(v)
            mst_edges.append((u, v, weight))
            total_weight += weight
            order.append(v)

            # thêm cạnh mới từ v
            for neighbor, w in self.get_neighbors(v):
                if neighbor not in visited:
                    heapq.heappush(heap, (w, v, neighbor))
        if len(visited) < len(self.vertices):
            return None, 0, order
        return mst_edges, total_weight, order

    # hàm mới
    def dijkstra_and_bellman_ford_path(self, start, end):
        if start not in self.vertices or end not in self.vertices:
            return None, None
        # Kiểm tra xem có cạnh âm không
        has_negative = any(w < 0 for w in self.edges.values())
        if has_negative:
            # Dùng Bellman-Ford
            distance = {v: float("inf") for v in self.vertices}
            prev = {v: None for v in self.vertices}
            distance[start] = 0
            for _ in range(len(self.vertices) - 1):
                for (u, v), w in self.edges.items():
                    if distance[u] != float("inf") and distance[u] + w < distance[v]:
                        distance[v] = distance[u] + w
                        prev[v] = u
            # Kiểm tra chu trình âm
            for (u, v), w in self.edges.items():
                if distance[u] != float("inf") and distance[u] + w < distance[v]:
                    raise ValueError("Đồ thị có chu trình âm, không thể tìm đường đi ngắn nhất")
        else:
            # Dijkkstra
            dist = {v: float('inf') for v in self.vertices}
            prev = {v: None for v in self.vertices}
            dist[start] = 0
            pq = [(0, start)]

            while pq:
                current_dist, u = heapq.heappop(pq)
                if u == end:
                    break
                if current_dist > dist[u]:
                    continue
                for v, w in self.get_neighbors(u):
                    alt = dist[u] + w
                    if alt < dist[v]:
                        dist[v] = alt
                        prev[v] = u
                        heapq.heappush(pq, (alt, v))
            distance = dist
        if distance[end] == float("inf"):
            return None, None
        path = []
        cur = end
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        path.reverse()
        return path, distance[end]
