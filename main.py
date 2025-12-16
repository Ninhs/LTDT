import tkinter as tk
from tkinter import ttk
from graph_controller import GraphController


root = tk.Tk()
root.title("Đồ thị")
root.geometry("1000x700")
root.resizable(False, False)


# Khung chọn loại đồ thị
frame_graph_type = tk.LabelFrame(root, text="Loại đồ thị", bg="cyan")
frame_graph_type.place(x=10, y=10, width=210, height=80)

graph_type = tk.StringVar(value="vo_huong")
tk.Radiobutton(frame_graph_type, text="Đồ thị vô hướng", variable=graph_type, value="vo_huong").pack(anchor="w")
tk.Radiobutton(frame_graph_type, text="Đồ thị có hướng", variable=graph_type, value="co_huong").pack(anchor="w")


# Khung chọn đỉnh tìm đường đi
frame_vertices = tk.LabelFrame(root, text="Đỉnh", bg="cyan")
frame_vertices.place(x=220, y=10, width=396, height=80)

tk.Label(frame_vertices, text="Đỉnh đầu:").grid(row=0, column=0, sticky="w")
start_vertex = ttk.Combobox(frame_vertices, values=["1","2","3","4","5"])
start_vertex.grid(row=1, column=0)
tk.Label(frame_vertices, text="Đỉnh đích:").grid(row=0, column=1, sticky="w")
end_vertex = ttk.Combobox(frame_vertices, values=["1","2","3","4","5"])
end_vertex.grid(row=1, column=1)

tk.Button(frame_vertices, text="Tìm đường đi").grid(row=1, column=2)

# Canvas vẽ đồ thị
canvas = tk.Canvas(root, bg="white", width=678, height=400)
canvas.place(x=10, y=90)

# Khung duyệt đồ thị
frame_right = tk.Frame(root, bg="cyan")
frame_right.place(x=617, y=10, width=375, height=80)

frame_traverse = tk.LabelFrame(frame_right, text="Duyệt đồ thị")
frame_traverse.pack(fill="x", padx=5, pady=5)

ttk.Label(frame_traverse, text="Loại thuật toán:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

cb_start = ttk.Combobox(frame_traverse,
                        values=["DFS", "BFS", "Bellman-Ford", "Dijkstra", "Prim", "Kruskal", "Sequential Color"],
                        state="readonly",
                        width=15)
cb_start.current(0)
cb_start.grid(row=0, column=1, padx=5, pady=5)

btn_right = tk.Button(frame_traverse, text="Duyệt", width=10)
btn_right.grid(row=0, column=2)

frame_traverse.columnconfigure(0, weight=1)
frame_traverse.columnconfigure(1, weight=1)





# Hiển thị kết quả ma trận
frame_display = ttk.LabelFrame(root, text="Hiển thị")
frame_display.place(x=10, y=480, width=980, height=200)

# Kết quả
frame_result = ttk.LabelFrame(frame_display, text="Kết quả")
frame_result.place(x=10, y=10, width=470, height=170)

text_result = tk.Text(frame_result, wrap="none")
text_result.pack(side="left", fill="both", expand=True)

scroll_result = ttk.Scrollbar(frame_result, orient="vertical")
scroll_result.pack(side="right", fill="y")

text_result.configure(yscrollcommand=scroll_result.set)

# Ma trận
frame_matrix = ttk.LabelFrame(frame_display, text="Ma trận")
frame_matrix.place(x=490, y=10, width=470, height=170)

text_matrix = tk.Text(frame_matrix, wrap="none")
text_matrix.pack(side="left", fill="both", expand=True)

scroll_matrix = ttk.Scrollbar(frame_matrix, orient="vertical")
scroll_matrix.pack(side="right", fill="y")

text_matrix.configure(yscrollcommand=scroll_matrix.set)

# object vẽ đồ thị
controller = GraphController(
    canvas=canvas,
    graph_type_var=graph_type,
    text_result=text_result,
    text_matrix=text_matrix
)

# Khung chức năng
frame_add = tk.LabelFrame(root, text="Chức năng", bg="cyan")
frame_add.place(x=693, y=93, width=298, height=387)

tk.Label(frame_add, text="Đỉnh đầu:").grid(row=0, column=0)
tk.Label(frame_add, text="Đỉnh cuối:").grid(row=1, column=0)
tk.Label(frame_add, text="Trọng số:").grid(row=2, column=0)

start_entry = tk.Entry(frame_add, width=38)
start_entry.grid(row=0, column=1)
end_entry = tk.Entry(frame_add, width=38)
end_entry.grid(row=1, column=1)
weight_entry = tk.Entry(frame_add, width=38)
weight_entry.grid(row=2, column=1)

tk.Button(frame_add, text="Thêm cạnh").grid(row=3, column=0, columnspan=2, sticky="we")
tk.Button(frame_add, text="Thêm đỉnh", command=controller.enable_add_vertex).grid(row=4, column=0, columnspan=2, sticky="we")
tk.Button(frame_add, text="Cập nhật").grid(row=5, column=0, sticky="we")
tk.Button(frame_add, text="Di chuyển").grid(row=5, column=1, sticky="we")
tk.Button(frame_add, text="Làm mới").grid(row=6, column=0, columnspan=2, sticky="we")


root.mainloop()
