from sqlalchemy import text as _sa_text
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from configparser import NoSectionError
from dev_helper.database_handler import DatabaseHandler


def test_find_config_file():
    """
    Test if the find_config_file method correctly constructs the path to the configuration file.
    """
    config_file_path = DatabaseHandler(section="test_database").find_config_file(
        ".db.conf"
    )
    assert (
        config_file_path == "/builds/charger-s/pj_dev_helper/.db.conf"
        or f"/.db.conf" in config_file_path
    )


def test_connect():
    """
    Test if the connect method establishes a connection and creates an engine.
    """
    db = DatabaseHandler(section="test_pj_helper_database")
    db.connect()
    assert db.engine is not None


def test_create_session():
    """
    Test if the create_session method creates a new database session.
    """
    db = DatabaseHandler(section="test_pj_helper_database")
    db.connect()
    session = db.create_session()
    assert isinstance(session, Session)
    assert session.bind is db.engine


def test_execute_create_table():
    """
    Test if the execute_query method correctly executes a SQL query and returns the result.
    """
    create_table_sql = _sa_text("""
    CREATE TABLE IF NOT EXISTS test_table (
    id SERIAL PRIMARY KEY,
    a INTEGER,
    b INTEGER
    );
    """)
    check_query = _sa_text ("""
                SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :x);
    """)
    param = {'x': 'test_table'}

    handler = DatabaseHandler(section="test_pj_helper_database")
    with handler.get_session() as session:
        session.execute(create_table_sql)
        session.commit()
        result = session.execute(check_query, param).scalar()
        assert result is True
