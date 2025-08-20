from contextlib import contextmanager
import redis as redis


class RedisBase:
    def __init__(self, process_id: str):
        self.host = "localhost"
        self.port = 6379
        self.process_id = process_id
        self.redis_db = 0

    @contextmanager
    def redis_session(self):
        session = redis.Redis(
            host=self.host, port=self.port, db=self.redis_db, decode_responses=True
        )
        try:
            yield session
        except Exception as e:
            print(f"REDIS: Session error {e}")
        finally:
            session.close()

    # To set a log
    def set_log(self, message: str):
        with self.redis_session() as session:
            session.lpush(self.process_id, message)

    # To retrieve a log
    def get_log(self) -> str:
        with self.redis_session() as session:
            value = session.lrange(self.process_id, 0, -1)
            value = " \n".join(value)
            return value


if __name__ == "__main__":
    redis_base = RedisBase("testid")
    redis_base.set_log("Hi")
    out = redis_base.get_log()
    print(out)
