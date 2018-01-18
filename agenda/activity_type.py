from enum import Enum

class ActivityType(Enum):
    INTERN = 0
    EXTERN = 1

    def succ(self):
        v = self.value+1
        if v > 1:
            raise ValueError('Enumeration ended')
        return ActivityType(v)

    def pred(self):
        v = self.value-1
        if v < 0:
            raise ValueError('Enumeration ended')
        return ActivityType(v)