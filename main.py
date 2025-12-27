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
start_vertex_cb = ttk.Entry(frame_vertices)
start_vertex_cb.grid(row=1, column=0, padx=5, pady=5)

tk.Label(frame_vertices, text="Đỉnh đích:", bg="cyan").grid(row=0, column=1, sticky="w", padx=5, pady=5)
end_vertex_cb = ttk.Entry(frame_vertices)
end_vertex_cb.grid(row=1, column=1, padx=5, pady=5)

btn_find_path = tk.Button(frame_vertices, text="Tìm đường đi", bg="orange")
btn_find_path.grid(row=1, column=2, padx=1, pady=1)

# Canvas vẽ đồ thị
canvas = tk.Canvas(root, bg="white", width=678, height=400)
canvas.place(x=10, y=90)

# Khung duyệt đồ thị (bên phải trên)
frame_right = tk.Frame(root, bg="cyan")
frame_right.place(x=617, y=10, width=375, height=80)

frame_traverse = tk.LabelFrame(frame_right, text="Duyệt đồ thị", bg="cyan")
frame_traverse.pack(fill="x", padx=1, pady=1, ipady=5, ipadx=5)

tk.Label(frame_traverse, text="Loại thuật toán:", bg="cyan").grid(row=0, column=0, padx=1, pady=1, sticky="w")
cb_start = ttk.Combobox(frame_traverse,
                        values=["DFS", "BFS", "Bellman-Ford", "Dijkstra", "Prim", "Kruskal", "Sequential Color"],
                        state="readonly",
                        width=15)
cb_start.current(0)
cb_start.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_traverse, text="Đỉnh bắt đầu:", bg="cyan").grid(row=1, column=0, padx=1, pady=1, sticky="w")
entry_right = tk.Entry(frame_traverse)
entry_right.grid(row=1, column=1, padx=1, pady=1)
btn_right = tk.Button(frame_traverse, text="Duyệt", width=10, height=1)
btn_right.grid(row=1, column=2, padx=30, pady=1)


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

# Combobox chọn space (đồ thị)
space_var = tk.StringVar()
space_cb = ttk.Combobox(frame_add, textvariable=space_var, state="readonly", width=22)
space_cb['values'] = ()
space_cb.grid(row=4, column=2, columnspan=3, padx=5, pady=5)
# btn_load_db = tk.Button(frame_add, text="Mở data", bg="yellow")
# btn_load_db.grid(row=4, column=0, columnspan=1,sticky="w", padx=5, pady=5, ipady=10)
btn_save_config = tk.Button(frame_add, text="Lưu config", bg="lightblue")
btn_save_config.grid(row=4, column=1, columnspan=1, pady=5, sticky="w")
btn_add_vertex = tk.Button(frame_add, text="Thêm đỉnh")

btn_add_vertex.grid(row=5, column=0, columnspan=3, sticky="we", padx=5, pady=5, ipady=10)
btn_update = tk.Button(frame_add, text="Cập nhật", padx=20, pady=8)
btn_update.grid(row=6, column=0, padx=(0,5), sticky="we")
btn_move = tk.Button(frame_add, text="Di chuyển", padx=20, pady=8)
btn_move.grid(row=6, column=1, padx=(0, 5), sticky="we")
btn_clear = tk.Button(frame_add, text="Làm mới", padx=20, pady=8)
btn_clear.grid(row=6, column=2, sticky="we")


controller = GraphController(
    canvas=canvas,
    graph_type_var=graph_type,
    text_result=text_result,
    text_matrix=text_matrix,
    entry_src=entry_src,
    entry_dst=entry_dst,
    entry_weight=entry_weight,
    btn_add_edge=btn_add_edge,
    algo_var=cb_start,
    entry_start=entry_right,
    space_cb=space_cb,
    # btn_load_db=btn_load_db,
    btn_update=btn_update,
    btn_move=btn_move,
    btn_clear=btn_clear,
    start_vertex_cb=start_vertex_cb,
    end_vertex_cb=end_vertex_cb,
    btn_find_path=btn_find_path,
    space_var=space_var
)

# thực hiện các chức năng từ controller
btn_add_edge.config(command=controller.add_edge)
btn_right.config(command=controller.run_algorithm)
btn_add_vertex.config(command=controller.enable_add_vertex)
# btn_load_db.config(command=controller.load_from_db)
btn_update.config(command=controller.update_graph)
btn_move.config(command=controller.enable_move_mode)
btn_clear.config(command=controller.clear_canvas)
btn_find_path.config(command=controller.run_find_path)
btn_save_config.config(command=controller.save_graph_config)


frame_add.columnconfigure(0, weight=1, uniform="group")
frame_add.columnconfigure(1, weight=1, uniform="group")
frame_add.columnconfigure(2, weight=1, uniform="group")


# Khởi chạy ứng dụng
root.mainloop()