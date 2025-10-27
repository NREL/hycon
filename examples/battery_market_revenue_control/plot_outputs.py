# Plot the outputs of the simulation for the wind and storage example

import matplotlib.pyplot as plt
import numpy as np
from hercules import HerculesOutput

# Read the Hercules output file using HerculesOutput
ho = HerculesOutput("outputs/hercules_output.h5")

# # Print metadata information
# print("Simulation Metadata:")
# ho.print_metadata()
# print()

# Create a shortcut to the dataframe
df = ho.df

# Get the h_dict from metadata
h_dict = ho.h_dict

fig, axarr = plt.subplots(2, 1, sharex=True)
fig.set_size_inches(10, 8)

# Plot grid signals as well as battery limits
ax = axarr[0]

ax.plot(
    df["time"],
    df["external_signals.DA_LMP"],
    label="DA LMP",
    color="k",
    linestyle="--",
    linewidth=0.5,
)
ax.plot(
    df["time"],
    df["external_signals.RT_LMP"],
    label="RT LMP",
    color="k",
    linestyle="-",
    linewidth=0.5,
)

# Process and plot the day ahead top and bottom 4 and 1
da_lmps = df[["external_signals.DA_LMP_{:02d}".format(h) for h in range(24)]].to_numpy()
da_lmps_sorted = np.sort(da_lmps, axis=1)
b4 = da_lmps_sorted[:, 3]
t4 = da_lmps_sorted[:, -4]
b1 = da_lmps_sorted[:, 0]
t1 = da_lmps_sorted[:, -1]

ax.fill_between(
    df["time"],
    t4,
    500,
    label="Main discharge price (daily)",
    color="C2",
    alpha=0.3,
    edgecolor="None",
)
ax.fill_between(
    df["time"],
    t1,
    500,
    label="High discharge price (daily)",
    color="C2",
    alpha=0.5,
    edgecolor="None",
)
ax.fill_between(
    df["time"],
    -500,
    b4,
    label="Main charge price (daily)",
    color="C1",
    alpha=0.3,
    edgecolor="None",
)
ax.fill_between(
    df["time"],
    -500,
    b1,
    label="Low charge price (daily)",
    color="C1",
    alpha=0.5,
    edgecolor="None",
)
ax.set_ylim([-50, 50])
ax.set_ylabel("Price [$/MWh]")
ax.set_xlim([0, df["time"].max()])

# Plot the battery power and SOC
ax = axarr[1]
ax.plot(
    df["time"],
    df["battery.power"]/1e3, # Base unit: kW
    label="Battery output",
    color="k",
    linewidth=1.0,
)
ax.plot(
    df["time"],
    df["battery.power_setpoint"]/1e3, # Base unit: kW
    label="Battery setpoint",
    color="k",
    linestyle=":",
    linewidth=1.0,
)
ax.set_ylabel("Power [MW]")

ax2 = ax.twinx()

color = "C0"
ax2.set_ylabel("State of charge [-]", color=color)
ax2.plot(
    df["time"],
    df["battery.soc"],
    color=color
)
ax2.tick_params(axis="y", labelcolor=color)

for ax in axarr:
    ax.grid(True)
    ax.legend(loc="upper right")

# Compute total revenue on real-time market
df["revenue_rt"] = (
    df["battery.power"]/1e3
    * df["external_signals.RT_LMP"]
    / 3600
)
print("Real-time revenue over simulation: ${:.1f}".format(df["revenue_rt"].sum()))


plt.show()
