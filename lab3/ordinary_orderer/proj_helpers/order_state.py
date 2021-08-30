from enum import Enum


class OrderState(Enum):
    FREE = 1
    TAKEN = 2
    READY = 3
    OK = 4
    ERROR = 0
