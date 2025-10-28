import pandas as pd
from floris.utilities import wrap_180


def convert_absolute_nacelle_heading_to_offset(target_nac_heading, current_nac_heading):
    # NOTE: by convention, absolute headings are given CW positive, but offsets
    # are given CCW positive.

    return -1 * wrap_180(target_nac_heading - current_nac_heading)

def generate_day_ahead_price_dataframe(df_in):
    # TODO: Add docstring
    # TODO: Check time rounding ok? Better if time_utc was used, perhaps?
    df_hr = df_in[df_in["time"] % 3600 == 0]

    df_hr["datetime"] = pd.to_datetime(df_hr["time_utc"])

    # Extract date and hour
    df_hr["date"] = df_hr["datetime"].dt.date
    df_hr["hour"] = df_hr["datetime"].dt.hour

    df_hourly = df_hr.pivot_table(
        values="lmp_da",
        index="date",
        columns="hour",
        aggfunc="first"  # Use first value if multiple entries per hour
    )
    df_hourly = df_hourly.reindex(columns=list(range(24)))
    df_hourly = df_hourly.rename(columns={h: "DA_LMP_{:02d}".format(h) for h in df_hourly.columns})
    df_hourly = df_hourly.reset_index()

    # Add back time column and drop unneeded date column
    df_hourly["time"] = df_hr["time"][0:-1:24].values
    df_hourly = df_hourly.drop(columns=["date"])

    df_out = (df_in[["time", "lmp_rt", "lmp_da"]]
          .rename(columns={"lmp_rt": "RT_LMP", "lmp_da": "DA_LMP"})
          .merge(
            df_hourly,
            on="time",
            how="left",
          )
          .fillna(method="ffill")
    )

    return df_out

