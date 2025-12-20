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
