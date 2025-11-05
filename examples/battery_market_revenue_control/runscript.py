# Requires Hercules v2

import pandas as pd
from hercules.grid.grid_utilities import generate_locational_marginal_price_dataframe
from hercules.hercules_model import HerculesModel
from hercules.utilities import load_yaml
from hercules.utilities_examples import prepare_output_directory
from whoc.controllers import BatteryPriceSOCController, HybridSupervisoryControllerMultiRef
from whoc.interfaces import HerculesV2Interface

prepare_output_directory()

input_file = "inputs/hercules_input.yaml"

df_lmp = generate_locational_marginal_price_dataframe(
    pd.read_csv("inputs/da_lmp.csv"),
    pd.read_csv("inputs/rt_lmp.csv")
)
df_lmp.drop(columns="time").to_csv("lmp_data.csv", index=False)

# Load the input file and establish the Hercules model
h_dict = load_yaml(input_file)
hmodel = HerculesModel(h_dict)

# Establish the interface and controller, assign to the Hercules model
interface=HerculesV2Interface(hmodel.h_dict)
controller = HybridSupervisoryControllerMultiRef(
    battery_controller=BatteryPriceSOCController(
        interface=interface, input_dict=hmodel.h_dict
    ),
    interface=HerculesV2Interface(hmodel.h_dict),
    input_dict=h_dict,
)
hmodel.assign_controller(controller)

# Run the simulation
hmodel.run()

hmodel.logger.info("Process completed successfully")
