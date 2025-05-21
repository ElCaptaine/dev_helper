# dev_helper
`dev_helpers` is a Python package designed to simplify the development process by providing a collection of essential development tools, all conveniently stored in one place. The package aims to enhance the developer experience, making it easier to perform common tasks. Key components of this package include the DatabaseHandler, for managing database connections and operations,.

## Installation

If the package is published, do a normal pip installation (as shown below)
```bash
pip install dev_helper
```
Till it is released and published in PIPY, the installation steps are the following:
1. Clone the project: 
```bash 
git clone https://github.com/ElCaptaine/dev_helper.git
```
1. Go into the directory:
```bash
cd path/to/folder/of/dev_helper
```
1. Either do in the root dir of the project:
    - `pip install -e .`
    - `python setup.py install`

That's it. If you want to also contribute please also install the test requirements
(`pip install -e .[tests]`)
    

## Components

### DatabaseHandler

The `DatabaseHandler` is a crucial component of `dev_helper`, designed to streamline database-related tasks. 
It simplifies database connections, session management, and query execution. 
For detailed information on how to use the `DatabaseHandler`,
refer to the [documentation](documentation/database_handler.md).

```python
from dev_helper import DatabaseHandler

# Example usage
db_handler = DatabaseHandler(config_file=".db.conf", section="test_database")
with db_handler as session:
    results = session.execute_query("SELECT * FROM your_table")
    print(results)
```

## Testing locally

If you want to test locally, please make sure that Docker is installed, and ensure that the .db.conf file has an entry like test_helper_database.

Also, make sure that the PostgreSQL container is set up and running. For example:

```bash
docker run --name postgres-container \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_password \
  -p 5432:5432 \
  -d postgres:latest
```

## Scripts

### database_visualizer
This guide introduces the Database Visualizer script, which provides a graphical representation of relationships between tables in a database.

#### What it Does

The Database Visualizer script:

1. Connects to the specified database.
2. Retrieves information about table relationships.
3. Generates a graph that visually represents these relationships.
4. Allows customization of graph layout and saving the graph image.

#### Usage

To use the Database Visualizer:

1. Run the script with Python.
2. Specify the database to visualize using the `--db_spec` option.
3. Optionally, provide additional arguments like `--path`, `--layout`, and `--show` for customization.

#### Example

```bash
python database_visualizer.py --db_spec my_database --path /path/to/save/graph --layout shell_layout --show
```

This command visualizes the relationships in the `my_database` database, saves the graph image to the specified path, uses the `shell_layout` for graph layout, and displays the graph plot.

#### Note

Ensure you have the necessary dependencies installed, and provide the appropriate database specification.

For detailed information and advanced usage, refer to the [documentation](documentation/database_visualizer.md).


## Contributing

If you would like to contribute to `dev_helpers` or report issues, please check the [contribution guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Still WIP
- The `dev_helpers` package is built upon the collaborative efforts of the developer community.
- Special thanks to the contributors for their valuable input.

Happy coding with `dev_helpers`! 🚀
