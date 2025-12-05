FLORIS_DICT = {
    "logging": {
        "console": {"enable": True, "level": "WARNING"},
        "file": {"enable": False, "level": "WARNING"},
    },
    "solver": {"type": "turbine_grid", "turbine_grid_points": 3},
    "wake": {
        "model_strings": {
            "combination_model": "sosfs",
            "deflection_model": "gauss",
            "turbulence_model": "crespo_hernandez",
            "velocity_model": "gauss",
        },
        "enable_secondary_steering": True,
        "enable_yaw_added_recovery": True,
        "enable_transverse_velocities": True,
        "enable_active_wake_mixing": False,
        "wake_deflection_parameters": {
            "gauss": {
                "ad": 0.0,
                "alpha": 0.58,
                "bd": 0.0,
                "beta": 0.077,
                "dm": 1.0,
                "ka": 0.38,
                "kb": 0.004,
            },
        },
        "wake_turbulence_parameters": {
            "crespo_hernandez": {"initial": 0.1, "constant": 0.5, "ai": 0.8, "downstream": -0.32}
        },
        "wake_velocity_parameters": {
            "gauss": {"alpha": 0.58, "beta": 0.077, "ka": 0.38, "kb": 0.004},
        },
    },
    "farm": {
        "layout_x": [0.0],
        "layout_y": [0.0],
        "turbine_type": ["nrel_5MW"],
    },
    "flow_field": {
        "wind_speeds": [8.0],
        "wind_directions": [270.0],
        "turbulence_intensities": [0.06],
        "wind_veer": 0.0,
        "wind_shear": 0.12,
        "air_density": 1.225,
        "reference_wind_height": 90.0,
    },
    "name": "GCH_for_FlorisStandin",
    "description": "FLORIS Gauss Curl Hybrid model standing in for AMR-Wind",
    "floris_version": "v4.x",
}