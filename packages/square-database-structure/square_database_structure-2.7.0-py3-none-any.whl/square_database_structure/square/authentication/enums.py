from enum import Enum


class RecoveryMethodEnum(Enum):
    EMAIL = "EMAIL"
    BACKUP_CODE = "BACKUP_CODE"


class VerificationCodeTypeEnum(Enum):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION"
    EMAIL_RECOVERY = "EMAIL_RECOVERY"
    BACKUP_CODE_RECOVERY = "BACKUP_CODE_RECOVERY"


class AuthProviderEnum(Enum):
    SELF = "SELF"
    GOOGLE = "GOOGLE"
