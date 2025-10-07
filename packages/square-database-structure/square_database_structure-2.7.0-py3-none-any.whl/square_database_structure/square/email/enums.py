from enum import Enum


class EmailTypeEnum(Enum):
    VERIFY_EMAIL = "VERIFY_EMAIL"
    PASSWORD_RESET = "PASSWORD_RESET"


class EmailStatusEnum(Enum):
    SENT = "SENT"
    FAILED = "FAILED"
