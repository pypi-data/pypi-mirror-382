"""Reader to import data from OSIsoft PI into the internal InfluxDB store."""

from gemini_framework.abstract.database_reader_abstract import DatabaseReaderAbstract
from gemini_framework.database.connector.osisoftpi_driver import OsisoftPIDriver


class InfluxdbOsisoftPIReaderDB(DatabaseReaderAbstract):
    """Synchronize OSIsoft PI data into InfluxDB for a given category."""

    def __init__(self, category):
        """Initialize OSIsoft PI database reader."""
        super().__init__()
        self.category = category
        self.external_db_driver = OsisoftPIDriver()

    def set_external_db_parameters(self):
        """Set external OSIsoft PI database parameters."""
        self.parameters['osisoftpi']['interval'] = self.delta_t

        self.external_db_driver.update_parameters(self.parameters['osisoftpi'])
