# Requires Hercules v2
import os
import shutil
import sys

import pandas as pd
from hercules.emulator import Emulator
from hercules.hybrid_plant import HybridPlant
from hercules.utilities import load_hercules_input, setup_logging
from whoc.controllers import BatteryPriceSOCController, HybridSupervisoryControllerMultiRef
from whoc.interfaces import HerculesV2Interface
from whoc.utilities import generate_locational_marginal_price_dataframe

# If the output folder exists, delete it
if os.path.exists("outputs"):
    shutil.rmtree("outputs")
os.makedirs("outputs")

# Get the logger
logger = setup_logging()

# If more than one argument is provided raise and error
if len(sys.argv) > 2:
    raise Exception(
        "Usage: python hercules_runscript.py [hercules_input_file] or python hercules_runscript.py"
    )

# If one argument is provided, use it as the input file
if len(sys.argv) == 2:
    input_file = sys.argv[1]
# If no arguments are provided, use the default input file
else:
    input_file = "inputs/hercules_input.yaml"

df_lmp = generate_locational_marginal_price_dataframe(
    pd.read_csv("inputs/da_lmp.csv"),
    pd.read_csv("inputs/rt_lmp.csv")
)
df_lmp[df_lmp.time <= 604800.0].drop(columns="time_utc").to_csv("lmp_data.csv", index=False)

# Initialize logging
logger.info(f"Starting with input file: {input_file}")

# Load the input file
h_dict = load_hercules_input(input_file)

# Establish the interface and controller
interface=HerculesV2Interface(h_dict)
controller = HybridSupervisoryControllerMultiRef(
    battery_controller=BatteryPriceSOCController(
        interface=interface, input_dict=h_dict
    ),
    interface=HerculesV2Interface(h_dict),
    input_dict=h_dict,
)

# Initialize the hybrid plant
hybrid_plant = HybridPlant(h_dict)

# Add initial values and meta data back to the h_dict
h_dict = hybrid_plant.add_plant_metadata_to_h_dict(h_dict)

# Initialize the emulator
emulator = Emulator(controller, hybrid_plant, h_dict, logger)

# Run the emulator
emulator.enter_execution(function_targets=[], function_arguments=[[]])

logger.info("Process completed successfully")
