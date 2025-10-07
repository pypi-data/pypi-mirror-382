from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    MetaData,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from square_database_structure.square.file_storage import global_string_schema_name
from square_database_structure.square.public.tables import App

Base = declarative_base(metadata=MetaData(schema=global_string_schema_name))


class File(Base):
    __tablename__ = "file"

    file_id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    file_name_with_extension = Column(String, nullable=False)
    file_content_type = Column(String, nullable=False, index=True)
    file_date_created = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    file_last_modified = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    file_system_file_name_with_extension = Column(String, nullable=False)
    file_system_relative_path = Column(String, server_default="", nullable=False)
    file_storage_token = Column(String, nullable=False, unique=True, index=True)
    app_id = Column(
        Integer,
        ForeignKey(App.app_id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
