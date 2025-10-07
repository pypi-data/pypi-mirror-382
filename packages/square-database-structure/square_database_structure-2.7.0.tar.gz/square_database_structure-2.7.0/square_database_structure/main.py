from square_database_structure.square import (
    global_string_database_name as local_string_square_database_name,
)
from square_database_structure.square.authentication import (
    global_string_schema_name as local_string_square_authentication_schema_name,
)
from square_database_structure.square.authentication.data import (
    data_to_insert as local_list_square_authentication_data_to_insert,
)
from square_database_structure.square.authentication.stored_procedures_and_functions import (
    stored_procedures_and_functions as local_list_square_authentication_stored_procedures_and_functions,
)
from square_database_structure.square.authentication.tables import (
    Base as SquareAuthenticationBase,
)
from square_database_structure.square.email import (
    global_string_schema_name as local_string_square_email_schema_name,
)
from square_database_structure.square.email.data import (
    data_to_insert as local_list_square_email_data_to_insert,
)
from square_database_structure.square.email.stored_procedures_and_functions import (
    stored_procedures_and_functions as local_list_square_email_stored_procedures_and_functions,
)
from square_database_structure.square.email.tables import (
    Base as SquareEmailBase,
)
from square_database_structure.square.file_storage import (
    global_string_schema_name as local_string_square_file_storage_schema_name,
)
from square_database_structure.square.file_storage.data import (
    data_to_insert as local_list_square_file_storage_data_to_insert,
)
from square_database_structure.square.file_storage.stored_procedures_and_functions import (
    stored_procedures_and_functions as local_list_square_file_storage_stored_procedures_and_functions,
)
from square_database_structure.square.file_storage.tables import (
    Base as SquareFileStorageBase,
)
from square_database_structure.square.greeting import (
    global_string_schema_name as local_string_square_greeting_schema_name,
)
from square_database_structure.square.greeting.data import (
    data_to_insert as local_list_square_greeting_data_to_insert,
)
from square_database_structure.square.greeting.stored_procedures_and_functions import (
    stored_procedures_and_functions as local_list_square_greeting_stored_procedures_and_functions,
)
from square_database_structure.square.greeting.tables import (
    Base as SquareGreetingBase,
)
from square_database_structure.square.public import (
    global_string_schema_name as local_string_square_public_schema_name,
)
from square_database_structure.square.public.data import (
    data_to_insert as local_list_square_public_data_to_insert,
)
from square_database_structure.square.public.stored_procedures_and_functions import (
    stored_procedures_and_functions as local_list_square_public_stored_procedures_and_functions,
)
from square_database_structure.square.public.tables import (
    Base as SquarePublicBase,
)

global_list_create = [
    {
        "database": local_string_square_database_name,
        "schemas": [
            {
                "schema": local_string_square_public_schema_name,
                "base": SquarePublicBase,
                "data_to_insert": local_list_square_public_data_to_insert,
                "stored_procedures_and_functions": local_list_square_public_stored_procedures_and_functions,
            },
            {
                "schema": local_string_square_file_storage_schema_name,
                "base": SquareFileStorageBase,
                "data_to_insert": local_list_square_file_storage_data_to_insert,
                "stored_procedures_and_functions": local_list_square_file_storage_stored_procedures_and_functions,
            },
            {
                "schema": local_string_square_authentication_schema_name,
                "base": SquareAuthenticationBase,
                "data_to_insert": local_list_square_authentication_data_to_insert,
                "stored_procedures_and_functions": local_list_square_authentication_stored_procedures_and_functions,
            },
            {
                "schema": local_string_square_greeting_schema_name,
                "base": SquareGreetingBase,
                "data_to_insert": local_list_square_greeting_data_to_insert,
                "stored_procedures_and_functions": local_list_square_greeting_stored_procedures_and_functions,
            },
            {
                "schema": local_string_square_email_schema_name,
                "base": SquareEmailBase,
                "data_to_insert": local_list_square_email_data_to_insert,
                "stored_procedures_and_functions": local_list_square_email_stored_procedures_and_functions,
            },
        ],
    }
]
