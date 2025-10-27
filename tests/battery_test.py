from whoc.controllers.battery_controller import (
    BatteryPriceSOCController,
)
from whoc.interfaces import HerculesV2Interface

test_hercules_dict = {
    "dt": 1,
    "time": 0,
    "plant": {"interconnect_limit": 10},
    "battery": {
        "size": 100.0,
        "energy_capacity": 400.0,
        "power": 100.0,
        "soc": 0.5,
        "charge_rate": 50.0 * 1e3,
        "discharge_rate": 100.0 * 1e3,
    },
    "external_signals": {  # Is this OK like this?
        "charge_price": 0.0,
        "discharge_price": 25.0,
        "lmp_rt": 10.0,
        "battery_power_reference": 1000.0,
    },
}


def test_BatteryPriceSOCController_init():
    test_interface = HerculesV2Interface(test_hercules_dict)

    # Initialize controller
    test_controller = BatteryPriceSOCController(test_interface, test_hercules_dict)

    # Check that the controller is initialized correctly
    assert (
        test_controller.rated_power_charging == test_hercules_dict["battery"]["charge_rate"]
    )
    assert (
        test_controller.rated_power_discharging
        == test_hercules_dict["battery"]["discharge_rate"]
    )


def test_BatteryPriceSOCController_compute_controls():
    test_interface = HerculesV2Interface(test_hercules_dict)

    # Initialize controller
    test_controller = BatteryPriceSOCController(test_interface, test_hercules_dict)

    # For testing, overwrite the high_soc_price, high_soc, low_soc_price, and low_soc
    test_controller.high_soc_price = 25.0
    test_controller.high_soc = 0.8
    test_controller.low_soc_price = 0.0
    test_controller.low_soc = 0.2

    # Test the high soc condition when lmp_rt is below the charge price
    # but above the low_soc_price
    measurement_dict = {"battery": {
        "state_of_charge": 0.9,
        "lmp_rt": 5,
        "discharge_price": 20,
        "charge_price": 10,
        "power_reference": 100000.0,
    }}
    controls_dict = test_controller.compute_controls(measurement_dict)
    assert controls_dict["power_setpoint"] == 0.0

    # Test the high soc condition when lmp_rt is below the low_soc_price
    measurement_dict = {"battery": {
        "state_of_charge": 0.9,
        "lmp_rt": -5,
        "discharge_price": 20,
        "charge_price": 10,
        "power_reference": 100000.0,
    }}
    controls_dict = test_controller.compute_controls(measurement_dict)
    assert controls_dict["power_setpoint"] == -1 * test_controller.rated_power_charging

    # Test when soc is below the high_loc and lmp_rt is below the charge price
    # and above the low_soc_price (shouldn't matter)
    measurement_dict = {"battery": {
        "state_of_charge": 0.7,
        "lmp_rt": 5,
        "discharge_price": 20,
        "charge_price": 10,
        "power_reference": 100000.0,
    }}
    controls_dict = test_controller.compute_controls(measurement_dict)
    assert controls_dict["power_setpoint"] == -1 * test_controller.rated_power_charging


    # Test when lmp_rt is in between the charge and discharge price
    measurement_dict = {"battery": {
        "state_of_charge": 0.5,
        "lmp_rt": 15,
        "discharge_price": 20,
        "charge_price": 10,
        "power_reference": 100000.0,
    }}
    controls_dict = test_controller.compute_controls(measurement_dict)
    assert controls_dict["power_setpoint"] == 0.0

    # Test when the soc is above the low_soc and lmp_rt is above the discharge price
    measurement_dict = {"battery": {
        "state_of_charge": 0.3,
        "lmp_rt": 25,
        "discharge_price": 20,
        "charge_price": 10,
        "power_reference": 100000.0,
    }}
    controls_dict = test_controller.compute_controls(measurement_dict)
    assert controls_dict["power_setpoint"] == test_controller.rated_power_discharging

    # Test when the soc is below the low_soc and lmp_rt is above the discharge price
    # But below the high_soc_price (should prevent discharge)
    measurement_dict = {"battery": {
        "state_of_charge": 0.1,
        "lmp_rt": 22,
        "discharge_price": 20,
        "charge_price": 10,
        "power_reference": 1000.0,
    }}
    controls_dict = test_controller.compute_controls(measurement_dict)
    assert controls_dict["power_setpoint"] == 0.0

    # Test when the soc is below the low_soc and lmp_rt is above the high_soc_price
    measurement_dict = {"battery": {
        "state_of_charge": 0.1,
        "lmp_rt": 26,
        "discharge_price": 20,
        "charge_price": 10,
        "power_reference": 100000.0,
    }}
    controls_dict = test_controller.compute_controls(measurement_dict)
    assert controls_dict["power_setpoint"] == test_controller.rated_power_discharging

    # Test the ability of battery reference to limit the power setpoint
    measurement_dict = {"battery": {
        "state_of_charge": 0.1,
        "lmp_rt": 26,
        "discharge_price": 20,
        "charge_price": 10,
        "power_reference": 777.0,
    }}
    controls_dict = test_controller.compute_controls(measurement_dict)
    assert controls_dict["power_setpoint"] == 777.0