from enum import Enum


class SystemConfigurationMotdAdditionalPropertyLevel(str, Enum):
    ALERT = "alert"
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
