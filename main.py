import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Đồ thị")
root.geometry("1000x700")  

# Khung chọn loại đồ thị
frame_graph_type = tk.LabelFrame(root, text="Loại đồ thị", bg="cyan")
frame_graph_type.place(x=10, y=10, width=200, height=70)

graph_type = tk.StringVar(value="vo_huong")
tk.Radiobutton(frame_graph_type, text="Đồ thị vô hướng", variable=graph_type, value="vo_huong").pack(anchor="w")
tk.Radiobutton(frame_graph_type, text="Đồ thị có hướng", variable=graph_type, value="co_huong").pack(anchor="w")


# Khung chọn đỉnh tìm đường đi
frame_vertices = tk.LabelFrame(root, text="Đỉnh", bg="cyan")
frame_vertices.place(x=220, y=10, width=396, height=70)

start_vertex = ttk.Combobox(frame_vertices, values=["1","2","3","4","5"])
start_vertex.grid(row=0, column=0)
end_vertex = ttk.Combobox(frame_vertices, values=["1","2","3","4","5"])
end_vertex.grid(row=0, column=1)

tk.Button(frame_vertices, text="Tìm đường đi").grid(row=0, column=2)

# Canvas vẽ đồ thị
canvas = tk.Canvas(root, bg="white", width=600, height=400)
canvas.place(x=10, y=90)

# Khung thêm cạnh đỉnh
frame_add = tk.LabelFrame(root, text="Chức năng", bg="cyan")
frame_add.place(x=650, y=93, width=300, height=400)

tk.Label(frame_add, text="Đỉnh đầu:").grid(row=0, column=0)
tk.Label(frame_add, text="Đỉnh cuối:").grid(row=1, column=0)
tk.Label(frame_add, text="Trọng số:").grid(row=2, column=0)

start_entry = tk.Entry(frame_add)
start_entry.grid(row=0, column=1)
end_entry = tk.Entry(frame_add)
end_entry.grid(row=1, column=1)
weight_entry = tk.Entry(frame_add)
weight_entry.grid(row=2, column=1)

tk.Button(frame_add, text="Thêm cạnh").grid(row=3, column=0, columnspan=2, sticky="we")
tk.Button(frame_add, text="Thêm đỉnh").grid(row=4, column=0, columnspan=2, sticky="we")
tk.Button(frame_add, text="Cập nhật").grid(row=5, column=0, sticky="we")
tk.Button(frame_add, text="Di chuyển").grid(row=5, column=1, sticky="we")
tk.Button(frame_add, text="Làm mới").grid(row=6, column=0, columnspan=2, sticky="we")

# Hiển thị kết quả ma trận
result_text = tk.Text(root, width=50, height=10)
result_text.place(x=10, y=500)

matrix_text = tk.Text(root, width=50, height=10)
matrix_text.place(x=550, y=500)


root.mainloop()
