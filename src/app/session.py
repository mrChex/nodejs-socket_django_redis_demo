import json
from redis_sessions.session import SessionStore as RedisSessionStore


class SessionStore(RedisSessionStore):

    def encode(self, session_dict):
        return json.dumps(session_dict)

    def decode(self, session_data):
        return json.loads(session_data)
