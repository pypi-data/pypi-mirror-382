from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    JSON,
    LargeBinary,
    Enum,
    MetaData,
)
from sqlalchemy.orm import declarative_base

from square_database_structure.square.public import global_string_schema_name
from square_database_structure.square.public.enums import TestEnumEnum

Base = declarative_base(metadata=MetaData(schema=global_string_schema_name))


class Test(Base):
    __tablename__ = "test"

    test_id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    test_text = Column(String, nullable=True, unique=True)
    test_datetime = Column(DateTime, nullable=True)
    test_bool = Column(Boolean, nullable=True)
    test_enum_enum = Column(Enum(TestEnumEnum), nullable=True)
    test_float = Column(Float, nullable=True)
    test_json = Column(JSON, nullable=True)
    test_blob = Column(LargeBinary, nullable=True)


class App(Base):
    __tablename__ = "app"

    app_id = Column(
        Integer, primary_key=True, nullable=False, unique=True, autoincrement=True
    )
    app_name = Column(String, nullable=False, unique=True)
