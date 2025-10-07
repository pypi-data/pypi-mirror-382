from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    DateTime,
    text,
    String,
    ForeignKey,
    Enum,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from square_database_structure.square.authentication import global_string_schema_name
from square_database_structure.square.authentication.enums import (
    RecoveryMethodEnum,
    VerificationCodeTypeEnum,
    AuthProviderEnum,
)
from square_database_structure.square.file_storage.tables import File
from square_database_structure.square.public.tables import App

Base = declarative_base(metadata=MetaData(schema=global_string_schema_name))


class User(Base):
    __tablename__ = "user"

    user_id = Column(
        UUID,
        primary_key=True,
        nullable=False,
        unique=True,
        server_default=text("gen_random_uuid()"),
    )
    user_username = Column(String, nullable=False, unique=True, index=True)


class UserAuthProvider(Base):
    __tablename__ = "user_auth_provider"

    user_auth_provider_id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id = Column(
        UUID,
        ForeignKey(User.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    auth_provider = Column(
        Enum(AuthProviderEnum, schema=global_string_schema_name),
        nullable=False,
    )
    auth_provider_user_id = Column(String, nullable=True)
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "auth_provider",
            name="uq_user_id_auth_provider",
        ),
    )


class UserCredential(Base):
    __tablename__ = "user_credential"

    user_credential_id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    user_id = Column(
        UUID,
        ForeignKey(User.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    user_credential_hashed_password = Column(String, nullable=False)


class UserApp(Base):
    __tablename__ = "user_app"

    user_id = Column(
        UUID,
        ForeignKey(User.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    app_id = Column(
        Integer,
        ForeignKey(App.app_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        primary_key=True,
    )


class UserSession(Base):
    __tablename__ = "user_session"

    user_session_id = Column(
        Integer, primary_key=True, unique=True, nullable=False, autoincrement=True
    )
    user_id = Column(
        UUID,
        ForeignKey(User.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    app_id = Column(
        Integer,
        ForeignKey(App.app_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user_session_refresh_token = Column(
        String,
        nullable=False,
        unique=True,
    )
    user_session_expiry_time = Column(DateTime(timezone=True), nullable=False)


class UserProfile(Base):
    __tablename__ = "user_profile"

    user_profile_id = Column(
        Integer, primary_key=True, unique=True, nullable=False, autoincrement=True
    )
    user_id = Column(
        UUID,
        ForeignKey(User.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    user_profile_photo_storage_token = Column(
        String,
        ForeignKey(File.file_storage_token, ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        unique=True,
        default=None,
    )
    user_profile_email = Column(
        String,
        nullable=True,
        unique=True,
        default=None,
    )
    user_profile_email_verified = Column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    user_profile_phone_number_country_code = Column(
        String,
        nullable=True,
        default=None,
    )
    user_profile_phone_number = Column(
        String,
        nullable=True,
        default=None,
    )
    user_profile_first_name = Column(
        String,
        nullable=True,
        default=None,
    )
    user_profile_last_name = Column(
        String,
        nullable=True,
        default=None,
    )
    __table_args__ = (
        UniqueConstraint(
            "user_profile_phone_number_country_code",
            "user_profile_phone_number",
            name="uq_user_profile_phone_number",
        ),
    )


class UserRecoveryMethod(Base):
    __tablename__ = "user_recovery_method"

    user_recovery_method_id = Column(
        Integer, primary_key=True, unique=True, nullable=False, autoincrement=True
    )
    user_id = Column(
        UUID,
        ForeignKey(User.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user_recovery_method_name = Column(
        Enum(RecoveryMethodEnum, schema=global_string_schema_name),
        nullable=False,
    )
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "user_recovery_method_name",
            name="uq_user_id_user_recovery_method",
        ),
    )


class UserVerificationCode(Base):
    __tablename__ = "user_verification_code"

    user_verification_code_id = Column(
        Integer, primary_key=True, unique=True, nullable=False, autoincrement=True
    )
    user_id = Column(
        UUID,
        ForeignKey(User.user_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    user_verification_code_type = Column(
        Enum(VerificationCodeTypeEnum, schema=global_string_schema_name),
        nullable=False,
    )
    user_verification_code_hash = Column(
        String,
        unique=True,
        nullable=False,
    )
    user_verification_code_created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    user_verification_code_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    user_verification_code_used_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )
