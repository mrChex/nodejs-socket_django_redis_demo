import json
from redis_sessions.session import SessionStore as RedisSessionStore
import pickle



class SessionStore(RedisSessionStore):

    def encode(self, session_dict):
        "Returns the given session dictionary pickled and encoded as a string."
        pickled = pickle.dumps(session_dict, pickle.HIGHEST_PROTOCOL)
        hash = self._hash(pickled)
        return base64.b64encode(hash.encode() + b":" + pickled).decode('ascii')

    def decode(self, session_data):
        encoded_data = base64.b64decode(force_bytes(session_data))
        try:
            # could produce ValueError if there is no ':'
            hash, pickled = encoded_data.split(b':', 1)
            expected_hash = self._hash(pickled)
            if not constant_time_compare(hash.decode(), expected_hash):
                raise SuspiciousOperation("Session data corrupted")
            else:
                return pickle.loads(pickled)
        except Exception:
            # ValueError, SuspiciousOperation, unpickling exceptions. If any of
            # these happen, just return an empty dictionary (an empty session).
            return {}