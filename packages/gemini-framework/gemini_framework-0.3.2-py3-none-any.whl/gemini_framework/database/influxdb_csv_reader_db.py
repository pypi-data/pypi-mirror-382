"""Reader to import data from CSV into the internal InfluxDB store."""

from gemini_framework.abstract.database_reader_abstract import DatabaseReaderAbstract
from gemini_framework.database.connector.csv_driver import CSVDriver


class InfluxdbCSVReaderDB(DatabaseReaderAbstract):
    """Synchronize CSV data into InfluxDB for a given category."""

    def __init__(self, category):
        """Initialize CSV database reader."""
        super().__init__()
        self.category = category
        self.external_db_driver = CSVDriver()

    def set_external_db_parameters(self):
        """Set external CSV database parameters."""
        self.external_db_driver.update_parameters({'url': ''})
