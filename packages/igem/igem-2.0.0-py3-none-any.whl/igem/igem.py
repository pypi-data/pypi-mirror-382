# import os
from igem.db.database import Database
from igem.core.settings_manager import SettingsManager
from igem.utils.logger import Logger

# from igem.etl.etl_manager import ETLManager
# from igem.etl.conflict_manager import ConflictManager


class IGEM:
    def __init__(self, db_uri: str = None):
        self.logger = Logger(log_level="DEBUG")
        self.db_uri = db_uri
        self.db = None

        if self.db_uri:
            self.connect_db()

    @property
    def settings(self):
        if not self.db:
            msn = "You must connect to a database first."
            self.logger.log(msn, "INFO")
            raise RuntimeError(msn)
        if not hasattr(self, "_settings"):
            msn = "⚙️ Initializing settings..."
            self.logger.log(msn, "INFO")
            # self._settings = SettingsManager(self.igem.db.session)
            with self.db.get_session() as session:
                self._settings = SettingsManager(session)
        return self._settings

    def create_new_project(self, db_uri: str, overwrite=False):
        """Create a new igem project database and connect to it."""
        self.logger.log(f"Creating igem database at {db_uri}", "INFO")
        self._create_db(db_uri=db_uri, overwrite=overwrite)
        # self.connect_db(db_uri)
        self.logger.log(f"igem database ready at {db_uri}", "INFO")

    def _create_db(self, db_uri: str = None, overwrite=False):
        if db_uri:
            self.db_uri = db_uri
        if not self.db_uri:
            msn = "Database URI must be set before creating the database."
            self.logger.log(msn, "ERROR")
            raise ValueError(msn)
        self.db = Database()  # Do not pass db_uri here
        self.db.db_uri = self.db_uri
        return self.db.create_db(overwrite=overwrite)

    def connect_db(self, new_uri: str = None):
        if new_uri:
            self.db_uri = new_uri
        self.db = Database(self.db_uri)

    def __repr__(self):
        return f"<igem(db_uri={self.db_uri})>"
