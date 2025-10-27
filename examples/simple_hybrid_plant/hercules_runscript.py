import os
import shutil
import sys

from hercules.emulator import Emulator
from hercules.hybrid_plant import HybridPlant
from hercules.utilities import load_hercules_input, setup_logging
from hercules.utilities_examples import ensure_example_inputs_exist
from whoc.controllers import (
    BatteryPassthroughController,
    HybridSupervisoryControllerBaseline,
    SolarPassthroughController,
    WindFarmPowerTrackingController,
)
from whoc.interfaces import HerculesV2Interface

# If the output folder exists, delete it
if os.path.exists("outputs"):
    shutil.rmtree("outputs")
os.makedirs("outputs")

# Ensure example inputs exist
ensure_example_inputs_exist()

# Get the logger
logger = setup_logging()

# If more than one argument is provided raise and error
if len(sys.argv) > 2:
    raise Exception(
        "Usage: python hercules_runscript.py [hercules_input_file] or python hercules_runscript.py"
    )

input_file = "inputs/hercules_input.yaml"

# Initialize logging
logger.info(f"Starting with input file: {input_file}")

# Load the input file
h_dict = load_hercules_input(input_file)

# User options
include_solar = True
include_battery = True

# Load all inputs, remove solar and/or battery as desired
if not include_solar:
    del h_dict["solar_farm"]
if not include_battery:
    del h_dict["battery"]

# Initialize the hybrid plant
hybrid_plant = HybridPlant(h_dict)
h_dict = hybrid_plant.add_plant_metadata_to_h_dict(h_dict)

# Add initial values and meta data back to the h_dict
h_dict = hybrid_plant.add_plant_metadata_to_h_dict(h_dict)


# Establish controllers based on options
interface = HerculesV2Interface(h_dict)
print("Setting up controller.")
wind_controller = WindFarmPowerTrackingController(interface, h_dict)
solar_controller = (
    SolarPassthroughController(interface, h_dict) if include_solar
    else None
)
battery_controller = (
    BatteryPassthroughController(interface, h_dict) if include_battery
    else None
)
controller = HybridSupervisoryControllerBaseline(
    interface,
    h_dict,
    wind_controller=wind_controller,
    solar_controller=solar_controller,
    battery_controller=battery_controller
)

emulator = Emulator(controller, hybrid_plant, h_dict, logger)

# Run the emulator
emulator.enter_execution(function_targets=[], function_arguments=[[]])

logger.info("Process completed successfully")
