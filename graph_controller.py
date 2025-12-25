from graph_model import Graph, Algorithm
from database import NebulaDB
from nebula3.common.ttypes import Value
import tkinter as tk
import math
import random

class GraphController:
    def __init__(self, canvas, graph_type_var, text_result, text_matrix,
                 entry_src, entry_dst, entry_weight, btn_add_edge, algo_var, entry_start, start_vertex_cb,
                 end_vertex_cb, space_var,
                 btn_find_path, btn_update, btn_move, btn_clear,
                 space_cb, btn_load_db):
        self.canvas = canvas
        self.graph_type_var = graph_type_var
        self.text_result = text_result
        self.text_matrix = text_matrix

        self.entry_src = entry_src  # Entry đỉnh đầu
        self.entry_dst = entry_dst  # Entry đỉnh cuối
        self.entry_weight = entry_weight  # Entry trọng số
        self.btn_add_edge = btn_add_edge  # Button thêm cạnh
        self.algo_var = algo_var  # Biến duyệt đồ thị
        self.entry_start = entry_start  # Đỉnh bắt đầu để duyệt toàn bộ bằng thuật toán
        self.start_vertex_cb = start_vertex_cb  # entry bắt đầu tìm đường đi
        self.end_vertex_cb = end_vertex_cb  # entry đỉnh đích tìm đường đi
        self.btn_update = btn_update    # Update đồ thị khi click và điền thong tin vào entry đỉnh và trọng số
        self.btn_move = btn_move    # Di chuyển khi click vào nút và kéo thả các đỉnh
        self.btn_clear = btn_clear  # Xá toàn bộ đồ thị trên màng hình canvas
        self.btn_find_path = btn_find_path  # nút tìm đường đi khi nhập đỉnh đầu và đỉnh đích

        self.move_mode = False
        self.selected_vertex = None  # Đỉnh đang được kéo

        # Bind sự kiện cho di chuyển đỉnh
        self.canvas.bind("<Button-1>", self.on_canvas_click)  # Đã có
        self.canvas.bind("<B1-Motion>", self.on_vertex_drag)  # Kéo chuột
        self.canvas.bind("<ButtonRelease-1>", self.on_vertex_release)  # Thả chuột

        self.space_cb = space_cb
        self.space_var = space_var
        self.btn_load_db = btn_load_db

        # Load danh sách space khi khởi động
        self.refresh_space_list()
        self.graph_type_var.trace_add("write", self.on_graph_type_change)

        self.graph = Graph(directed=(graph_type_var.get() == "co_huong"))
        self.vertex_count = 0

        self.add_vertex_mode = False
        self.add_edge_mode = False  # Thêm mode cho cạnh
        self.hint_shown = False

        # Bind
        self.btn_move.config(command=self.enable_move_mode)
        self.btn_load_db.config(command=self.load_from_db)
        self.btn_update.config(command=self.update_graph)
        self.btn_clear.config(command=self.clear_canvas)
        self.btn_add_edge.config(command=self.add_edge)

    # Lưu dữ liệu
    def save_graph_config(self):
        selected_space = self.space_var.get()
        session = NebulaDB.get_session()
        try:
            is_directed = self.graph_type_var.get() == "co_huong"
            session.execute(f'USE `{selected_space}`;') # Hoặc space hiện tại
            session.execute('INSERT VERTEX IF NOT EXISTS graph_config(is_directed) VALUES "config":(true);')
            session.execute(f'UPDATE VERTEX "config" OF graph_config SET is_directed = {str(is_directed).lower()};')
            self.text_result.insert("end", f"Đã lưu config đồ thị {'có hướng' if is_directed else 'vô hướng'}\n")
        except Exception as e:
            self.text_result.insert("end", f"Lỗi lưu config: {e}\n")

    def enable_add_vertex(self):
        self.clear_result()
        self.add_vertex_mode = not self.add_vertex_mode
        self.add_edge_mode = False

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
        self.save_vertex_to_db(vid, x, y)

        # LƯU TỌA ĐỘ VÀO NEBULA
        session = NebulaDB.get_session()
        try:
            session.execute(f'INSERT VERTEX IF NOT EXISTS point(x, y) VALUES "{vid}":({x}, {y});')
            self.text_result.insert("end", f"Đã thêm đỉnh {vid} tại ({x}, {y}) và lưu tọa độ vào DB\n")
        except Exception as e:
            self.text_result.insert("end", f"Lỗi lưu tọa độ đỉnh: {e}\n")

    def draw_vertex(self, vid):
        v = self.graph.vertices[vid]
        r = 20

        self.canvas.create_oval(v.x - r, v.y - r, v.x + r, v.y + r,
                                fill="lightblue", outline="blue", width=2,
                                tags=(vid,))

        self.canvas.create_text(v.x, v.y, text=vid, font=("Arial", 12, "bold"),
                                tags=(vid,))

    def enable_add_edge(self):
        self.clear_result()
        self.add_edge_mode = not self.add_edge_mode
        self.add_vertex_mode = False

        if self.add_edge_mode:
            self.text_result.delete("1.0", "end")
            self.text_result.insert("end",
                                    "Chế độ thêm cạnh: Nhập đỉnh đầu, đỉnh cuối, trọng số rồi nhấn 'Thêm cạnh'\n")
        else:
            self.text_result.insert("end", "Đã tắt chế độ thêm cạnh\n")

    def on_graph_type_change(self, *args):
        is_directed = (self.graph_type_var.get() == "co_huong")
        self.graph.directed = is_directed
        self.text_result.insert(
            "end",
            f"Đã chuyển sang đồ thị {'có hướng' if is_directed else 'vô hướng'}\n"
        )
        self.redraw_all()
        self.show_matrix()

    def add_edge(self):
        self.clear_result()
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

        # Thêm cạnh vào model
        if self.graph.directed:
            self.graph.edges[(src, dst)] = weight
        else:
            key = tuple(sorted([src, dst]))
            self.graph.edges[key] = weight

        # === VẼ CẠNH LÊN CANVAS ===
        v1 = self.graph.vertices[src]
        v2 = self.graph.vertices[dst]

        # Vẽ đường thẳng có hướng và vô hw
        r = 20  # bán kính đỉnh
        dx = v2.x - v1.x
        dy = v2.y - v1.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            dist = 1
        offset_x = dx / dist * r
        offset_y = dy / dist * r
        if self.graph.directed:
            self.canvas.create_line(v1.x + offset_x, v1.y + offset_y,
                                    v2.x - offset_x, v2.y - offset_y,
                                    fill="black", width=3,
                                    arrow=tk.LAST, arrowshape=(16, 20, 6))
        else:
            self.canvas.create_line(v1.x, v1.y, v2.x, v2.y, fill="black", width=3)
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
            if self.graph.directed:
                session.execute(f'INSERT EDGE connect(weight) VALUES "{src}"->"{dst}":({weight});')
            else:
                session.execute(f'INSERT EDGE connect(weight) VALUES "{src}"->"{dst}":({weight});')
                session.execute(f'INSERT EDGE connect(weight) VALUES "{dst}"->"{src}":({weight});')

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

    def update_graph(self):
        selected_space = self.space_var.get()
        self.clear_result()
        src = self.entry_src.get().strip()
        dst = self.entry_dst.get().strip()
        weight_str = self.entry_weight.get().strip()

        if not src:
            self.text_result.insert("end", "Vui lòng nhập ít nhất đỉnh đầu!\n")
            return

        session = NebulaDB.get_session()
        try:
            session.execute(f'USE `{selected_space}`;')  # Giả sử dùng space mặc định
        except:
            pass  # Offline mode

        # XÓA ĐỈNH (và tất cả cạnh liên quan)
        if not dst and not weight_str:
            if src not in self.graph.vertices:
                self.text_result.insert("end", f"Đỉnh {src} không tồn tại!\n")
                return

            # Xóa cạnh trong model
            edges_to_delete = [k for k in list(self.graph.edges.keys()) if src in k]
            for k in edges_to_delete:
                del self.graph.edges[k]

            # XÓA ĐỒNG BỘ NEBULA
            try:
                session.execute(f'DELETE VERTEX "{src}";')
                self.text_result.insert("end", f"Xóa đỉnh {src} khỏi NebulaGraph\n")
            except:
                pass

            del self.graph.vertices[src]
            self.text_result.insert("end", f"Đã xóa đỉnh {src} và tất cả cạnh liên quan\n")

        # XÓA/SỬA CẠNH
        elif dst:
            if self.graph.directed:
                key = (src, dst)
            else:
                key = tuple(sorted([src, dst]))

            if key not in self.graph.edges:
                self.text_result.insert("end", f"Không tìm thấy cạnh {src}-{dst}\n")
                return

            if weight_str:  # SỬA TRỌNG SỐ
                try:
                    new_weight = float(weight_str)
                    self.graph.edges[key] = new_weight

                    # SỬA TRONG NEBULA (cả 2 chiều nếu vô hướng)
                    try:
                        session.execute(f'UPDATE EDGE connect "{src}" -> "{dst}" SET weight = {new_weight};')
                        if not self.graph.directed:
                            session.execute(f'UPDATE EDGE connect "{dst}" -> "{src}" SET weight = {new_weight};')
                        self.text_result.insert("end", f"Đã sửa trọng số {src}-{dst} → {new_weight} trong DB\n")
                    except:
                        pass
                    self.text_result.insert("end", f"Đã sửa trọng số cạnh {src}-{dst} thành {new_weight}\n")
                except ValueError:
                    self.text_result.insert("end", "Trọng số mới phải là số!\n")
                    return
            else:  # XÓA CẠNH
                del self.graph.edges[key]

                # XÓA TRONG NEBULA
                try:
                    session.execute(f'DELETE EDGE connect "{src}" -> "{dst}";')
                    if not self.graph.directed:
                        session.execute(f'DELETE EDGE connect "{dst}" -> "{src}";')
                    self.text_result.insert("end", f"Đã xóa cạnh {src}-{dst} khỏi NebulaGraph\n")
                except:
                    pass
                self.text_result.insert("end", f"Đã xóa cạnh {src}-{dst}\n")

        self.redraw_all()
        self.show_matrix()
        self.entry_src.delete(0, "end")
        self.entry_dst.delete(0, "end")
        self.entry_weight.delete(0, "end")

    def enable_move_mode(self):
        self.clear_result()
        self.move_mode = not self.move_mode
        if self.move_mode:
            self.text_result.insert("end", "Chế độ di chuyển: click và kéo đỉnh để di chuyển\n")
            self.canvas.config(cursor="hand2")
        else:
            self.text_result.insert("end", "Đã tắt chế độ di chuyển\n")
            self.canvas.config(cursor="")
            self.selected_vertex = None

    # không thêm đỉnh khi đang ở mode cạnh
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
        self.clear_result()
        self.clear_result()
        self.canvas.delete("all")
        self.graph = Graph(directed=(self.graph_type_var.get() == "co_huong"))
        self.vertex_count = 0
        self.text_result.insert("end", "Đã làm mới canvas - xóa hết đỉnh và cạnh\n")
        self.show_matrix()

    def redraw_all(self):
        self.canvas.delete("all")
        for vid in self.graph.vertices:
            self.draw_vertex(vid)
        for (u, v), w in self.graph.edges.items():
            v1 = self.graph.vertices[u]
            v2 = self.graph.vertices[v]
            mid_x = (v1.x + v2.x) / 2
            mid_y = (v1.y + v2.y) / 2
            if self.graph.directed:
                r = 20  # bán kính đỉnh
                dx = v2.x - v1.x
                dy = v2.y - v1.y
                dist = math.hypot(dx, dy)
                if dist == 0:
                    dist = 1
                offset_x = dx / dist * r
                offset_y = dy / dist * r

                self.canvas.create_line(v1.x + offset_x, v1.y + offset_y,
                                        v2.x - offset_x, v2.y - offset_y,
                                        fill="black", width=3,
                                        arrow=tk.LAST, arrowshape=(16, 20, 6))
            else:
                self.canvas.create_line(v1.x, v1.y, v2.x, v2.y, fill="black", width=3)
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
        if not self.graph.vertices:
            self.text_matrix.delete("1.0", "end")
            self.text_matrix.insert("end", "Đồ thị rỗng - chưa có đỉnh\n")
            return

        keys = sorted(self.graph.vertices.keys())
        n = len(keys)
        index = {k: i for i, k in enumerate(keys)}

        matrix = [[0 for _ in range(n)] for _ in range(n)]

        for (u, v), w in self.graph.edges.items():
            i = index[u]
            j = index[v]
            matrix[i][j] = w
            if not self.graph.directed:
                matrix[j][i] = w

        self.text_matrix.delete("1.0", "end")

        header = f"MA TRẬN KỀ - ĐỒ THỊ {'CÓ HƯỚNG' if self.graph.directed else 'VÔ HƯỚNG'}\n\n"
        self.text_matrix.insert("end", header)

        # Header cột
        col_header = "    |" + "".join(f" {k:>6} " for k in keys) + "\n"
        separator = "----+" + "--------" * n + "\n"
        self.text_matrix.insert("end", col_header)
        self.text_matrix.insert("end", separator)

        # Dòng ma trận
        for i, vid in enumerate(keys):
            row = f" {vid:>2} |"
            for j in range(n):
                val = matrix[i][j]
                if val == 0:
                    row += "   ∞   "
                else:
                    row += f" {val:>6} "
            row += "\n"
            self.text_matrix.insert("end", row)

        # Footer
        self.text_matrix.insert("end", "\n")
        self.text_matrix.insert("end", "∞ = không có cạnh trực tiếp\n")
        self.text_matrix.insert("end", f"Tổng số đỉnh: {n} | Tổng số cạnh: {len(self.graph.edges)}\n")
        self.text_matrix.see("1.0")

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
        self.clear_result()
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
        self.clear_result()
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
        self.clear_result()
        start = self.entry_start.get().strip()
        if not start:
            self.text_result.insert("end", "Vui lòng nhập đỉnh bắt đầu!\n")
            return
        if start not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh bắt đầu không hợp lệ!\n")
            return

        algo = Algorithm()
        algo.edges = self.graph.edges
        algo.directed = self.graph.directed  # vẫn giữ để model đúng
        algo.vertices = list(self.graph.vertices.keys())

        distances = algo.bellman_ford(algo.vertices, start)

        self.text_result.delete("1.0", "end")
        if distances is None:
            self.text_result.insert("end", "Đồ thị chứa chu trình âm đạt được từ đỉnh bắt đầu!\n")
        else:
            self.text_result.insert("end", f"Bellman-Ford từ đỉnh {start}:\n")
            for v in sorted(distances.keys()):
                d = distances[v]
                dist_str = "∞" if d == float("inf") else str(d)
                self.text_result.insert("end", f"Đỉnh {v}: {dist_str}\n")

    # duyệt dijkstra
    def run_dijkstra(self):
        start = self.entry_start.get().strip()

        if not start:
            self.text_result.insert("end", "Vui lòng nhập đỉnh bắt đầu!\n")
            return
        if start not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh bắt đầu không hợp lệ!\n")
            return

        algo = Algorithm()
        algo.edges = self.graph.edges
        algo.directed = self.graph.directed
        algo.vertices = self.graph.vertices.keys()

        # Gọi Dijkstra chỉ từ start đến tất cả các đỉnh (không cần end)
        distances = algo.dijkstra(start)  # Hàm dijkstra trong Algorithm phải trả dict distances

        self.text_result.delete("1.0", "end")
        self.text_result.insert("end", f"Thuật toán Dijkstra từ đỉnh {start} đến tất cả các đỉnh:\n\n")

        # Sắp xếp đỉnh theo thứ tự (để đẹp)
        for v in sorted(distances.keys()):
            d = distances[v]
            if d == float('inf'):
                self.text_result.insert("end", f"Đỉnh {v}: Không đến được\n")
            else:
                self.text_result.insert("end", f"Đỉnh {v}: {d}\n")

    # duyệt prim
    def run_prim(self):
        self.clear_result()
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
        self.clear_result()
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
        self.clear_result()
        self.text_result.delete("1.0", "end")

        algo = Algorithm(directed=(self.graph_type_var.get() == "co_huong"))
        algo.vertices = self.graph.vertices
        algo.edges = self.graph.edges
        colors = algo.sequential_coloring()

        self.text_result.insert("end", " Sequential Coloring:\n")
        for v, c in colors.items():
            self.text_result.insert("end", f"Đỉnh {v} → Màu {c}\n")

    def run_find_path(self):
        self.clear_result()
        start = self.start_vertex_cb.get().strip()
        end = self.end_vertex_cb.get().strip()

        if not start or not end:
            self.text_result.insert("end", "Vui lòng nhập cả đỉnh đầu và đỉnh đích!\n")
            return
        if start not in self.graph.vertices or end not in self.graph.vertices:
            self.text_result.insert("end", "Đỉnh không hợp lệ\n")
            return

        algo = Algorithm()
        algo.edges = self.graph.edges
        algo.directed = self.graph.directed
        algo.vertices = self.graph.vertices.keys()

        path, total_weight = algo.dijkstra_and_bellman_ford_path(start, end)

        self.text_result.delete("1.0", "end")
        if path is None:
            self.text_result.insert("end", f"Không có đường đi từ {start} đến {end}\n")
        else:
            self.text_result.insert("end", f"Đường đi ngắn nhất từ {start} đến {end}:\n")
            self.text_result.insert("end", " → ".join(path) + "\n")
            self.text_result.insert("end", f"Tổng trọng số: {total_weight}\n")

    def refresh_space_list(self):
        self.clear_result()

        session = self.connect_graph_space()
        if session is None:
            self.space_cb['values'] = ("graph_project",)
            self.space_var.set("graph_project")
            return
        try:
            result = session.execute("SHOW SPACES;")
            if not result.is_succeeded():
                raise Exception("SHOW SPACES thất bại")

            spaces = []
            for row in result.rows():
                spaces.append(row.values[0].get_sVal().decode())

            self.space_cb['values'] = tuple(spaces)

            if spaces:
                self.space_var.set(spaces[0])
                self.text_result.insert(
                    "end",
                    f"ONLINE: số lượng space {len(spaces)}, space được kết nối: {', '.join(spaces)}\n"
                )
            else:
                self.text_result.insert("end", "ONLINE: Không có space nào\n")

        except Exception as e:
            self.text_result.insert("end", f"Lỗi NebulaGraph: {e}\n")

    def load_from_db(self):
        self.clear_result()

        session = self.connect_graph_space()
        if session is None:
            self.text_result.insert("end", "Không thể load - đang chạy offline\n")
            return

        self.text_result.insert("end", "Đang load đồ thị từ database...\n")
        self.text_result.see("end")

        try:
            # 1. Đọc config hướng
            is_directed_from_db = False
            try:
                config_result = session.execute(
                    'MATCH (v:graph_config) WHERE id(v) == "config" YIELD v.is_directed'
                )
                if config_result.is_succeeded() and config_result.row_size() > 0:
                    val = config_result.rows()[0].values[0]
                    if val.is_bool():
                        is_directed_from_db = val.as_bool()
            except:
                pass

            # 2. Set hướng đồ thị
            self.graph_type_var.set("co_huong" if is_directed_from_db else "vo_huong")
            self.graph.directed = is_directed_from_db

            # 3. Lấy cạnh
            result = session.execute(
                '''
                MATCH (v1)-[e:connect]->(v2)
                RETURN
                  tostring(id(v1)),
                  tostring(id(v2)),
                  CASE WHEN e.weight IS NULL THEN 1.0 ELSE toFloat(e.weight) END
                LIMIT 1000
                '''
            )
            if not result.is_succeeded() or result.row_size() == 0:
                self.text_result.insert("end", "Space trống hoặc không có cạnh!\n")
                return

            # 4. Lấy tọa độ đỉnh
            coordinates = {}
            coord_result = session.execute(
                '''
                MATCH (v:point)
                RETURN
                  tostring(id(v)),
                  CASE WHEN v.x IS NULL THEN NULL ELSE toFloat(v.x) END,
                  CASE WHEN v.y IS NULL THEN NULL ELSE toFloat(v.y) END
                '''
            )

            if coord_result.is_succeeded():
                for row in coord_result.rows():
                    vid = row.values[0].get_sVal().decode("utf-8")

                    x_val = row.values[1]
                    y_val = row.values[2]

                    try:
                        x = x_val.get_dVal()
                        y = y_val.get_dVal()
                    except AssertionError:
                        continue  # bỏ đỉnh lỗi

                    coordinates[vid] = (x, y)

            # 5. Xóa cũ, tạo graph mới
            self.canvas.delete("all")
            self.graph = Graph(directed=is_directed_from_db)
            self.vertex_count = 0

            # 6. Thêm đỉnh vào model
            vertices_set = set()
            for row in result.rows():
                src = row.values[0].get_sVal().decode("utf-8")
                dst = row.values[1].get_sVal().decode("utf-8")
                vertices_set.add(src)
                vertices_set.add(dst)

            w_canvas, h_canvas = 678, 400
            for vid in vertices_set:
                x, y = coordinates.get(vid, (random.randint(50, w_canvas - 50), random.randint(50, h_canvas - 50)))
                self.graph.add_vertex(vid, x, y)
                self.vertex_count = max(self.vertex_count, int(vid) if vid.isdigit() else 0)

            # 7. Thêm cạnh vào model
            for row in result.rows():
                src = row.values[0].get_sVal().decode("utf-8")
                dst = row.values[1].get_sVal().decode("utf-8")

                try:
                    weight = row.values[2].get_dVal()
                except AssertionError:
                    weight = 1.0  # fallback

                self.graph.add_edge(src, dst, weight)

            # 8. DÙNG REDRAW_ALL ĐỂ VẼ TOÀN BỘ (chỉ 1 dòng!)
            self.redraw_all()

            # 9. Cập nhật ma trận
            self.show_matrix()

            self.text_result.insert("end",
                                    f"Load thành công {len(vertices_set)} đỉnh, {len(result.rows())} cạnh từ DB!\n")

        except Exception as e:
            self.text_result.insert("end", f"Lỗi load: {str(e)}\n")
            self.text_result.insert("end", "Chương trình vẫn chạy offline bình thường.\n")
            import traceback
            self.text_result.insert("end", "Lỗi load (traceback):\n")
            self.text_result.insert("end", traceback.format_exc() + "\n")

    def rebuild_edges_on_type_change(self):
        old_edges = list(self.graph.edges.items())
        new_edges = {}

        if self.graph.directed:
            # vô hướng → có hướng
            for (u, v), w in old_edges:
                new_edges[(u, v)] = w
                new_edges[(v, u)] = w
        else:
            # có hướng → vô hướng
            for (u, v), w in old_edges:
                key = tuple(sorted([u, v]))
                new_edges[key] = w
        self.graph.edges = new_edges

    def connect_graph_space(self):
        try:
            session = NebulaDB.get_session()
            if session is None:
                raise Exception("Session rỗng")

            space = "graph_project"
            result = session.execute(f"USE {space};")

            if not result.is_succeeded():
                raise Exception("Không USE được space")

            self.space_var.set(space)
            self.text_result.insert("end", f"ONLINE: Đã kết nối space\n")

            return session

        except Exception as e:
            self.text_result.insert(
                "end",
                f"OFFLINE: Không kết nối được space graph_project ({e})\n"
            )
            return None

    def save_vertex_to_db(self, vid, x, y):
        if not self.connect_graph_space():
            return

        try:
            session = NebulaDB.get_session()
            session.execute(
                f'INSERT VERTEX point(x, y) VALUES "{vid}":({x}, {y});'
            )
        except Exception as e:
            self.text_result.insert("end", f"Lỗi lưu đỉnh {vid}: {e}\n")

    def save_edge_to_db(self, src, dst, weight):
        if not self.connect_graph_space():
            return

        try:
            session = NebulaDB.get_session()
            session.execute(
                f'INSERT EDGE connect(weight) VALUES "{src}"->"{dst}":({weight});'
            )
        except Exception as e:
            self.text_result.insert("end", f"Lỗi lưu cạnh {src}->{dst}: {e}\n")
    def clear_result(self):
        self.text_result.delete("1.0", "end")