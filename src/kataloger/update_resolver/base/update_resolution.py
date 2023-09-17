from enum import IntEnum, unique


@unique
class UpdateResolution(IntEnum):
    CANT_RESOLVE = 1
    UPDATE_FOUND = 2
    NO_UPDATES = 3
