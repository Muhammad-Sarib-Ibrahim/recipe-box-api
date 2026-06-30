from sqlmodel import SQLModel, create_engine, Session

# SQLite file will be created in the project root as recipes.db
DATABASE_URL = "sqlite:///./recipes.db"

# connect_args is SQLite-specific: by default SQLite only allows one thread
# to talk to a connection. FastAPI can use multiple threads, so we relax that.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def create_db_and_tables():
    """Called once on startup to create tables if they don't exist yet."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    A FastAPI 'dependency'. Think of this like a context manager you'd use
    with `with open(...) as f:` in Python — it hands FastAPI a session,
    and closes it automatically when the request is done.
    """
    with Session(engine) as session:
        yield session
