from enum import IntEnum


class Stage(IntEnum):
    START = 0,
    ADDING_PLACE_NAME = 1,
    ADDING_PLACE_LOCATION = 2,
    ASKING_FOR_RESET = 3,
    SEARCHING_PLACE_TO_VISIT = 4,
    MARKING_PLACE_AS_VISITED = 5
