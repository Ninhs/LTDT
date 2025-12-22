from graph_model import Graph, Algorithm
from database import NebulaDB

class GraphController:
    def __init__(self, canvas, graph_type_var, text_result, text_matrix,
                 entry_src, entry_dst, entry_weight, btn_add_edge, algo_var, entry_start, end_vertex_cb,
                 btn_update, btn_move, btn_clear,
                 space_cb, btn_load_db):  # Thêm các Entry + Button
        self.canvas = canvas
        self.graph_type_var = graph_type_var
        self.text_result = text_result
        self.text_matrix = text_matrix

        self.entry_src = entry_src      # Entry đỉnh đầu
        self.entry_dst = entry_dst      # Entry đỉnh cuối
        self.entry_weight = entry_weight  # Entry trọng số
        self.btn_add_edge = btn_add_edge # Button thêm cạnh
        self.algo_var = algo_var        # Biến duyệt đồ thị
        self.entry_start = entry_start  # Entry
        self.end_vertex_cb = end_vertex_cb
        self.btn_update = btn_update
        self.btn_move = btn_move
        self.btn_clear = btn_clear


        self.move_mode = False
        self.selected_vertex = None  # Đỉnh đang được kéo

        # Bind sự kiện cho di chuyển đỉnh
        self.canvas.bind("<Button-1>", self.on_canvas_click)  # Đã có
        self.canvas.bind("<B1-Motion>", self.on_vertex_drag)  # Kéo chuột
        self.canvas.bind("<ButtonRelease-1>", self.on_vertex_release)  # Thả chuột

        self.space_cb = space_cb
        self.btn_load_db = btn_load_db


        # Load danh sách space khi khởi động
        self.refresh_space_list()

        self.graph = Graph(directed=(graph_type_var.get() == "co_huong"))
        self.vertex_count = 0

        self.add_vertex_mode = False
        self.add_edge_mode = False   # Thêm mode cho cạnh
        self.hint_shown = False

        # Bind
        self.btn_move.config(command=self.enable_move_mode)
        self.btn_load_db.config(command=self.load_from_db)
        self.btn_update.config(command=self.update_graph)
        self.btn_clear.config(command=self.clear_canvas)
        self.btn_add_edge.config(command=self.add_edge)

    def enable_add_vertex(self):
        self.add_vertex_mode = not self.add_vertex_mode
        self.add_edge_mode = False  # Tắt mode cạnh nếu đang bật

        if self.add_vertex_mode:
            self.text_result.insert("end", "Chế độ thêm đỉnh: click canvas để thêm đỉnh\n")
        else:
            self.text_result.insert("end", "Đã tắt chế độ thêm đỉnh\n")

    def add_vertex(self, event):
        vid = str(self.vertex_count + 1)
        x, y = event.x, event.y
        self.graph.add_vertex(vid, x, y)
        self.vertex_count += 1
        self.draw_vertex(vid)
        self.show_matrix()

        # LƯU TỌA ĐỘ VÀO NEBULA
        session = NebulaDB.get_session()
        try:
            session.execute(f'INSERT VERTEX IF NOT EXISTS vertex(x, y) VALUES "{vid}":({x}, {y});')
            self.text_result.insert("end", f"Đã thêm đỉnh {vid} tại ({x}, {y}) và lưu tọa độ vào DB\n")
        except Exception as e:
            self.text_result.insert("end", f"Lỗi lưu tọa độ đỉnh: {e}\n")

    def draw_vertex(self, vid):
        v = self.graph.vertices[vid]
        r = 20

        # Thêm tags=(vid,) cho cả oval và text
        self.canvas.create_oval(v.x - r, v.y - r, v.x + r, v.y + r,
                                fill="lightblue", outline="blue", width=2,
                                tags=(vid,))  # <--- Thêm tags

        self.canvas.create_text(v.x, v.y, text=vid, font=("Arial", 12, "bold"),
                                tags=(vid,))  # <--- Thêm tags

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

        # === LƯU VÀO NEBULAGRAPH (vô hướng: insert 2 chiều) Danh sách kề ===
        session = NebulaDB.get_session()
        try:
            # Insert cạnh cả hai chiều
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
        if self.move_mode:
            items = self.canvas.find_overlapping(event.x - 20, event.y - 20, event.x + 20, event.y + 20)
            for item in items:
                tags = self.canvas.gettags(item)
                if tags and tags[0].isdigit():
                    self.selected_vertex = tags[0]
                    return

    def update_graph(self):
        """Cập nhật đồ thị: xóa/sửa cạnh hoặc xóa đỉnh"""
        src = self.entry_src.get().strip()
        dst = self.entry_dst.get().strip()
        weight_str = self.entry_weight.get().strip()

        if not src:
            self.text_result.insert("end", "Vui lòng nhập ít nhất đỉnh đầu!\n")
            return

        # Trường hợp 1: Chỉ nhập src → xóa đỉnh src và tất cả cạnh liên quan
        if not dst and not weight_str:
            if src not in self.graph.vertices:
                self.text_result.insert("end", f"Đỉnh {src} không tồn tại!\n")
                return

            # Xóa tất cả cạnh liên quan đến src
            edges_to_delete = [k for k in list(self.graph.edges.keys()) if src in k]
            for k in edges_to_delete:
                del self.graph.edges[k]

            # Xóa đỉnh
            del self.graph.vertices[src]
            self.text_result.insert("end", f"Đã xóa đỉnh {src} và tất cả cạnh liên quan\n")

        # Trường hợp 2: Nhập src và dst → xóa hoặc sửa cạnh
        elif dst:
            key = tuple(sorted([src, dst]))
            if key not in self.graph.edges:
                self.text_result.insert("end", f"Không tìm thấy cạnh {src}-{dst}\n")
                return

            if weight_str:  # Có nhập trọng số → sửa trọng số
                try:
                    new_weight = float(weight_str)
                    self.graph.edges[key] = new_weight
                    self.text_result.insert("end", f"Đã sửa trọng số cạnh {src}-{dst} thành {new_weight}\n")
                except ValueError:
                    self.text_result.insert("end", "Trọng số mới phải là số!\n")
                    return
            else:  # Không nhập trọng số → xóa cạnh
                del self.graph.edges[key]
                self.text_result.insert("end", f"Đã xóa cạnh {src}-{dst}\n")

        # Vẽ lại toàn bộ
        self.redraw_all()
        self.show_matrix()
        self.entry_src.delete(0, "end")
        self.entry_dst.delete(0, "end")
        self.entry_weight.delete(0, "end")

    def enable_move_mode(self):
        """Bật/tắt chế độ di chuyển đỉnh"""
        self.move_mode = not self.move_mode
        if self.move_mode:
            self.text_result.insert("end", "Chế độ di chuyển: click và kéo đỉnh để di chuyển\n")
            self.canvas.config(cursor="hand2")
        else:
            self.text_result.insert("end", "Đã tắt chế độ di chuyển\n")
            self.canvas.config(cursor="")
            self.selected_vertex = None

    def on_canvas_click(self, event):
        if self.move_mode:
            # Tìm đỉnh gần nhất với click
            closest = self.canvas.find_closest(event.x, event.y)
            tags = self.canvas.gettags(closest)
            if tags and tags[0].isdigit():  # tag là VID
                self.selected_vertex = tags[0]
                self.text_result.insert("end", f"Đang di chuyển đỉnh {self.selected_vertex}\n")
            return
        if self.add_vertex_mode:
            self.add_vertex(event)

    def on_vertex_drag(self, event):
        if self.move_mode and self.selected_vertex:
            vid = self.selected_vertex
            v = self.graph.vertices[vid]
            v.x = event.x
            v.y = event.y
            self.redraw_all()  # Vẽ lại để cập nhật vị trí

            # Cập nhật tọa độ trong NebulaGraph (nếu có tag vertex)
            session = NebulaDB.get_session()
            try:
                session.execute(f'UPDATE VERTEX "{vid}" SET x = {event.x}, y = {event.y};')
            except:
                pass  # Bỏ qua nếu chưa có tag hoặc lỗi

    def on_vertex_release(self, event):
        if self.move_mode and self.selected_vertex:
            self.text_result.insert("end", f"Đã di chuyển đỉnh {self.selected_vertex} đến ({event.x}, {event.y})\n")
            self.selected_vertex = None

    def clear_canvas(self):
        """Làm mới: xóa hết đỉnh và cạnh trên canvas"""
        self.canvas.delete("all")
        self.graph = Graph()
        self.vertex_count = 0
        self.text_result.insert("end", "Đã làm mới canvas - xóa hết đỉnh và cạnh\n")
        self.show_matrix()

    def redraw_all(self):
        """Vẽ lại toàn bộ đồ thị (dùng khi xóa hoặc di chuyển)"""
        self.canvas.delete("all")
        for vid in self.graph.vertices:
            self.draw_vertex(vid)
        for (u, v), w in self.graph.edges.items():
            v1 = self.graph.vertices[u]
            v2 = self.graph.vertices[v]
            self.canvas.create_line(v1.x, v1.y, v2.x, v2.y, fill="black", width=3)
            mid_x = (v1.x + v2.x) / 2
            mid_y = (v1.y + v2.y) / 2
            offset_y = -12
            weight_str = str(w)
            temp_text = self.canvas.create_text(mid_x, mid_y + offset_y, text=weight_str, font=("Arial", 12, "bold"))
            bbox = self.canvas.bbox(temp_text)
            if bbox:
                padding = 5
                self.canvas.create_rectangle(bbox[0] - padding, bbox[1] - padding,
                                             bbox[2] + padding, bbox[3] + padding,
                                             fill="white", outline="gray", width=1)
            self.canvas.delete(temp_text)
            self.canvas.create_text(mid_x, mid_y + offset_y, text=weight_str,
                                    font=("Arial", 12, "bold"), fill="red", anchor="center")

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
        elif algo == "Dijkstra":
            self.run_dijkstra()
        elif algo == "Prim":
            self.run_prim()
        else:
            self.text_result.insert("end", f"Thuật toán {algo} chưa hỗ trợ\n")

    # chạy DFS
    def run_dfs(self):
        start = self.entry_start.get()
        if start not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh bắt đầu không hợp lệ\n")
            return

        algo = Algorithm()
        algo.edges = self.graph.edges
        algo.directed = self.graph.directed
        algo.vertices = self.graph.vertices.keys()

        predecessor, distances = algo.dfs(start)

        self.text_result.delete("1.0", "end")
        self.text_result.insert("end", f"DFS từ đỉnh {start}:\n")

        # Thứ tự duyệt (có thể lấy từ visited hoặc predecessor)
        order = []
        for v in predecessor:
            if predecessor[v] is not None or v == start:
                order.append(v)
        self.text_result.insert("end", "Thứ tự duyệt: " + " → ".join(order) + "\n\n")

        self.text_result.insert("end", "Khoảng cách (tổng trọng số đường đi DFS):\n")
        for v in sorted(distances.keys()):
            d = distances[v]
            dist_str = "∞" if d == float('inf') else str(d)
            self.text_result.insert("end", f"Đỉnh {v}: {dist_str}\n")
    # chạy BFS
    def run_bfs(self):
        start = self.entry_start.get()
        if start not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh bắt đầu không hợp lệ\n")
            return

        algo = Algorithm()
        algo.edges = self.graph.edges
        algo.directed = self.graph.directed
        algo.vertices = self.graph.vertices.keys()

        predecessor, distances = algo.bfs(start)

        self.text_result.delete("1.0", "end")
        self.text_result.insert("end", f"BFS từ đỉnh {start}:\n")
        self.text_result.insert("end", "Thứ tự duyệt: " + " → ".join(distances.keys()) + "\n\n")

        self.text_result.insert("end", "Khoảng cách (tổng trọng số đường đi):\n")
        for v, d in sorted(distances.items()):
            self.text_result.insert("end", f"Đỉnh {v}: {d} {'(không đến được)' if d == float('inf') else ''}\n")

    # duyệt bellman
    def run_bellman_ford(self):
        start = self.entry_start.get()
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

    # duyệt dijkstra
    def run_dijkstra(self):
        start = self.entry_start.get().strip()
        if not start:
            self.text_result.insert("end", "Vui lòng nhập đỉnh bắt đầu!\n")
            return
        if start not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh bắt đầu không hợp lệ\n")
            return

        algo = Algorithm()
        algo.edges = self.graph.edges
        algo.directed = self.graph.directed
        algo.vertices = self.graph.vertices.keys()

        # Gọi Dijkstra từ start đến tất cả các đỉnh
        distances = algo.dijkstra_all(start)  # <--- Sửa hàm dijkstra thành dijkstra_all

        self.text_result.delete("1.0", "end")
        self.text_result.insert("end", f"Đường đi ngắn nhất Dijkstra từ đỉnh {start} đến tất cả các đỉnh:\n\n")

        for v in sorted(distances.keys()):
            d = distances[v]
            if d == float('inf'):
                self.text_result.insert("end", f"Đỉnh {v}: Không đến được\n")
            else:
                self.text_result.insert("end", f"Đỉnh {v}: {d}\n")

    # duyệt prim
    def run_prim(self):
        start = self.entry_start.get().strip()
        if not start:
            self.text_result.insert("end", "Vui lòng nhập đỉnh bắt đầu!\n")
            return
        if start not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh bắt đầu không hợp lệ\n")
            return
        if self.graph.directed:
            self.text_result.insert("end", "Thuật toán Prim chỉ áp dụng cho đồ thị vô hướng!\n")
            return

        algo = Algorithm()
        algo.vertices = self.graph.vertices
        algo.edges = self.graph.edges

        # Gọi Prim, nhận danh sách cạnh MST và thứ tự thêm đỉnh (nếu Algorithm.prim trả thêm)
        mst_edges, total_weight, order = algo.prim(start)  # Giả sử prim trả thêm order

        self.text_result.delete("1.0", "end")
        self.text_result.insert("end", f"Thuật toán Prim từ đỉnh {start}:\n\n")

        if mst_edges is None:
            self.text_result.insert("end", "Đồ thị không liên thông – không tồn tại cây khung nhỏ nhất đầy đủ\n")
            return

        self.text_result.insert("end", "Quá trình duyệt và thêm cạnh vào MST:\n")
        for i, (u, v, w) in enumerate(mst_edges, 1):
            self.text_result.insert("end", f"Bước {i}: Thêm cạnh {u} — {v} (trọng số {w})\n")

        self.text_result.insert("end", f"\nCây khung nhỏ nhất (MST) gồm {len(mst_edges)} cạnh:\n")
        for u, v, w in mst_edges:
            self.text_result.insert("end", f"{u} — {v} : {w}\n")

        self.text_result.insert("end", f"\nTổng trọng số cây khung nhỏ nhất = {total_weight}\n")

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

    def refresh_space_list(self):
        session = NebulaDB.get_session()
        try:
            result = session.execute('SHOW SPACES;')
            if result.is_succeeded():
                spaces = [row.values()[0].as_string().strip('"') for row in result.rows()]
                self.space_cb['values'] = spaces
                if spaces:
                    self.space_var.set(spaces[0])
                self.text_result.insert("end", f"Tìm thấy {len(spaces)} đồ thị: {', '.join(spaces)}\n")
            else:
                self.text_result.insert("end", "Lỗi lấy danh sách space\n")
        except Exception as e:
            self.text_result.insert("end", f"Lỗi kết nối DB: {e}\n")

    def load_from_db(self):
        selected_space = self.space_var.get()  # <--- Dòng quan trọng: lấy space được chọn từ Combobox
        if not selected_space:
            self.text_result.insert("end", "Vui lòng chọn một đồ thị từ danh sách!\n")
            return

        self.text_result.insert("end", f"Đang load đồ thị '{selected_space}' từ NebulaGraph...\n")
        self.text_result.see("end")

        session = NebulaDB.get_session()
        try:
            # Chọn space
            session.execute(f'USE `{selected_space}`;')

            # Lấy tất cả cạnh
            result = session.execute('MATCH (v1)-[e:connect]->(v2) RETURN id(v1), id(v2), e.weight LIMIT 1000')

            if not result.row_size():
                self.text_result.insert("end", f"Đồ thị '{selected_space}' trống (không có cạnh)\n")
                return

            # Lấy tọa độ đỉnh (nếu có tag vertex với x, y)
            coordinates = {}
            coord_result = session.execute('MATCH (v:vertex) RETURN id(v), v.x, v.y')
            if coord_result.is_succeeded():
                for row in coord_result.rows():
                    vid = row.values()[0].as_string()
                    x = row.values()[1].as_double()
                    y = row.values()[2].as_double()
                    coordinates[vid] = (x, y)

            # Xóa canvas và model cũ
            self.canvas.delete("all")
            self.graph = Graph()
            self.vertex_count = 0

            vertices_set = set()
            edges_data = []

            for row in result.rows():
                src = row.values()[0].as_string()
                dst = row.values()[1].as_string()
                weight = row.values()[2].as_double()

                vertices_set.add(src)
                vertices_set.add(dst)
                edges_data.append((src, dst, weight))

            # Vị trí đỉnh: ưu tiên tọa độ lưu trong DB, nếu không có thì random
            import random
            w = self.canvas.winfo_width() or 800
            h = self.canvas.winfo_height() or 600

            for vid in vertices_set:
                if vid in coordinates:
                    x, y = coordinates[vid]
                else:
                    x = random.randint(50, w - 50)
                    y = random.randint(50, h - 50)
                self.graph.add_vertex(vid, x, y)
                self.vertex_count = max(self.vertex_count, int(vid) if vid.isdigit() else 0)
                self.draw_vertex(vid)

            # Vẽ cạnh và trọng số
            for src, dst, weight in edges_data:
                key = tuple(sorted([src, dst]))
                self.graph.edges[key] = weight

                v1 = self.graph.vertices[src]
                v2 = self.graph.vertices[dst]

                self.canvas.create_line(v1.x, v1.y, v2.x, v2.y, fill="black", width=3)

                mid_x = (v1.x + v2.x) / 2
                mid_y = (v1.y + v2.y) / 2
                offset_y = -12

                weight_str = str(weight)
                temp_text = self.canvas.create_text(mid_x, mid_y + offset_y, text=weight_str,
                                                    font=("Arial", 12, "bold"))
                bbox = self.canvas.bbox(temp_text)
                if bbox:
                    padding = 5
                    self.canvas.create_rectangle(
                        bbox[0] - padding, bbox[1] - padding,
                        bbox[2] + padding, bbox[3] + padding,
                        fill="white", outline="gray", width=1
                    )
                self.canvas.delete(temp_text)

                self.canvas.create_text(
                    mid_x, mid_y + offset_y,
                    text=weight_str,
                    font=("Arial", 12, "bold"),
                    fill="red",
                    anchor="center"
                )

            self.show_matrix()
            self.text_result.insert("end",
                                    f"Load thành công đồ thị '{selected_space}' với {len(vertices_set)} đỉnh và {len(edges_data)} cạnh!\n")
            self.text_result.see("end")

        except Exception as e:
            self.text_result.insert("end", f"Lỗi load từ NebulaGraph: {str(e)}\n")
            self.text_result.see("end")