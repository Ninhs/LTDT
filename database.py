from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config

class NebulaDB:
    _pool = None
    _session = None

    @classmethod
    def init(cls):
        if cls._pool is None:
            config = Config()
            config.max_connection_pool_size = 10
            config.timeout = 30000  # 30 giây

            cls._pool = ConnectionPool()
            try:
                cls._pool.init([('127.0.0.1', 9669)], config)
                cls._session = cls._pool.get_session('root', 'nebula')
                cls._session.execute('USE graph_project;')
            except Exception as e:
                print(f"Lỗi kết nối NebulaGraph: {e}")
                cls._pool = None
                cls._session = None
                raise

    @classmethod
    def get_session(cls):
        if cls._session is None:
            import time
            for attempt in range(5):
                try:
                    cls.init()
                    return cls._session
                except Exception as e:
                    print(f"Lần thử {attempt + 1}/5: Chưa kết nối được NebulaGraph ({e}), chờ 5 giây...")
                    time.sleep(5)
            raise RuntimeError("Không thể kết nối NebulaGraph sau 5 lần thử")
        return cls._session

    @classmethod
    def close(cls):
        if cls._pool:
            cls._pool.close()