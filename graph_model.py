from collections import deque
import heapq

class Vertex: # Lớp đỉnh
    def __init__(self, vid, x, y):
        self.id = vid # Mã đỉnh(A, B, 1, 2)
        self.x = x
        self.y = y


class Edge: # Lớp cạnh
    def __init__(self, u, v, weight=1, directed=False):
        self.u = u
        self.v = v
        self.weight = weight
        self.directed = directed

class Graph: # Lớp lưu tạm thời đồ thị
    def __init__(self, directed=False):
        self.directed = directed
        self.vertices = {}
        self.edges = {}

    # Thêm đỉnh
    def add_vertex(self, vid, x, y):
        self.vertices[vid] = Vertex(vid, x, y)

    # Thêm cạnh
    def add_edge(self, src, dst, weight=1):
        key = tuple(sorted([src, dst]))
        self.edges[key] = weight

    # Ma trận kề
    def adjacency_matrix(self):
        keys = list(self.vertices.keys())
        index = {k: i for i, k in enumerate(keys)}
        n = len(keys)

        matrix = [[0]*n for _ in range(n)]
        for e in self.edges:
            i, j = index[e.u], index[e.v]
            matrix[i][j] = e.weight
            if not self.directed:
                matrix[j][i] = e.weight

        return keys, matrix


class Algorithm:
    def __init__(self, directed=False):
        self.directed = directed
        self.vertices = {}
        self.edges = {}

    # hàm đọc ma trận kề
    def load_from_adj_list(self, adj_list):
        self.vertices.clear()
        self.edges.clear()
        for u in adj_list:
            self.vertices[u] = True
        for u in adj_list:
            for v, w in adj_list[u]:
                key = tuple(sorted([u, v]))
                self.edges[key] = w

    # thuật toán bfs
    def bfs(self, start):
        """
        Duyệt BFS từ start, trả về:
        - predecessor: dict {đỉnh: cha của nó trong cây BFS}
        - distances: dict {đỉnh: tổng trọng số từ start đến đỉnh đó}
        """
        if start not in self.vertices:
            return {}, {}

        predecessor = {start: None}
        distances = {start: 0}
        queue = deque([start])
        visited = set([start])

        while queue:
            current = queue.popleft()

            # Duyệt các đỉnh kề
            for (u, v), w in self.edges.items():
                neighbor = None
                weight = w
                if u == current:
                    neighbor = v
                elif not self.directed and v == current:
                    neighbor = u

                if neighbor and neighbor not in visited:
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
        vertices_list = list(self.vertices.keys())

        for v in vertices_list:
            neighbor_colors = set()

            for (u, w) in self.edges:
                if u == v and w in colors:
                    neighbor_colors.add(colors[w])
                elif not self.directed and w == v and u in colors:
                    neighbor_colors.add(colors[u])

            color = 1
            while color in neighbor_colors:
                color += 1
            colors[v] = color

        return colors

    # duyệt dfs
    def dfs(self, start):
        """
        Duyệt DFS từ start, trả về:
        - predecessor: dict {đỉnh: cha của nó trong cây DFS}
        - distances: dict {đỉnh: tổng trọng số từ start đến đỉnh đó theo đường DFS}
        """
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

            neighbors = []
            for (x, y), w in self.edges.items():
                if x == u and y not in visited:
                    neighbors.append((y, w))
                elif not self.directed and y == u and x not in visited:
                    neighbors.append((x, w))

            # Thêm neighbor vào stack (reversed để ưu tiên thứ tự)
            for neighbor, weight in reversed(neighbors):
                stack.append(neighbor)
                predecessor[neighbor] = u
                distances[neighbor] = distances[u] + weight

        return predecessor, distances

    # duyệt bellman
    def bellman_ford(self, vertices, start):
        distance = {v: float("inf") for v in vertices}
        distance[start] = 0

        for _ in range(len(vertices) - 1):
            for u, v, w in self.edges:
                if distance[u] != float("inf") and distance[u] + w < distance[v]:
                    distance[v] = distance[u] + w

        for u, v, w in self.edges:
            if distance[u] != float("inf") and distance[u] + w < distance[v]:
                return None  # có chu trình âm

        return distance

    #thuật toán dijkistra
    def dijkstra_all(self, start):
        """
        Dijkstra từ start đến tất cả các đỉnh khác.
        Trả về dict {đỉnh: khoảng cách ngắn nhất}
        """
        if start not in self.vertices:
            return {}

        import heapq

        dist = {v: float('inf') for v in self.vertices}
        dist[start] = 0

        pq = [(0, start)]  # (khoảng cách, đỉnh)

        while pq:
            current_dist, u = heapq.heappop(pq)

            if current_dist > dist[u]:
                continue

            for (x, y), w in self.edges.items():
                if x == u:
                    v = y
                elif not self.directed and y == u:
                    v = x
                else:
                    continue

                alt = dist[u] + w
                if alt < dist[v]:
                    dist[v] = alt
                    heapq.heappush(pq, (alt, v))

        return dist

    #thuật toán prim
    def prim(self, start):
        if start not in self.vertices:
            return None, 0, []

        import heapq

        mst_edges = []
        total_weight = 0
        order = [start]  # Thứ tự thêm đỉnh
        visited = set([start])
        edges = []

        # Thêm tất cả cạnh từ start vào heap
        for (u, v), w in self.edges.items():
            if u == start:
                heapq.heappush(edges, (w, u, v))
            elif v == start:
                heapq.heappush(edges, (w, v, u))

        while edges and len(visited) < len(self.vertices):
            w, u, v = heapq.heappop(edges)
            if v in visited:
                continue
            if u not in visited:
                u, v = v, u  # Đảo để u đã visit, v mới

            visited.add(v)
            order.append(v)
            mst_edges.append((u, v, w))
            total_weight += w

            # Thêm các cạnh mới từ v
            for (x, y), ww in self.edges.items():
                if x == v and y not in visited:
                    heapq.heappush(edges, (ww, x, y))
                elif y == v and x not in visited:
                    heapq.heappush(edges, (ww, y, x))

        if len(visited) < len(self.vertices):
            return None, 0, order  # Không liên thông

        return mst_edges, total_weight, order