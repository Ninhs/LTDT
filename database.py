from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
import time

class NebulaDB:
    _pool = None
    _session = None

    @classmethod
    def get_session(cls):
        if cls._session is not None:
            return cls._session

        for attempt in range(5):
            try:
                if cls._pool is None:
                    config = Config()
                    config.max_connection_pool_size = 10
                    config.timeout = 30000

                    cls._pool = ConnectionPool()
                    cls._pool.init([('127.0.0.1', 9669)], config)

                cls._session = cls._pool.get_session('root', 'nebula')

                # Test kết nối bằng query đơn giản
                result = cls._session.execute('YIELD 1;')
                if result.is_succeeded():
                    print("Kết nối NebulaGraph thành công!")
                    return cls._session
                else:
                    raise Exception("Query test thất bại")

            except Exception as e:
                print(f"Lần thử {attempt + 1}/5: Không kết nối được NebulaGraph ({e}), chờ 5 giây...")
                time.sleep(5)
                cls._session = None

        # Nếu hết 5 lần → trả session fake để app không crash
        print("Chạy ở chế độ OFFLINE (không kết nối NebulaGraph)")
        class FakeSession:
            def execute(self, query):
                print(f"[FAKE NEBULA] {query}")
                class FakeResult:
                    def is_succeeded(self):
                        return True
                    def rows(self):
                        return []
                    def error_msg(self):
                        return ""
                return FakeResult()

        cls._session = FakeSession()
        return cls._session

    @classmethod
    def close(cls):
        if cls._pool:
            cls._pool.close()
            cls._pool = None
            cls._session = None