# DatabaseHandler

The `DatabaseHandler` is a Python class designed to simplify database operations and enhance the development process by encapsulating database connection logic. The goal is to provide a common tool that makes connecting to databases easier and promotes cleaner code through the use of context managers.

## Usage

### Initialization

```python
from DatabaseHandler import DatabaseHandler

# Create an instance of DatabaseHandler with optional parameters
db_handler = DatabaseHandler(
    config_file=".db.conf",
    section="test_database",
    use_context_manager=True
)
```

### Context Management

The `DatabaseHandler` can be used as a context manager for convenient resource management:

```python
with db_handler as session:
    # Your database operations using the session
    results = session.execute_query("SELECT * FROM your_table")
    print(results)
# The session is automatically committed and closed upon exiting the block
```

Alternatively, you can manually manage the session if the context manager is not desired:

```python
db_handler.connect()
session = db_handler.create_session()
try:
    # Your database operations using the session
    results = db_handler.execute_query("SELECT * FROM your_table")
    print(results)
finally:
    db_handler.rollback_and_close()
```

### Configuration

The configuration for connecting to the database is loaded from a specified configuration file (default: `.db.conf`) and a section within that file (default: `test_database`). Ensure that your configuration file has the necessary information:

```ini
[test_database]
host = your_database_host
port = your_database_port
user = your_database_user
password = your_database_password
database = your_database_name
```

### Methods

#### `execute_query(query: str, parameters: Optional[Dict[str, str]] = None) -> List`

Executes a SQL query and returns the result.

- `query`: The SQL query to be executed.
- `parameters` (optional): Parameters to be passed to the query.

```python
results = db_handler.execute_query("SELECT * FROM your_table")
print(results)
```

#### `load_config() -> None`

Loads the configuration from the specified file. Raises `configparser.NoSectionError` if the specified section is not found in the configuration file.

```python
db_handler.load_config()
```

#### `get_session() -> _ctx.AbstractContextManager[_orm.Session]`

A context manager for acquiring and managing a database session. Useful for scenarios where you need a temporary session for specific operations.

```python
handler = DatabaseHandler(section="test_database")
with handler.get_session() as session:
    session.execute(create_table_sql)
    session.commit()
```

## Configuration File

Ensure your configuration file (default: `.db.conf`) follows the INI format and includes the required database connection information in the specified section.

```ini
[test_database]
host = your_database_host
port = your_database_port
user = your_database_user
password = your_database_password
database = your_database_name
```

## Note

- This code assumes a PostgreSQL database. Modify the connection string in the `connect` method if using a different database.
- Proper exception handling should be implemented in a production environment.
- Ensure that the necessary dependencies (`sqlalchemy` and `typing_extensions`) are installed using `pip install sqlalchemy typing-extensions`.
- Handle sensitive information, such as database passwords, securely in a production setting.
