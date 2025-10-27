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

# TODO: Should this be internal to the controller? I.e. the controller receives just the DA price?
def generate_pricing_power_reference(df_dayahead_lmp):
    # Resample df_period_start_only to be hourly noting that for the day ahead
    # data this was anyway upsampled from houly originally so only need to grab
    # the rows which correspond to the start of each hour
    df_period_start_only = df_dayahead_lmp[
        df_dayahead_lmp["time"] % 3600 == 0
    ]

    # Add a date column to df_period_start_only
    df_period_start_only["date"] = pd.to_datetime(df_period_start_only["time_utc"]).dt.date

    # The discharge price is the 4th highest price in the day
    df_period_start_only["discharge_price"] = df_period_start_only.groupby("date")[
        "lmp_da"
    ].transform(lambda x: x.nlargest(4).iloc[3])
    # The charge price is the 4th lowest price in the day
    df_period_start_only["charge_price"] = df_period_start_only.groupby("date")[
        "lmp_da"
    ].transform(lambda x: x.nsmallest(4).iloc[3])

    # Merge df_period_start_only onto df and forward fill the discharge and charge prices
    df = df_dayahead_lmp.merge(
        df_period_start_only[["time", "discharge_price", "charge_price"]],
        on="time",
        how="left",
    )
    df["discharge_price"] = df["discharge_price"].ffill()
    df["charge_price"] = df["charge_price"].ffill()


    # In this setting battery power reference sets the max power
    df["battery_power_reference"] = 10000

    df = df[
        ["time", "battery_power_reference", "discharge_price", "charge_price", "lmp_rt", "lmp_da"]
    ]

    df.to_csv("power_reference.csv", index=False)
    return None


# ## TEMPORARY

# df = pd.read_feather("lmp_input.ftr")
# df = df[df.time_utc.dt.tz_localize(None) >= np.datetime64('2020-04-01 00:00:00')]
# df = df[df.time_utc.dt.tz_localize(None) < np.datetime64('2020-04-08 00:00:00')]

# # Make a version including period end
# df_period_end = df.copy(deep=True)
# df_period_end["time"] = df_period_end["time"] + 299.0
# df_period_end["time_utc"] = df_period_end["time_utc"] + pd.Timedelta(seconds=299)
# df = pd.concat([df, df_period_end]).sort_values(by="time")
# df.time = df.time - df.time.min()

# df.to_csv("one_week_lmp.csv", index=False)


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

generate_pricing_power_reference(pd.read_csv("inputs/one_week_lmp.csv"))

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
