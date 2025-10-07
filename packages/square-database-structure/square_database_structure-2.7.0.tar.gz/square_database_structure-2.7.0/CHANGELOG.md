# changelog

> ## 📌 note on versioning
> this module is planned to deviate slightly from SemVer.
> - **Major.x** and **x.Minor.x** increments → changes in application logic
> - **x.x.Patch** increments → changes in database data or structure

## v2.7.0

- remove setup.py and switch to pyproject.toml.

## v2.6.0

- docs
    - split changelog into a new file.
    - update README.
- dependencies
    - move pytest to extras_require.

## v2.5.9

- square
    - public
        - update TestEnumEnum.

## v2.5.8

- square
    - public
        - add more datatypes / columns in test table.
        - in test table convert test_text to nullable.

## v2.5.7

- square
    - authentication
        - make user_verification_code_expires_at nullable in UserVerificationCode table.

## v2.5.6

- square
    - authentication
        - add user_profile_phone_number_country_code in UserProfile table.
        - update unique constraint for phone number to account for user_profile_phone_number_country_code.

## v2.5.5

- square
    - email
        - fix schema name import.

## v2.5.4

- square
    - authentication
        - add UserVerificationCode.
        - add user_profile_email_verified in UserProfile table.
        - add VerificationCodeTypeEnum.
        - add AuthProviderEnum.
        - add UserAuthProvider.
        - move username from UserProfile to User.
    - email
        - new schema.
        - add EmailLog table.
        - add EmailTypeEnum.
        - add EmailStatusEnum.

## v2.5.3

- square
    - public
        - make test_text unique.

## v2.5.2

- square
    - authentication
        - remove user_status enum and column from User.
        - add RecoveryMethodEnum.
        - add UserRecoveryMethod table.

## v2.5.1

- square
    - file_storage
        - remove file_is_deleted and file_date_deleted from File table.

## v2.5.0

- testing
    - remove conftest file and all fixtures.
    - remove test_create_database_and_tables.
    - modify pytest workflow.
    - rename test file.

## v2.4.0

- testing
    - add fixture_create_database_and_tables for cleanup.

## v2.3.1

- square
    - authentication
        - remove user_credential_username from UserCredential table.
        - add UserProfile table.

## v2.3.0

- remove hardcoded testing database creds from pytest.

## v2.2.0

- add test_create_database_and_tables.

## v2.1.0

- add testing framework.

## v2.0.0

- replace force_recreate_tables optional param to drop_if_exists.

## v1.4.0

- add force_recreate_tables optional param to create_database_and_tables.

## v1.3.4

- remove app raspi_home inside square->public->app.
- remove app_id column from square->greeting->greeting.

## v1.3.3

- add new app raspi_home inside square->public->app.
- add new schema square->greeting with 1 table Greeting.

## v1.3.2

- update to versioning plan.
- add test app in square->public->app.

## v1.3.1

- update license in setup.py.

## v1.3.0

- add support for stored procedures and functions.

## v1.2.0

- move data to separate file for each schema.
- add enums file for each schema.

## v1.1.0

- add database, schema and table creation logic (from square database) (removed logs).

## v1.0.3

- change structure of square->authentication->UserApp and square->authentication->UserSession (due to complications with
  Composite Key).
- change default data in square->public->app.

## v1.0.2

- replace file_purpose with app_id in file_storage.

## v1.0.1

- add main.py file to have explicit mapping and ordering for schemas to be created.
- move database and schema names to `__init__.py`.
- add app table in public, change user, remove profile and add user app and remove enums.

## v1.0.0

- initial commit.
