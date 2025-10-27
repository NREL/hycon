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

# If the output folder exists, delete it
if os.path.exists("outputs"):
    shutil.rmtree("outputs")
os.makedirs("outputs")

def generate_day_ahead_prices(df_dayahead_lmp):
    df = df_dayahead_lmp[df_dayahead_lmp["time"] % 3600 == 0]

    df["datetime"] = pd.to_datetime(df["time_utc"])

    # Extract date and hour
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour

    df_hourly = df.pivot_table(
        values="lmp_da",
        index="date",
        columns="hour",
        aggfunc="first"  # Use first value if multiple entries per hour
    )
    df_hourly = df_hourly.reindex(columns=list(range(24)))
    df_hourly = df_hourly.rename(columns={h: "DA_LMP_{:02d}".format(h) for h in df_hourly.columns})
    df_hourly = df_hourly.reset_index()

    # Add back time column and drop unneeded date column
    df_hourly["time"] = df["time"][0:-1:24].values
    df_hourly = df_hourly.drop(columns=["date"])

    df = (df_dayahead_lmp[["time", "lmp_rt", "lmp_da"]]
          .rename(columns={"lmp_rt": "RT_LMP", "lmp_da": "DA_LMP"})
          .merge(
            df_hourly,
            on="time",
            how="left",
          )
          .fillna(method="ffill")
    )

    df.to_csv("lmp_data.csv", index=False)
    return None

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

generate_day_ahead_prices(pd.read_csv("inputs/one_week_lmp.csv"))

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
