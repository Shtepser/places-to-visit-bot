import os

import redis

from Place import Place
from Stage import Stage


REDIS_URL = os.environ.get("REDIS_URL")


class Database:

    def __init__(self):
        self.__places = redis.from_url(REDIS_URL, db=0)
        self.__stages = redis.from_url(REDIS_URL, db=1)

    def has_user(self, user_id) -> bool:
        return bool(self.__places.hkeys(user_id)) and self.__stages.get(user_id) is not None

    def add_place(self, user_id, place: Place):
        self.__places.hset(user_id, place.name, repr(place))

    def get_places(self, user_id) -> list:
        return [Place.from_string(self.__places.hget(user_id, key).decode("utf8"))
                for key in self.__places.hkeys(user_id)]

    def get_place_by_name(self, user_id, place_name):
        return Place.from_string(self.__places.hget(user_id, place_name).decode("utf8"))

    def remove_place(self, user_id, place: Place):
        self.__places.hdel(user_id, place.name)

    def reset_user(self, user_id):
        self.__places.delete(user_id)
        self.__stages.delete(user_id)
        self.clean_staged_place_name(user_id)

    def set_user_stage(self, user_id, stage: Stage):
        self.__stages.set(user_id, stage.value)

    def get_user_stage(self, user_id):
        stage_code = self.__stages.get(user_id)
        if not stage_code:
            return None
        return Stage(int(stage_code))

    def set_staged_place_name(self, user_id, place_name):
        self.__stages.set(f"staged_name_{user_id}", place_name)

    def get_staged_place_name(self, user_id):
        staged_name = self.__stages.get(f"staged_name_{user_id}")
        if staged_name:
            return staged_name.decode("utf8")
        return None

    def clean_staged_place_name(self, user_id):
        self.__stages.delete(f"staged_name_{user_id}")
