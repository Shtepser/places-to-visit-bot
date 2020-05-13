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
        lat, lon = round(place.lat, 6), round(place.lon, 6)
        name = re.sub(r'_+', '_', place.name)
        return bool(self.database.sadd(user_id, f"{name}__{lat}__{lon}"))

    def get_places(self, user_id) -> list:
        raw_places = [place.decode("utf8").split("__") for place in self.database.smembers(user_id)]
        return [Place(name, float(lat), float(lon)) for name, lat, lon in raw_places]

    def reset_user(self, user_id) -> bool:
        return bool(self.database.delete(user_id) == 1)
