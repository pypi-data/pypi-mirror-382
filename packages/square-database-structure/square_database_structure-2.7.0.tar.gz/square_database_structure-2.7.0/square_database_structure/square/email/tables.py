from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    DateTime,
    String,
    ForeignKey,
    Enum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from square_database_structure.square.authentication.tables import User
from square_database_structure.square.email import global_string_schema_name
from square_database_structure.square.email.enums import EmailTypeEnum, EmailStatusEnum

Base = declarative_base(metadata=MetaData(schema=global_string_schema_name))


class EmailLog(Base):
    __tablename__ = "email_log"

    email_log_id = Column(
        Integer, primary_key=True, unique=True, nullable=False, autoincrement=True
    )
    user_id = Column(
        UUID,
        ForeignKey(User.user_id, ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    recipient_email = Column(
        String,
        nullable=False,
        index=True,
    )
    email_type = Column(
        Enum(EmailTypeEnum, schema=global_string_schema_name),
        nullable=False,
    )
    sent_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    status = Column(
        Enum(EmailStatusEnum, schema=global_string_schema_name),
        nullable=False,
    )

    third_party_message_id = Column(
        String,
        nullable=True,
        unique=True,
        index=True,
    )
