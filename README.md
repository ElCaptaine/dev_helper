# dev_helper
`dev_helpers` is a Python package designed to simplify the development process by providing a collection of essential development tools, all conveniently stored in one place. The package aims to enhance the developer experience, making it easier to perform common tasks. Key components of this package include the DatabaseHandler, for managing database connections and operations, and the Logger, a tool for enhanced logging management.

## Installation

If the package is published, do a normal pip installation (as shown below)
```bash
pip install pj_dev_helpers
```
Till it is released and published in PIPY, the installation steps are the following:
1. Clone the project: 
```bash 
git clone https://gitlab.com/charger-s/pj_dev_helper.git
```
1. Go into the directory:
```bash
cd path/to/folder/of/pj_dev_helper
```
1. Either do in the root dir of the project:
    - `pip install -e .`
    - `python setup.py install`

That's it. If you want to also contribute please also install the test requirements
(`pip install -e .[tests]`)
    

## Components

### DatabaseHandler

The `DatabaseHandler` is a crucial component of `pj_dev_helpers`, designed to streamline database-related tasks. 
It simplifies database connections, session management, and query execution. 
For detailed information on how to use the `DatabaseHandler`,
refer to the [documentation](documentation/database_handler.md).

```python
from pj_dev_helpers import DatabaseHandler

# Example usage
db_handler = DatabaseHandler(config_file=".db.conf", section="test_database")
with db_handler as session:
    results = session.execute_query("SELECT * FROM your_table")
    print(results)
```

## Testing locally

If you want to test locally, please make sure that Docker is installed, and ensure that the .db.conf file has an entry liketest_pj_helper_database.

Also, make sure that the PostgreSQL container is set up and running. For example:

```bash
docker run --name postgres-container \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_password \
  -p 5432:5432 \
  -d postgres:latest
```
## Contributing

If you would like to contribute to `dev_helpers` or report issues, please check the [contribution guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The `dev_helpers` package is built upon the collaborative efforts of the developer community.
- Special thanks to the contributors for their valuable input.

Happy coding with `dev_helpers`! 🚀
