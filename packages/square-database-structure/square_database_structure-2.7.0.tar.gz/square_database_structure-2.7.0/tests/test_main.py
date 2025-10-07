from square_database_structure.main import global_list_create


def test_global_list_create():
    assert isinstance(global_list_create, list)
    for database in global_list_create:
        assert isinstance(database, dict)
        assert "database" in database
        assert isinstance(database["database"], str)
        assert "schemas" in database
        assert isinstance(database["schemas"], list)
        for schema in database["schemas"]:
            assert isinstance(schema, dict)
            assert "schema" in schema
            assert isinstance(schema["schema"], str)
            assert "base" in schema
            assert "data_to_insert" in schema
            assert isinstance(schema["data_to_insert"], list)
            assert "stored_procedures_and_functions" in schema
            assert isinstance(schema["stored_procedures_and_functions"], list)
