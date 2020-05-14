import os

import redis

from Place import Place
from Stage import Stage


class Database:

    def __init__(self):
        redis_URL = os.environ.get("REDIS_URL")
        self.__places = redis.from_url(redis_URL, db=0)
        self.__stages = redis.from_url(redis_URL, db=1)

    def has_user(self, user_id) -> bool:
        return bool(self.__places.smembers(user_id)) and self.__stages.get(user_id) is not None

    def add_place(self, user_id, place: Place):
        self.__places.sadd(user_id, repr(place))

    def get_places(self, user_id) -> list:
        return [Place.from_string(place.decode("utf8"))
                for place in self.__places.smembers(user_id)]

    def remove_place(self, user_id, place: Place):
        return self.__places.srem(user_id, repr(place)) == 1

    def reset_user(self, user_id):
        self.__places.delete(user_id)
        self.__stages.delete(user_id)

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
