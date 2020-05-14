import os

import redis

from Place import Place
from Stage import Stage


class Database:

    def __init__(self):
        redis_path = os.environ.get("REDIS_URL")
        self.__places = redis.from_url(redis_path, db=0)
        self.__stages = redis.from_url(redis_path, db=1)
        self.__staged_place_names = redis.from_url(redis_path, db=2)

    def has_user(self, user_id) -> bool:
        return bool(self.__places.smembers(user_id)) and self.__stages.get(user_id) is not None

    def add_place(self, user_id, place: Place) -> bool:
        return bool(self.__places.sadd(user_id, repr(place)))

    def get_places(self, user_id) -> list:
        return [Place.from_string(place.decode("utf8"))
                for place in self.__places.smembers(user_id)]

    def remove_place(self, user_id, place: Place):
        return self.__places.srem(user_id, repr(place)) == 1

    def reset_user(self, user_id) -> bool:
        return self.__places.delete(user_id) == 1 and self.__stages.delete(user_id) == 1

    def set_user_stage(self, user_id, stage: Stage):
        return self.__stages.set(user_id, stage.value)

    def get_user_stage(self, user_id):
        return Stage(int(self.__stages.get(user_id)))

    def set_staged_place_name(self, user_id, place_name):
        return self.__staged_place_names.set(user_id, place_name) == 1

    def get_staged_place_name(self, user_id):
        staged_name = self.__staged_place_names.get(user_id)
        if staged_name:
            return staged_name.decode("utf8")
        return None

    def clean_staged_place_name(self, user_id):
        return self.__staged_place_names.delete(user_id) == 1