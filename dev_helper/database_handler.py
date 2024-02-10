import os
import sqlalchemy as _sa
import sqlalchemy.orm as _orm
import contextlib as _ctx
import threading as _threading
import configparser
from typing import Optional, Dict, List
import typing_extensions as _typing_extension


class DatabaseHandler:
    def __init__(
        self,
        config_file: str = ".db.conf",
        section: str = "test_database",
        use_context_manager: bool = True,
    ) -> None:
        """
        Initializes the DatabaseHandler.

        Args:
            config_file (str): The path to the configuration file.
            section (str): The section name in the configuration file.
            use_context_manager (bool): If True, the handler will
                                        be used as a context manager.
        """
        self.config_file: str = self.find_config_file(config_file)
        self.config: Optional[configparser.ConfigParser] = None
        self.section: str = section
        self.use_context_manager: bool = use_context_manager
        self.engine: Optional[_sa.engine.Engine] = None
        self.lock: _threading.Lock = _threading.Lock()

    def __enter__(self) -> _typing_extension.Self:
        """
        Enters a context managed block.

        Returns:
            DatabaseHandler: The instance of the DatabaseHandler.
        """
        if self.use_context_manager:
            self.connect()
            self.session = self.create_session()
            return self
        else:
            self.connect()
            return self.create_session()

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_value: Optional[BaseException],
        traceback: Optional[_sa.exc.DBAPIError],
    ) -> None:
        """
        Exits a context managed block.

        Args:
            exc_type: The type of exception.
            exc_value: The exception instance.
            traceback: The traceback object.
        """
        if not self.use_context_manager:
            try:
                self.rollback_and_close()
            finally:
                if self.engine:
                    try:
                        self.engine.dispose()
                    except Exception as dispose_error:
                        print(f"Error during engine dispose: {dispose_error}")

    def find_config_file(self, config_file: str) -> str:
        """
        Finds the configuration file in the child directories starting from the root.

        Args:
            config_file (str): The initial configuration file path.

        Returns:
            str: The absolute path to the configuration file.
        """
        root_dir: str = "/"  # Set the root directory to '/' for Unix-like systems
        for dirpath, dirnames, filenames in os.walk(root_dir):
            if config_file in filenames:
                return os.path.join(dirpath, config_file)

        raise FileNotFoundError(
            f"{config_file} not found in any child directory starting from the root."
        )

    def connect(self) -> None:
        """
        Connects to the database and creates an engine if
        not already connected.
        """
        if not self.engine:
            self.load_config()
            host: str = self.config.get(self.section, "host")
            port: str = self.config.get(self.section, "port")
            user: str = self.config.get(self.section, "user")
            password: str = self.config.get(
                self.section,
                "password",
                fallback="postgres",
            )
            database: str = self.config.get(
                self.section,
                "database",
                fallback="postgres",
            )

            connection_string: str = (
                f"postgresql+psycopg2://{user}:{password}@" f"{host}:{port}/{database}"
            )
            self.engine = _sa.create_engine(connection_string)

    def rollback_and_close(self) -> None:
        """
        Rolls back and closes the session if it exists.
        """
        if hasattr(self, "session") and self.session:
            try:
                self.session.rollback()
            except Exception as rollback_error:
                print(f"Error during rollback: {rollback_error}")

            try:
                self.session.close()
            except Exception as close_error:
                print(f"Error during Session close: {close_error}")

    @_ctx.contextmanager
    def get_session(self) -> _ctx.AbstractContextManager[_orm.Session]:
        """
        Context manager for acquiring and managing a database session.

        Yields:
            sqlalchemy.orm.Session: The database session.
        """
        self.connect()  # Connect before acquiring a session
        session: _orm.Session = self.create_session()
        try:
            yield session
            self.rollback_and_close()
        except Exception as e:
            session.rollback()
            raise e

    def create_session(self) -> _orm.Session:
        """
        Creates a new database session.

        Returns:
            sqlalchemy.orm.Session: The created session.
        """
        return _orm.Session(bind=self.engine)

    def execute_query(
        self, query: str, parameters: Optional[Dict[str, str]] = None
    ) -> List:
        """
        Executes a SQL query and returns the result.

        Args:
            query (str): The SQL query to be executed.
            parameters (dict): Optional parameters to be passed to the query.

        Returns:
            list: The result of the query.
        """
        with self.get_session() as session:
            result_proxy: _sa.engine.ResultProxy = session.execute(
                _sa.text(query), parameters
            )
            if result_proxy.returns_rows:
                result: List = result_proxy.fetchall()
                session.commit()
                return result
            else:
                return []

    def load_config(self) -> None:
        """
        Loads the configuration from the specified file.
        """
        if not self.config:
            self.config = configparser.ConfigParser()
            self.config.read(self.config_file)
            if not self.config.has_section(self.section):
                raise configparser.NoSectionError(
                    f"No section '{self.section}' in {self.config_file}"
                )
