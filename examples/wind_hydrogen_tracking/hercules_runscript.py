from hercules.hercules_model import HerculesModel
from hercules.utilities import load_hercules_input
from hercules.utilities_examples import prepare_output_directory
from whoc.controllers import (
    HydrogenPlantController,
    WindFarmPowerTrackingController,
)
from whoc.interfaces import HerculesInterface

prepare_output_directory()

h_dict = load_hercules_input("inputs/hercules_input.yaml")

# Establish the Hercules model without a controller
hmodel = HerculesModel(h_dict)

interface = HerculesInterface(hmodel.h_dict)
print("Setting up controller.")
wind_controller = WindFarmPowerTrackingController(interface, hmodel.h_dict)
controller = HydrogenPlantController(
    interface,
    hmodel.h_dict,
    generator_controller=wind_controller
)

hmodel.assign_controller(controller)
hmodel.run()

print("Finished running closed-loop controller.")