import enum


class Role(enum.Enum):
    PLAYER = 0
    MASTER = 1

    @classmethod
    def is_valid(cls, n: int):
        return n in [member.value for member in cls]
