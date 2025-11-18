import matplotlib.pyplot as plt
import pandas as pd
from hercules import HerculesOutput

# Read the data from the simulation
ho = HerculesOutput("outputs/hercules_output.h5")
df = ho.df

# Extract individual components powers as well as total power
print(df.columns)
time = df["time"]

# Set plotting aesthetics
wind_col = "C0"
h2_col = "k"
power_err_col = "red"
h2_ref_col = "red"

# Plot the hydrogen output 
fig, ax = plt.subplots(2, 1, sharex=True, figsize=(12,8))
ax[0].plot(
    time/60,
    df["plant.locally_generated_power"]/1e3,
    color=wind_col,
    label="Power generated"
)
ax[0].plot(
    time/60,
    -df["electrolyzer.power"]/1e3,
    color=h2_col,
    label="Electrolyzer power consumed",
    linestyle="--"
)
ax[0].fill_between(
    time/60,
    df["plant.power"]/1e3,
    color=power_err_col,
    label="Generation/consumption mismatch"
)
ax[0].set_ylabel("Power [MW]")
ax[0].grid()
ax[0].legend(loc="lower right")

ax[1].plot(
    time/60,
    df["external_signals.hydrogen_reference"],
    color=h2_ref_col,
    label="Hydrogen reference",
    linestyle=":"
)
ax[1].plot(time/60, df["electrolyzer.H2_output"], color=h2_col, label="Hydrogen output rate")
ax[1].set_ylabel("Hydrogen Production Rate [kg/s]")
ax[1].grid()
ax[1].legend(loc="lower right")
ax[1].set_xlabel("Time [mins]")

# fig.savefig("../../docs/graphics/wind-hydrogen-example-plot.png", dpi=300, format="png")
plt.show()
