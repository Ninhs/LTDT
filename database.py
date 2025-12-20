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
            config.timeout = 30000

            cls._pool = ConnectionPool()
            cls._pool.init([('127.0.0.1', 9669)], config)

            cls._session = cls._pool.get_session('root', 'nebula')
            cls._session.execute('USE graph_project;')

    @classmethod
    def get_session(cls):
        if cls._session is None:
            cls.init()
        return cls._session

    @classmethod
    def close(cls):
        if cls._pool:
            cls._pool.close()