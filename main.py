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
tk.Radiobutton(frame_graph_type, text="Đồ thị vô hướng", bg="cyan", variable=graph_type, value="vo_huong").pack(anchor="w")
tk.Radiobutton(frame_graph_type, text="Đồ thị có hướng", bg="cyan", variable=graph_type, value="co_huong").pack(anchor="w")

# Khung chọn đỉnh tìm đường đi
frame_vertices = tk.LabelFrame(root, text="Đỉnh", bg="cyan")
frame_vertices.place(x=220, y=10, width=396, height=80)

tk.Label(frame_vertices, text="Đỉnh đầu:", bg="cyan").grid(row=0, column=0, sticky="w", padx=5, pady=5)
start_vertex = ttk.Combobox(frame_vertices, values=["1","2","3","4","5"])
start_vertex.grid(row=1, column=0, padx=5, pady=5)

tk.Label(frame_vertices, text="Đỉnh đích:", bg="cyan").grid(row=0, column=1, sticky="w", padx=5, pady=5)
end_vertex = ttk.Combobox(frame_vertices, values=["1","2","3","4","5"])
end_vertex.grid(row=1, column=1, padx=5, pady=5)

tk.Button(frame_vertices, text="Tìm đường đi").grid(row=1, column=2, padx=1, pady=1)

# Canvas vẽ đồ thị
canvas = tk.Canvas(root, bg="white", width=678, height=400)
canvas.place(x=10, y=90)

# Khung duyệt đồ thị (bên phải trên)
frame_right = tk.Frame(root, bg="cyan")
frame_right.place(x=617, y=10, width=375, height=80)

frame_traverse = tk.LabelFrame(frame_right, text="Duyệt đồ thị", bg="cyan")
frame_traverse.pack(fill="x", padx=5, pady=5, ipady=10, ipadx=10)

tk.Label(frame_traverse, text="Loại thuật toán:", bg="cyan").grid(row=0, column=0, padx=5, pady=5, sticky="w")
cb_start = ttk.Combobox(frame_traverse,
                        values=["DFS", "BFS", "Bellman-Ford", "Dijkstra", "Prim", "Kruskal", "Sequential Color"],
                        state="readonly",
                        width=15)
cb_start.current(0)
cb_start.grid(row=0, column=1, padx=5, pady=5)

btn_right = tk.Button(frame_traverse, text="Duyệt", width=10)
btn_right.grid(row=0, column=2, padx=5, pady=5)

# Hiển thị kết quả và ma trận
frame_display = ttk.LabelFrame(root, text="Hiển thị")
frame_display.place(x=10, y=480, width=980, height=200)

# Kết quả
frame_result = ttk.LabelFrame(frame_display, text="Kết quả")
frame_result.place(x=10, y=10, width=470, height=170)

text_result = tk.Text(frame_result, wrap="none")
text_result.pack(side="left", fill="both", expand=True)
scroll_result = ttk.Scrollbar(frame_result, orient="vertical", command=text_result.yview)
scroll_result.pack(side="right", fill="y")
text_result.configure(yscrollcommand=scroll_result.set)

# Ma trận
frame_matrix = ttk.LabelFrame(frame_display, text="Ma trận")
frame_matrix.place(x=490, y=10, width=470, height=170)

text_matrix = tk.Text(frame_matrix, wrap="none")
text_matrix.pack(side="left", fill="both", expand=True)
scroll_matrix = ttk.Scrollbar(frame_matrix, orient="vertical", command=text_matrix.yview)
scroll_matrix.pack(side="right", fill="y")
text_matrix.configure(yscrollcommand=scroll_matrix.set)

frame_add = tk.LabelFrame(root, text="Chức năng", bg="cyan")
frame_add.place(x=693, y=93, width=298, height=387)

# Các Entry cho thêm cạnh
tk.Label(frame_add, text="Đỉnh đầu:", bg="cyan").grid(row=0, column=0, sticky="e", padx=10, pady=8)
tk.Label(frame_add, text="Đỉnh cuối:", bg="cyan").grid(row=1, column=0, sticky="e", padx=10, pady=8)
tk.Label(frame_add, text="Trọng số:", bg="cyan").grid(row=2, column=0, sticky="e", padx=10, pady=8)

entry_src = tk.Entry(frame_add)
entry_src.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=8)
entry_dst = tk.Entry(frame_add)
entry_dst.grid(row=1, column=1, sticky='ew', padx=(0, 10), pady=8)
entry_weight = tk.Entry(frame_add)
entry_weight.grid(row=2, column=1, sticky='ew', padx=(0, 10), pady=8)

# Nút Thêm cạnh
btn_add_edge = tk.Button(frame_add, text="Thêm cạnh", width=25, bg="lightgreen")
btn_add_edge.grid(row=3, column=0, columnspan=3,sticky="we", padx=5, pady=25, ipady=10)


controller = GraphController(
    canvas=canvas,
    graph_type_var=graph_type,
    text_result=text_result,
    text_matrix=text_matrix,
    entry_src=entry_src,
    entry_dst=entry_dst,
    entry_weight=entry_weight,
    btn_add_edge=btn_add_edge
)

# Bind nút "Thêm cạnh" để gọi hàm add_edge trong controller
btn_add_edge.config(command=controller.add_edge)

tk.Button(frame_add, text="Thêm đỉnh", command=controller.enable_add_vertex).grid(row=4, column=0, columnspan=3, sticky="we", padx=5, pady=35, ipady=10)
tk.Button(frame_add, text="Cập nhật", padx=20, pady=8).grid(row=5, column=0, padx=(0,5), sticky="we")
tk.Button(frame_add, text="Di chuyển", padx=20, pady=8).grid(row=5, column=1, padx=(0, 5), sticky="we")
tk.Button(frame_add, text="Làm mới", padx=20, pady=8).grid(row=5, column=2, sticky="we")

frame_add.columnconfigure(0, weight=1, uniform="group")
frame_add.columnconfigure(1, weight=1, uniform="group")
frame_add.columnconfigure(2, weight=1, uniform="group")


# Khởi chạy ứng dụng
root.mainloop()