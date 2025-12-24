from database import NebulaDB  # hoặc copy class NebulaDB vào đây

session = NebulaDB.get_session()
result = session.execute('SHOW SPACES;')
if result.is_succeeded():
    print("ONLINE THÀNH CÔNG!")
    for row in result.rows():
        print(row)
else:
    print("Lỗi:", result.error_msg())