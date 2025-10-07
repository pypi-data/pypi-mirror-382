from enum import Enum


class MotdLevel(str, Enum):
    ALERT = "alert"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
