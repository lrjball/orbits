"""
Pulls the data for the orbits of various objects from the NASA Horizons API
"""
from pathlib import Path

import pandas as pd
import requests


BASE_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"


def create_dataframe(data_string):
    df = pd.DataFrame(
        [i.split() for i in data_string.split("\n") if i.strip()],
        columns=[
            "date",
            "time",
            "magnitude",
            "surface brightness",
            "angle",
            "distance",
        ],
    )
    df["date"] = pd.to_datetime(df["date"] + " " + df["time"])
    return df.drop(columns=["time"])


def get_planet_data(command, start_time, stop_time, step_size="1d"):
    params = {
        "format": "json",
        "COMMAND": command,
        "EPHEM_TYPE": "OBSERVER",
        "CENTER": "geo",
        "MAKE_EPHEM": "YES",
        "START_TIME": start_time,
        "STOP_TIME": stop_time,
        "STEP_SIZE": step_size,
        "QUANTITIES": "'9,13,20'",
        "SUPPRESS_RANGE_RATE": "YES",
    }
    response = requests.get(BASE_URL, params=params)
    content_string = response.json()["result"]
    start = content_string.find("$$SOE")
    end = content_string.find("$$EOE")
    data_string = content_string[start + 5 : end]
    return create_dataframe(data_string)


if __name__ == "__main__":
    start_date = "2020-01-01"
    end_date = "2025-01-01"
    step_size = "1h"
    # mapping of objects to their command ID
    commands = {
        "sun": "10",
        "mercury": "199",
        "venus": "299",
        "moon": "301",
        "mars": "499",
        "jupiter": "599",
        "saturn": "699",
        "uranus": "799",
        "neptune": "899",
        "parker_solar_probe": "-96",
        # note: artificial satellites can only be forecasted for a few weeks/months:
        # "ISS": "-125544",
        # 'JWST': '-170',
        "Tesla Roadster": "-143205",
        "ceres": "1;",
        "C2022_E3": "'DES=1003845;'",
    }
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    for name, command in commands.items():
        print(f"Getting data for {name}...")
        df = get_planet_data(command, start_date, end_date, step_size=step_size)
        df.to_csv(data_dir / f"{name}_data.csv")
        print(f"Saved data for {name}")
