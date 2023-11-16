from enum import Enum


class Misc(str, Enum):
    GET_ANNOUNCEMENT = "/v5/announcements/index"

    def __str__(self) -> str:
        return self.value
