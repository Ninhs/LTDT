from collections import deque

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
    def bfs(self, start, end):

        if start == end:
            return [start]

        queue = deque([[start]])
        visited = set([start])

        while queue:
            path = queue.popleft()
            current = path[-1]

            # Duyệt các đỉnh kề từ current
            for (u, v), _ in self.edges.items():  # Nếu self.edges là dict {(u,v): w}
                if u == current and v not in visited:
                    new_path = path + [v]
                    if v == end:
                        return new_path  # Tìm thấy đường đi
                    visited.add(v)
                    queue.append(new_path)
                elif not self.directed and v == current and u not in visited:
                    new_path = path + [u]
                    if u == end:
                        return new_path
                    visited.add(u)
                    queue.append(new_path)

        return None  # Không có đường đi

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
        visited = set()
        stack = [start]
        dfs_order = []

        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            dfs_order.append(u)
            # duyệt các đỉnh kề
            neighbors = []
            for (x, y) in self.edges:
                if x == u:
                    neighbors.append(y)
                elif not self.directed and y == u:
                    neighbors.append(x)
            # thêm vào stack theo thứ tự đảo ngược để duyệt đúng thứ tự
            stack.extend(reversed(neighbors))
        return dfs_order

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