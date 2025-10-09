"""Build a Plant from project configuration."""

import logging
import os
import json

from gemini_framework.framework.plant import Plant
from gemini_framework.database.influxdb_aveva_reader_db import InfluxdbAvevaReaderDB
from gemini_framework.database.influxdb_osisoftpi_reader_db import InfluxdbOsisoftPIReaderDB
from gemini_framework.database.influxdb_csv_reader_db import InfluxdbCSVReaderDB
from gemini_framework.modules.esp.unit import ESPUnit
from gemini_framework.modules.productionwell.unit import ProductionWellUnit
from gemini_framework.modules.injectionwell.unit import InjectionWellUnit
from gemini_framework.modules.injectionpump.unit import InjectionPumpUnit
from gemini_framework.modules.degasser.unit import DegasserUnit
from gemini_framework.modules.filter.unit import FilterUnit
from gemini_framework.modules.heatexchanger.unit import HeatExchangerUnit
from gemini_framework.modules.reservoir.unit import ReservoirUnit
from gemini_framework.modules.boosterpump.unit import BoosterPumpUnit
from gemini_framework.modules.gasboiler.unit import GasBoilerUnit

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


def setup(project_path, plant_name):
    """Set up the plant.

    :param str project_path: location of the project folder.
    :param str plant_name: the plant name or location name.
    """
    logger.info('Boot application ' + plant_name)

    plant = Plant()
    plant.project_path = project_path
    plant.name = plant_name

    project_folder = os.path.join(plant.project_path, plant.name)
    with open(os.path.join(project_folder, 'plant.conf'), 'r') as jsonfile:
        cfg = json.load(jsonfile)
        plant.update_parameters(cfg)

    with open(os.path.join(project_folder, 'diagram.json'), 'r') as jsonfile:
        plant.diagram = json.load(jsonfile)

    plant = boot_unit(plant)
    plant = boot_database(plant)

    return plant


def boot_unit(plant):
    """Boot unit in the plant."""
    logger.info('Boot Unit Plant')

    project_folder = os.path.join(plant.project_path, plant.name)
    for file in os.listdir(project_folder):
        if file.endswith('.param'):
            with open(os.path.join(project_folder, file), 'r') as jsonfile:
                unitfile = json.load(jsonfile)
                unit = []
                if unitfile['type'] == 'esp':
                    unit = ESPUnit(unitfile['id'], unitfile['name'], plant)
                elif unitfile['type'] == 'injection_pump':
                    unit = InjectionPumpUnit(unitfile['id'], unitfile['name'], plant)
                elif unitfile['type'] == 'production_well':
                    unit = ProductionWellUnit(unitfile['id'], unitfile['name'], plant)
                elif unitfile['type'] == 'injection_well':
                    unit = InjectionWellUnit(unitfile['id'], unitfile['name'], plant)
                elif unitfile['type'] == 'degasser':
                    unit = DegasserUnit(unitfile['id'], unitfile['name'], plant)
                elif unitfile['type'] == 'heat_exchanger':
                    unit = HeatExchangerUnit(unitfile['id'], unitfile['name'], plant)
                elif unitfile['type'] == 'filter':
                    unit = FilterUnit(unitfile['id'], unitfile['name'], plant)
                elif unitfile['type'] == 'reservoir':
                    unit = ReservoirUnit(unitfile['id'], unitfile['name'], plant)
                elif unitfile['type'] == 'booster_pump':
                    unit = BoosterPumpUnit(unitfile['id'], unitfile['name'], plant)
                elif unitfile['type'] == 'gas_boiler':
                    unit = GasBoilerUnit(unitfile['id'], unitfile['name'], plant)
                else:
                    logger.error(
                        'UNIT ' + unitfile['type'] + ' not yet implemented')

                unit.set_parameters(unitfile['parameters'])
                unit.set_tagnames(unitfile['tagnames'])

                plant.add_unit(unit)

    plant.connect_unit()

    plant.link_unit()

    return plant


def boot_database(plant):
    """Start up the boot database."""
    logger.info('Boot Database')
    # add measured database
    if plant.parameters['database']['external_database'] == 'avevadb':
        meas_database = InfluxdbAvevaReaderDB('measured')
    elif plant.parameters['database']['external_database'] == 'pisystem':
        meas_database = InfluxdbOsisoftPIReaderDB('measured')
    elif plant.parameters['database']['external_database'] == 'csv':
        meas_database = InfluxdbCSVReaderDB('measured')
    else:
        return plant

    plant.add_database(meas_database)
    plant.register_tags()
    plant.connect_database()

    return plant
