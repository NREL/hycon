# Plot the outputs of the simulation for the wind and storage example

import matplotlib.pyplot as plt
from hercules import HerculesOutput


# Read the Hercules output file using HerculesOutput
def plot_outputs():
    ho = HerculesOutput("outputs/hercules_output.h5")

    wind_color="C0"
    solar_color="C1"
    battery_color="C5"

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
        df["external_signals.lmp_da"],
        label="Day-ahead LMP",
        color="k",
        linestyle="--",
        linewidth=0.5,
    )
    ax.plot(
        df["time"],
        df["external_signals.lmp_rt"],
        label="Real-time LMP",
        color="k",
        linestyle="-",
        linewidth=0.5,
    )
    ax.plot(
        df["time"],
        [h_dict["controller"]["wind_price_threshold"]]*len(df),
        color=wind_color,
        linestyle="-",
        linewidth=1.0,
        label="Wind price threshold",
    )
    ax.plot(
        df["time"],
        [h_dict["controller"]["solar_price_threshold"]]*len(df),
        color=solar_color,
        linestyle="-",
        linewidth=1.0,
        label="Solar price threshold",
    )

    ax.grid()
    ax.legend()
    ax.set_ylim([-12, 12])
    ax.set_ylabel("Price [$/MWh]")
    ax.set_xlim([0, df["time"].max()])

    # Plot the power produced/consumed by each component
    ax = axarr[1]
    ax.plot(
        df["time"],
        df["wind_farm.power"]/1e3, # Base unit: kW
        label="Wind farm output",
        color=wind_color,
        linewidth=1.0,
    )
    ax.plot(
        df["time"],
        df["solar_farm.power"]/1e3, # Base unit: kW
        label="Solar output",
        color=solar_color,
        linewidth=1.0,
    )
    ax.plot(
        df["time"],
        df["battery.power"]/1e3, # Base unit: kW
        label="Battery output",
        color=battery_color,
        linewidth=1.0,
    )
    ax.plot(
        df["time"],
        df["plant.power"]/1e3, # Base unit: kW
        label="Total plant output",
        color="k",
        linewidth=1.0,
    )
    ax.plot(
        df["time"],
        [h_dict["plant"]["interconnect_limit"]/1e3]*len(df),
        label="Interconnection limit",
        color="red",
        linestyle="--"
    )


    ax.legend()
    ax.grid()
    ax.set_ylabel("Power [MW]")


if __name__ == "__main__":
    plot_outputs()
    plt.show()
