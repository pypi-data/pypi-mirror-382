# square_database_structure

> 📌 versioning: see [CHANGELOG.md](./CHANGELOG.md).

## about

python module to define postgresql database schemas using sqlalchemy.

## goals

- clear database → schema → table hierarchy
- reusable (template) across multiple projects
- single source of truth for schema and data

## installation

```bash
pip install square_database_structure
```

## usage

this module organizes database schemas in a standardized folder structure where each top-level folder represents a
database, and subfolders within it represent schemas. all mandatory components, such as `__init__.py` and tables.py,
data.py, stored_procedures_and_functions need to follow this structure.

### folder structure

```
square_database_structure/
├───main.py                                       # global definition file (mandatory)
├───create_database.py                            # global database creation file (mandatory)
└───database1/                                    # each folder corresponds to a separate database
    ├───__init__.py                               # contains the global name for the database (mandatory)
    └───schema1/                                  # each subfolder corresponds to a schema within the database
        ├───__init__.py                           # contains the global name for the schema (mandatory)
        ├───data.py                               # contains the data for insertion for the schema (mandatory)
        ├───enums.py                              # defines enums to be used in the schema (optional)
        ├───tables.py                             # defines tables of the schema (mandatory)
        └───stored_procedures_and_functions/      # contains stored procedures and functions for the schema (mandatory)
            ├───__init__.py                       # contains logic to discover sql files (mandatory)
            └───function1.sql                      # function or stored procedure sql file (optional)
```

- top-level folders: represent individual databases (e.g., database1).
- subfolders: represent schemas within each database (e.g., public, schema1).
- mandatory files:
    - `__init__.py` (both at the database and schema level).
    - tables.py within each schema.
    - data.py within each schema.
    - stored_procedures_and_functions package within each schema.

### defining database and schema names in `__init__.py`

each database and schema folder must contain an `__init__.py` file where the database and schema names are defined
as global variables.

#### example for database:

```python
# database1/__init__.py

global_string_database_name = "database1"  # mandatory: database name
```

#### example for schema:

```python
# database1/schema1/__init__.py

global_string_schema_name = "schema1"  # mandatory: schema name
```

### defining tables in tables.py

each schema folder must contain a tables.py file where:

- you must declare a Base object tied to the schema.
- you can define table classes, extending the Base object.

#### example tables.py:

```python
# tables.py
from sqlalchemy import Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from square_database_structure.square.public import global_string_schema_name

# 1. mandatory: declare Base with metadata pointing to the schema

Base = declarative_base(metadata=MetaData(schema=global_string_schema_name))


# 2.optional: define table classes by extending Base

class App(Base):
    __tablename__ = 'app'


id = Column(Integer, primary_key=True)
app_name = Column(String, nullable=False)
```

### defining data in data.py

- you must declare a data_to_insert list to store optional data that may be inserted into the schema's tables.

```python
from square_database_structure.square.public.tables import App

# 1. mandatory: initialize a list for optional data insertion
data_to_insert = []
# optional: append data to be inserted into the table
data_to_insert.append(App(app_name="example_app"))
```

### defining function or stored procedure in stored_procedures_and_functions package

- paste this logic in the `__init__.py` of this package to discover all sql files.

```python
from pathlib import Path

directory = Path(__file__).parent
stored_procedures_and_functions = []

for file_path in directory.iterdir():
    if file_path.is_file() and file_path.suffix == ".sql":
        with file_path.open("r") as file:
            content = file.read()
            stored_procedures_and_functions.append(content)
```

- you can keep raw sql files each containing ideally 1 stored procedure or function.
- the name of the file should ideally correspond to the function / procedure name.
- this raw sql should be compatible with postgres database.

```sql
CREATE OR REPLACE FUNCTION add_user(
    p_username VARCHAR,
    p_email VARCHAR
) RETURNS TEXT AS $$
BEGIN
    -- Insert a new user into the users table
    INSERT INTO users (username, email)
    VALUES (p_username, p_email);

    -- Return a success message
    RETURN 'User added successfully!';
END;
$$ LANGUAGE plpgsql;

```

### centralized definitions in main.py

the main.py file is mandatory and contains a global list that maps databases to schemas and their corresponding table
definitions. this list is manually created by the user (for now).

#### example main.py:

```python
# main.py

from square_database_structure.square.public import global_string_schema_name as schema1_name
from square_database_structure.square.public.tables import Base as Schema1Base
from square_database_structure.square.public.data import data_to_insert as schema1_data
from square_database_structure.square.public.stored_procedures_and_functions import (
    stored_procedures_and_functions as schema1_stored_procedures_and_functions)
from square_database_structure.square import global_string_database_name as database1_name

# global list that maps databases and schemas

global_list_create = [
    {
        "database": database1_name,  # mandatory: database name
        "schemas": [
            {
                "schema": schema1_name,  # mandatory: schema name
                "base": Schema1Base,  # mandatory: base for this schema
                "data_to_insert": schema1_data,  # mandatory: data to insert (even if empty)
                "stored_procedures_and_functions": schema1_stored_procedures_and_functions,
                # mandatory: stored procedures and functions (even if empty)
            },
        ],
    }
]
```

this file centralizes the definition of each database and schema, including the associated Base and data_to_insert for
table definitions.

### creating tables

once you have defined your databases, schemas, and tables, you can create them in your PostgreSQL database by using the
`create_database_and_tables` function.

```python
from square_database_structure import create_database_and_tables

# define the database connection details
db_username = "your_username"
db_password = "your_password"
db_ip = "localhost"
db_port = 5432

# call the function to create the database and tables
create_database_and_tables(db_username, db_password, db_ip, db_port)
```

## env

- python>=3.12.0
- postgresql >= 13

> feedback is appreciated. thank you!