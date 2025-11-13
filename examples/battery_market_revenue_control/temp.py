# Requires Hercules v2

import matplotlib.pyplot as plt
import pandas as pd
from hercules.grid.grid_utilities import generate_locational_marginal_price_dataframe

# Generate the LMP data needed for the simulation
df_lmp = generate_locational_marginal_price_dataframe(
    pd.read_csv("inputs/da_lmp.csv"),
    pd.read_csv("inputs/rt_lmp.csv")
)

fig, ax = plt.subplots()
fig.set_size_inches(10, 5)

for i in range(24):
    ax.plot(
        df_lmp["time_utc"],
        df_lmp[f"DA_LMP_{i:02d}"],
        label=f"DA_LMP_{i:02d}"
    )

plt.show()