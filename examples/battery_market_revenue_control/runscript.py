# Requires Hercules v2

import pandas as pd
from hercules.grid.grid_utilities import (
    generate_locational_marginal_price_dataframe_from_gridstatus,
)
from hercules.hercules_model import HerculesModel
from hercules.utilities_examples import prepare_output_directory
from whoc.controllers import BatteryPriceSOCController, HybridSupervisoryControllerMultiRef
from whoc.interfaces import HerculesV2Interface

prepare_output_directory()

# Generate the LMP data needed for the simulation
df_lmp = generate_locational_marginal_price_dataframe_from_gridstatus(
    pd.read_csv("inputs/lmp_da.csv"),
    pd.read_csv("inputs/lmp_rt.csv")
)
df_lmp.to_csv("lmp_data.csv", index=False)

# Load the input file and establish the Hercules model
hmodel = HerculesModel("inputs/hercules_input.yaml")

# Establish the interface and controller, assign to the Hercules model
interface=HerculesV2Interface(hmodel.h_dict)
controller = HybridSupervisoryControllerMultiRef(
    battery_controller=BatteryPriceSOCController(
        interface=interface, input_dict=hmodel.h_dict
    ),
    interface=HerculesV2Interface(hmodel.h_dict),
    input_dict=hmodel.h_dict,
)
hmodel.assign_controller(controller)

# Run the simulation
hmodel.run()

hmodel.logger.info("Process completed successfully")
