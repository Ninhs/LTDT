from graph_model import Graph, Algorithm
from database import NebulaDB

class GraphController:
    def __init__(self, canvas, graph_type_var, text_result, text_matrix,
                 entry_src, entry_dst, entry_weight, btn_add_edge, algo_var, start_vertex_cb, end_vertex_cb):  # Thêm các Entry + Button
        self.canvas = canvas
        self.graph_type_var = graph_type_var
        self.text_result = text_result
        self.text_matrix = text_matrix

        self.entry_src = entry_src      # Entry đỉnh đầu
        self.entry_dst = entry_dst      # Entry đỉnh cuối
        self.entry_weight = entry_weight  # Entry trọng số
        self.btn_add_edge = btn_add_edge
        self.algo_var = algo_var
        self.start_vertex_cb = start_vertex_cb
        self.end_vertex_cb = end_vertex_cb

        self.graph = Graph()
        self.vertex_count = 0

        self.add_vertex_mode = False
        self.add_edge_mode = False   # Thêm mode cho cạnh
        self.hint_shown = False

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Bind button thêm cạnh
        self.btn_add_edge.config(command=self.add_edge)

    def enable_add_vertex(self):
        self.add_vertex_mode = not self.add_vertex_mode
        self.add_edge_mode = False  # Tắt mode cạnh nếu đang bật

        if self.add_vertex_mode:
            self.text_result.insert("end", "Chế độ thêm đỉnh: click canvas để thêm đỉnh\n")
        else:
            self.text_result.insert("end", "Đã tắt chế độ thêm đỉnh\n")

    def add_vertex(self, event):
        """Hàm thực sự thêm một đỉnh mới khi click trên canvas"""
        vid = str(self.vertex_count + 1)  # Tự động đánh số: 1, 2, 3...
        self.graph.add_vertex(vid, event.x, event.y)
        self.vertex_count += 1
        self.draw_vertex(vid)
        self.show_matrix()

        # Thông báo
        self.text_result.insert("end", f"Đã thêm đỉnh {vid} tại vị trí ({event.x}, {event.y})\n")
        self.text_result.see("end")

    def draw_vertex(self, vid):
        """Vẽ đỉnh lên canvas"""
        v = self.graph.vertices[vid]  # v là object Vertex
        r = 20  # Bán kính đỉnh

        # SỬA TỪ v['x'], v['y'] THÀNH v.x, v.y
        self.canvas.create_oval(v.x - r, v.y - r, v.x + r, v.y + r,
                                fill="lightblue", outline="blue", width=2)
        self.canvas.create_text(v.x, v.y, text=vid, font=("Arial", 12, "bold"))

    def enable_add_edge(self):
        self.add_edge_mode = not self.add_edge_mode
        self.add_vertex_mode = False

        if self.add_edge_mode:
            self.text_result.delete("1.0", "end")
            self.text_result.insert("end", "Chế độ thêm cạnh: Nhập đỉnh đầu, đỉnh cuối, trọng số rồi nhấn 'Thêm cạnh'\n")
        else:
            self.text_result.insert("end", "Đã tắt chế độ thêm cạnh\n")

    def add_edge(self):
        src = self.entry_src.get().strip()
        dst = self.entry_dst.get().strip()

        if not src or not dst:
            self.text_result.insert("end", "Vui lòng nhập cả đỉnh đầu và đỉnh cuối!\n")
            return

        try:
            weight = float(self.entry_weight.get().strip())
        except ValueError:
            self.text_result.insert("end", "Trọng số phải là số!\n")
            return

        if src not in self.graph.vertices:
            self.text_result.insert("end", f"Đỉnh {src} không tồn tại!\n")
            return
        if dst not in self.graph.vertices:
            self.text_result.insert("end", f"Đỉnh {dst} không tồn tại!\n")
            return
        if src == dst:
            self.text_result.insert("end", "Không hỗ trợ cạnh khuyên (self-loop)!\n")
            return

        # Thêm cạnh vào model (vô hướng: lưu một lần với key sorted)
        key = tuple(sorted([src, dst]))
        if key in self.graph.edges:
            self.text_result.insert("end", f"Cạnh {src}-{dst} đã tồn tại!\n")
            return

        self.graph.edges[key] = weight

        # === VẼ CẠNH LÊN CANVAS ===
        v1 = self.graph.vertices[src]
        v2 = self.graph.vertices[dst]

        # Vẽ đường thẳng nối hai tâm đỉnh
        self.canvas.create_line(v1.x, v1.y, v2.x, v2.y,
                                fill="black", width=3)

        # === VẼ TRỌNG SỐ CHÍNH GIỮA CẠNH ===
        mid_x = (v1.x + v2.x) / 2
        mid_y = (v1.y + v2.y) / 2

        # Lệch nhẹ lên trên để tránh chồng lên đường thẳng
        offset_y = -12

        weight_str = str(weight)

        # Tạo nền trắng (hình chữ nhật bo tròn nhẹ)
        bbox = self.canvas.bbox(
            self.canvas.create_text(mid_x, mid_y + offset_y, text=weight_str, font=("Arial", 12, "bold")))
        if bbox:  # Nếu bbox hợp lệ
            padding = 5
            self.canvas.create_rectangle(
                bbox[0] - padding, bbox[1] - padding,
                bbox[2] + padding, bbox[3] + padding,
                fill="white", outline="gray", width=1
            )

        # Vẽ chữ đỏ lên trên nền trắng
        self.canvas.create_text(
            mid_x, mid_y + offset_y,
            text=weight_str,
            font=("Arial", 12, "bold"),
            fill="red",
            anchor="center"
        )

        # === LƯU VÀO NEBULAGRAPH (vô hướng: insert 2 chiều) ===
        session = NebulaDB.get_session()
        try:
            # Insert cạnh cả hai chiều (vì đồ thị vô hướng)
            session.execute(f'INSERT EDGE IF NOT EXISTS connect(weight) VALUES "{src}" -> "{dst}"@0:({weight});')
            session.execute(f'INSERT EDGE IF NOT EXISTS connect(weight) VALUES "{dst}" -> "{src}"@0:({weight});')

            self.text_result.insert("end", f"Đã thêm cạnh {src} — {dst} (trọng số {weight})\n")
            self.text_result.see("end")
        except Exception as e:
            self.text_result.insert("end", f"Lỗi lưu NebulaGraph: {str(e)}\n")

        # Cập nhật ma trận kề
        self.show_matrix()

        # Xóa ô nhập sau khi thêm thành công
        self.entry_src.delete(0, "end")
        self.entry_dst.delete(0, "end")
        self.entry_weight.delete(0, "end")

    # Sửa on_canvas_click để không thêm đỉnh khi đang ở mode cạnh
    def on_canvas_click(self, event):
        if self.add_vertex_mode:
            self.add_vertex(event)


    def show_matrix(self):
        pass

    # run thuật toán
    def run_algorithm(self):
        algo = self.algo_var.get()
        if algo == "Kruskal":
            self.run_kruskal()
        elif algo == "Sequential Color":
            self.run_sequential_color()
        elif algo == "BFS":
            self.run_bfs()
        elif algo == "DFS":
            self.run_dfs()
        elif algo == "Bellman-Ford":
            self.run_bellman_ford()
        else:
            self.text_result.insert("end", f"Thuật toán {algo} chưa hỗ trợ\n")

    # chạy BFS
    def run_bfs(self):
        start = self.start_vertex_cb.get()
        end = self.end_vertex_cb.get()

        if start not in self.graph.vertices or end not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh bắt đầu hoặc đỉnh đích không hợp lệ\n")
            return

        algo = Algorithm(directed=self.graph.directed)
        algo.vertices = self.graph.vertices
        algo.edges = self.graph.edges

        path = algo.bfs(start, end)

        if not path:
            self.text_result.insert("end", "Không tìm được đường đi bằng BFS\n")
            return

        total_weight = 0
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i + 1]

            if (u, v) in self.graph.edges:
                total_weight += self.graph.edges[(u, v)]
            elif not self.graph.directed and (v, u) in self.graph.edges:
                total_weight += self.graph.edges[(v, u)]
            else:
                self.text_result.insert("end", f"Không tìm thấy cạnh {u} -> {v}\n")
                return

        self.text_result.delete("1.0", "end")
        self.text_result.insert("end", "BFS path: " + " → ".join(path) + "\n")
        self.text_result.insert("end", f"Tổng trọng số: {total_weight}\n")

    # chạy Sequential Coloring
    def run_sequential_color(self):
        self.text_result.delete("1.0", "end")

        algo = Algorithm(directed=(self.graph_type_var.get() == "co_huong"))
        algo.vertices = self.graph.vertices
        algo.edges = self.graph.edges
        colors = algo.sequential_coloring()

        self.text_result.insert("end", " Sequential Coloring:\n")
        for v, c in colors.items():
            self.text_result.insert("end", f"Đỉnh {v} → Màu {c}\n")

    # chạy Kruskal
    def run_kruskal(self):
        self.text_result.delete("1.0", "end")

        algo = Algorithm(directed=(self.graph_type_var.get() == "co_huong"))
        algo.vertices = self.graph.vertices
        algo.edges = self.graph.edges
        try:
            mst, total_weight = algo.kruskal()
        except Exception as e:
            self.text_result.insert("end", f"Lỗi Kruskal: {e}\n")
            return

        self.text_result.insert("end", " Kruskal - Cây khung nhỏ nhất\n")
        for u, v, w in mst:
            self.text_result.insert("end", f"{u} - {v} : {w}\n")
        self.text_result.insert("end", f"\nTổng trọng số = {total_weight}\n")

    # chạy DFS
    def run_dfs(self):
        start = self.start_vertex_cb.get()
        end = self.end_vertex_cb.get()

        if start not in self.graph.vertices or end not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh không hợp lệ\n")
            return

        stack = [start]
        visited = set()
        parent = {start: None}

        while stack:
            u = stack.pop()
            if u == end:
                break

            if u in visited:
                continue
            visited.add(u)

            for (x, y), w in self.graph.edges.items():
                if x == u:
                    v = y
                elif not self.graph.directed and y == u:
                    v = x
                else:
                    continue

                if v not in visited:
                    parent[v] = u
                    stack.append(v)

        if end not in parent:
            self.text_result.insert("end", "Không tìm được đường đi\n")
            return

        # truy vết đường đi
        path = []
        cur = end
        while cur:
            path.append(cur)
            cur = parent[cur]
        path.reverse()

        # tính trọng số
        total_weight = 0
        for i in range(len(path) - 1):
            key = tuple(sorted([path[i], path[i + 1]]))
            total_weight += self.graph.edges[key]

        self.text_result.delete("1.0", "end")
        self.text_result.insert(
            "end",
            f"DFS path: {' → '.join(path)}\nTổng trọng số: {total_weight}\n"
        )

    # duyệt bellman
    def run_bellman_ford(self):
        start = self.start_vertex_cb.get()
        if start not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh bắt đầu không hợp lệ\n")
            return

        # Tạo danh sách cạnh dạng (u, v, w), hỗ trợ vô hướng
        edges_list = []
        for (u, v), w in self.graph.edges.items():
            edges_list.append((u, v, w))
            if not self.graph.directed:  # Nếu vô hướng
                edges_list.append((v, u, w))

        vertices_list = list(self.graph.vertices.keys())

        # Tạo instance Algorithm và gán edges
        algorithm = Algorithm()
        algorithm.edges = edges_list  # Gán danh sách cạnh vào instance

        distances = algorithm.bellman_ford(vertices_list, start)

        self.text_result.delete("1.0", "end")
        if distances is None:
            self.text_result.insert("end", "Đồ thị chứa chu trình âm!\n")
        else:
            self.text_result.insert("end", f"Bellman-Ford từ đỉnh {start}:\n")
            for v, d in distances.items():
                dist_str = "∞" if d == float('inf') else str(d)
                self.text_result.insert("end", f"Đỉnh {v}: {dist_str}\n")