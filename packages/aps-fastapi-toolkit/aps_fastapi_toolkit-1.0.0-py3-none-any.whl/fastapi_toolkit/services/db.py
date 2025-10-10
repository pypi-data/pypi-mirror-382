from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from fastapi_toolkit.schemas.db import DBConfigs


class DatabaseService:
    """
    Database connection manager using SQLAlchemy.
    """

    def __init__(self, configs: DBConfigs, is_sqlite: bool = False):
        self._engine = None
        self._configs = configs
        self.__create_engine(is_sqlite)

        # create a configured "Session" class
        self._SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    def __create_engine(self, is_sqlite: bool):
        """
        Create a SQLAlchemy engine based on the provided configurations.
        """
        # SQLite does not support some pool settings,
        # so we skip them if using SQLite
        if is_sqlite:
            self._engine = create_engine(
                url=self._configs.db_uri,
            )
            return

        # Create the engine with the provided configurations
        self._engine = create_engine(
            url=self._configs.db_uri,
            pool_size=self._configs.pool_size,
            max_overflow=self._configs.max_overflow,
            pool_timeout=self._configs.pool_timeout,
            pool_recycle=self._configs.pool_recycle,
            **(self._configs.other_engine_configs or {})
        )

    def get_db_session(self):
        """
        Returns a new database session.
        """
        db = self._SessionLocal()
        try:
            yield db
        except SQLAlchemyError as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @property
    def engine(self):
        """
        Returns the database engine.
        """
        return self._engine
