import hashlib
import os
import pathlib
import time

import requests

from lib.database.database_manager import DatabaseManager
from lib.util.logger import ServerLogger


class DatasetUpdater:
    """ Class responsible for updating the database

    This class makes it possible to update the database. Once it's run, it'll check whether the
    necessary data files are already stored locally. If this is not the case, it will be downloaded from Github.
    If it already exists, it will check whether the file is up-to-date, and if not it will update redownload the
    files accordingly.
    """

    def __init__(self):
        self.db_manager = DatabaseManager()

        self.tracked_files = [
            {
                "name": "vaccinations",
                "url": "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv",
                "local_path": pathlib.Path(os.environ.get("COVBOT_VACCINATIONS_PATH")),
                "on_update": self.db_manager.update_vaccinations
            },
            {
                "name": "cases",
                "url": "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/jhu/new_cases.csv",
                "local_path": pathlib.Path(os.environ.get("COVBOT_CASES_PATH")),
                "on_update": self.db_manager.update_covid_cases
            }
        ]
        self.logger = ServerLogger(__name__)

    def start(self):
        """Starts the database updater."""
        self.logger.info("Successfully started the database updater.")
        self._perform_updates()

    def _perform_updates(self):
        """Downloads the data files from Github in case they have been updated and updates the database."""
        for tracked_file in self.tracked_files:
            if not tracked_file["local_path"].exists():
                self.logger.info(f"Datafile with new {tracked_file['name']} does not exist.")
                self._download_file(tracked_file)
            else:
                # Check if the file was updated
                self.logger.debug(f"File for {tracked_file['name']} "
                                  f"already exists. Checking whether the file has changed...")
                response = requests.get(tracked_file["url"])

                with open(tracked_file["local_path"], "rb") as file:
                    content = file.read()

                    if hashlib.sha256(response.content).digest() == hashlib.sha256(content).digest():
                        self.logger.info(f"{tracked_file['name']} data file hasn't been updated.")
                    else:
                        self._download_file(tracked_file)

    def _download_file(self, tracked_file: dict):
        """Downloads the data files from Github."""
        self.logger.info(f"Downloading the {tracked_file['name']} data file...")
        response = requests.get(tracked_file["url"])
        self.logger.info(
            f"Download of {tracked_file['name']} data file was successful! Saving the file and updating...")

        with open(tracked_file["local_path"], 'wb+') as file:
            file.write(response.content)
        tracked_file["on_update"]()


if __name__ == '__main__':
    # Searches for updates every two hours.
    updater = DatasetUpdater()
    updater.start()
