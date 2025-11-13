# Requires Hercules v2

import pandas as pd
from hercules.grid.grid_utilities import (
    generate_locational_marginal_price_dataframe_from_gridstatus,
)
from hercules.hercules_model import HerculesModel
from hercules.utilities_examples import prepare_output_directory
from whoc.controllers import (
    BatteryPriceSOCController,
    HybridSupervisoryControllerPriceBased,
    SolarPassthroughController,
    WindFarmPowerTrackingController,
)
from whoc.interfaces import HerculesV2Interface

prepare_output_directory()

# Load and alter the input LMP data to match the time window for simulation
df_da = pd.read_csv("../shared_inputs/lmp_da.csv")
df_rt = pd.read_csv("../shared_inputs/lmp_rt.csv")

# Set the start time to 2018-05-10 at midnight
start_time = pd.Timestamp("2018-05-10 00:00:00", tz="UTC")

# Convert interval_start_utc to datetime and reset to new start time
df_da['interval_start_utc'] = pd.to_datetime(df_da['interval_start_utc'])
df_rt['interval_start_utc'] = pd.to_datetime(df_rt['interval_start_utc'])

# Calculate the time offset from the current start to the desired start
da_current_start = df_da['interval_start_utc'].min()
rt_current_start = df_rt['interval_start_utc'].min()

da_offset = start_time - da_current_start
rt_offset = start_time - rt_current_start

# Apply the offset to shift all times
df_da['interval_start_utc'] = df_da['interval_start_utc'] + da_offset
df_rt['interval_start_utc'] = df_rt['interval_start_utc'] + rt_offset

# Generate the LMP data needed for the simulation using the shifted time series
df_lmp = generate_locational_marginal_price_dataframe_from_gridstatus(df_da, df_rt)
df_lmp.to_csv("lmp_data.csv", index=False)

# Load the input file and establish the Hercules model
hmodel = HerculesModel("hercules_input.yaml")

# Establish the interface and controller, assign to the Hercules model
interface=HerculesV2Interface(hmodel.h_dict)
wind_controller = WindFarmPowerTrackingController(interface, hmodel.h_dict)
solar_controller = SolarPassthroughController(interface, hmodel.h_dict)
battery_controller = BatteryPriceSOCController(interface=interface, input_dict=hmodel.h_dict)
controller = HybridSupervisoryControllerPriceBased(
    wind_controller=wind_controller,
    solar_controller=solar_controller,
    battery_controller=battery_controller,
    interface=HerculesV2Interface(hmodel.h_dict),
    input_dict=hmodel.h_dict,
)
hmodel.assign_controller(controller)

# Run the simulation
hmodel.run()

hmodel.logger.info("Process completed successfully")
