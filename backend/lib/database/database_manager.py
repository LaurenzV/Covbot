from pandas import DataFrame
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import DatabaseError

from lib.database.database_connection import DatabaseConnection
from lib.database.dataset_handler import DatasetHandler
from lib.database.entities import create_tables, Vaccination, Case, drop_tables
from lib.util.logger import ServerLogger


class DatabaseManager:
    """Class that provides helper methods to manage the Covbot database."""
    def __init__(self, db_name="covbot"):
        self.logger: ServerLogger = ServerLogger(__name__)
        self.connection: DatabaseConnection = DatabaseConnection()
        self.db_name: str = db_name
        self.engine: Engine = self.connection.create_engine(self.db_name)
        self.dataset_handler: DatasetHandler = DatasetHandler()

    def update_database(self) -> None:
        """Updates the data on COVID cases and vaccinations. The database already needs to exist."""
        self.logger.info("Updating the data in the database...")
        self.update_covid_cases()
        self.update_vaccinations()

    def update_covid_cases(self) -> None:
        """Updates the data on COVID cases. The database already needs to exist."""
        covid_cases: DataFrame = self.dataset_handler.load_covid_cases()
        db_connection: Connection = self.engine.connect()

        self.logger.info("Deleting previous covid cases entries...")
        drop_tables(self.engine, [Case.__table__])
        create_tables(self.engine, [Case.__table__])
        self.logger.info("Updating the daily detected covid cases...")
        covid_cases.to_sql(name="cases", con=db_connection, if_exists="append", index=False)
        self.logger.info("Daily detected covid cases were updated.")

    def update_vaccinations(self) -> None:
        """Updates the data on vaccinations. The database already needs to exist."""
        vaccinations: DataFrame = self.dataset_handler.load_vaccinations()
        db_connection: Connection = self.engine.connect()

        self.logger.info("Deleting previous vaccinations entries...")
        drop_tables(self.engine, [Vaccination.__table__])
        create_tables(self.engine, [Vaccination.__table__])
        self.logger.info("Updating daily vaccinations...")
        vaccinations.to_sql(name="vaccinations", con=db_connection, if_exists="append", index=False)
        self.logger.info("Daily vaccinations were updated.")

    def create_tables(self) -> None:
        """Creates all necessary tables."""
        create_tables(self.engine)

    def drop_tables(self) -> None:
        """Drops all tables."""
        drop_tables(self.engine)
