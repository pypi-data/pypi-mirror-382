from psycopg2.errors import DuplicateDatabase
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from square_database_structure.main import global_list_create


def create_database_and_tables(
    db_username: str,
    db_password: str,
    db_ip: str,
    db_port: int,
    drop_if_exists: bool = False,
) -> None:
    try:
        local_list_create = global_list_create

        for local_dict_database in local_list_create:
            local_str_database_name = local_dict_database["database"]
            local_str_postgres_url = (
                f"postgresql://{db_username}:{db_password}@" f"{db_ip}:{str(db_port)}/"
            )
            postgres_engine = create_engine(local_str_postgres_url)
            # Create database if not exists
            try:
                with postgres_engine.connect() as postgres_connection:
                    postgres_connection.execute(text("commit"))
                    postgres_connection.execute(
                        text(f"CREATE DATABASE {local_str_database_name}")
                    )
            except Exception as e:
                if isinstance(getattr(e, "orig"), DuplicateDatabase):
                    if drop_if_exists:
                        with postgres_engine.connect() as postgres_connection:
                            postgres_connection.execute(text("commit"))
                            postgres_connection.execute(
                                text(
                                    f"DROP DATABASE {local_str_database_name} WITH (FORCE)"
                                )
                            )
                            postgres_connection.execute(
                                text(f"CREATE DATABASE {local_str_database_name}")
                            )
                else:
                    raise
            # ===========================================
            local_str_database_url = (
                f"postgresql://{db_username}:{db_password}@"
                f"{db_ip}:{str(db_port)}/{local_str_database_name}"
            )
            database_engine = create_engine(local_str_database_url)
            with database_engine.connect() as database_connection:
                for local_dict_schema in local_dict_database["schemas"]:
                    local_str_schema_name = local_dict_schema["schema"]
                    # Create schema if not exists
                    if not database_engine.dialect.has_schema(
                        database_connection, local_str_schema_name
                    ):
                        database_connection.execute(text("commit"))
                        database_connection.execute(
                            text(f"CREATE SCHEMA {local_str_schema_name}")
                        )
                    else:
                        pass
                    # ===========================================
                    database_connection.execute(
                        text(f"SET search_path TO {local_str_schema_name}")
                    )

                    inspector = inspect(database_engine)
                    existing_table_names = inspector.get_table_names(
                        schema=local_str_schema_name
                    )

                    base = local_dict_schema["base"]
                    # Create tables if not exists
                    base.metadata.create_all(database_engine)
                    # ===========================================
                    data_to_insert = local_dict_schema["data_to_insert"]
                    local_object_session = sessionmaker(bind=database_engine)
                    session = local_object_session()
                    filtered_data_to_insert = [
                        x
                        for x in data_to_insert
                        if x.__tablename__ not in existing_table_names
                    ]
                    # insert data for newly created tables
                    try:
                        session.add_all(filtered_data_to_insert)
                        # ===========================================
                        session.commit()
                        session.close()
                    except Exception:
                        session.rollback()
                        session.close()
                        raise
                    # create stored procedures
                    stored_procedures_and_functions = local_dict_schema[
                        "stored_procedures_and_functions"
                    ]
                    for (
                        stored_procedures_and_function
                    ) in stored_procedures_and_functions:
                        database_connection.execute(
                            text(stored_procedures_and_function)
                        )
    except Exception:
        raise
