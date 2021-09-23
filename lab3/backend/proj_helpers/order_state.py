from enum import Enum


class OrderState(Enum):
    FREE = 'FREE'
    TAKEN = 'TAKEN'
    READY = 'READY'
    OK = 'OK'

    def __str__(self):
        return self._value_
