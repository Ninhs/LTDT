from graph_model import Graph

class GraphController:
    def __init__(self, canvas, graph_type_var, text_result, text_matrix):
        self.canvas = canvas
        self.graph_type_var = graph_type_var
        self.text_result = text_result
        self.text_matrix = text_matrix

        self.graph = Graph()
        self.vertex_count = 0

        self.add_vertex_mode = False
        self.hint_shown = False

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def enable_add_vertex(self):
        self.add_vertex_mode = not self.add_vertex_mode

        if self.add_vertex_mode:
            if not self.hint_shown:
                self.text_result.insert(
                    "end",
                    "Chế độ thêm đỉnh: click vào màng hình bên trên để thêm\n"
                )
                self.hint_shown = True

        else:
            self.text_result.insert(
                "end",
                "Đã tắt chế độ thêm đỉnh\n"
            )
            self.hint_shown = False

    def add_vertex(self, event):
        vid = str(self.vertex_count + 1)
        self.graph.add_vertex(vid, event.x, event.y)
        self.vertex_count += 1
        self.draw_vertex(vid)
        self.show_matrix()

    # Click Màng hình sẽ thêm được đỉnh
    def on_canvas_click(self, event):
        if not self.add_vertex_mode:
            return

        self.add_vertex(event)

    def draw_vertex(self, vid):
        v = self.graph.vertices[vid]
        r = 15
        self.canvas.create_oval(v.x-r, v.y-r, v.x+r, v.y+r, fill="lightblue")
        self.canvas.create_text(v.x, v.y, text=vid)

    def traverse_graph(self):
        self.text_result.delete("1.0", "end")
        self.text_result.insert("end", "Đang duyệt đồ thị...\n")

    def show_matrix(self):
        self.text_matrix.delete("1.0", "end")
        keys, matrix = self.graph.adjacency_matrix()

        self.text_matrix.insert("end", "   " + " ".join(keys) + "\n")
        for i, row in enumerate(matrix):
            self.text_matrix.insert("end", keys[i] + "  " + " ".join(map(str, row)) + "\n")

