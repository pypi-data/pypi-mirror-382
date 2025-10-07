from sqlalchemy import (
    MetaData,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

from square_database_structure.square.authentication.tables import User
from square_database_structure.square.greeting import global_string_schema_name

Base = declarative_base(metadata=MetaData(schema=global_string_schema_name))


class Greeting(Base):
    __tablename__ = "greeting"

    greeting_id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    greeting_is_anonymous = Column(Boolean, nullable=False)
    greeting_anonymous_sender_name = Column(String)
    user_id = Column(
        UUID,
        ForeignKey(User.user_id, ondelete="CASCADE", onupdate="CASCADE"),
    )
    greeting_text = Column(String)
    greeting_datetime = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
