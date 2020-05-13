import os
import re

import redis

from Place import Place


class Database:

    def __init__(self):
        self.database = redis.from_url(os.environ.get("REDIS_URL"), db=0)

    def has_user(self, user_id) -> bool:
        return bool(self.database.smembers(user_id))

    def add_place(self, user_id, place: Place) -> bool:
        return bool(self.database.sadd(user_id, repr(place)))

    def get_places(self, user_id) -> list:
        return [Place.from_string(place.decode("utf8"))
                for place in self.database.smembers(user_id)]

    def remove_place(self, user_id, place: Place):
        return self.database.srem(user_id, repr(place)) == 1

    def reset_user(self, user_id) -> bool:
        return bool(self.database.delete(user_id) == 1)
