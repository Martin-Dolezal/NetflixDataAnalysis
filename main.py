from tkinter import filedialog
import pandas as pd
from time import strptime
import matplotlib.pyplot as plt
import datetime
from pytz import timezone
import pytz
import numpy as np

if __name__ == '__main__':
    directory = filedialog.askdirectory()
    # read ViewingActivity
    data = pd.read_csv(f"{directory}\\CONTENT_INTERACTION\\ViewingActivity.csv")
    # remove irrelevant rows - trailers, hooks
    data = data[data["Supplemental Video Type"].isna()]
    start_times = pd.array(data["Start Time"])

    # convert times from string to datetime object
    hours_utc = [datetime.datetime(*strptime(item, "%Y-%m-%d %H:%M:%S")[:6]) for item in start_times]

    # times are in utc, need to be converted to local time TODO change to any local time, not hardcoded Prague,
    #  maybe argument
    hours_prague = [pytz.utc.localize(hour, is_dst=True).astimezone(timezone("Europe/Prague")).hour for hour in
                    hours_utc]

    # arrays for plotting
    hour_count = []
    day_hours = []
    for hour in range(24):
        day_hours.append(hour)
        hour_count.append(hours_prague.count(hour))
    fig, ax = plt.subplots(layout="constrained")
    ax.bar(day_hours, hour_count)
    ax.set_title("Netflix starting times grouped by hour")
    ax.grid(linestyle="--")
    ax.set_xticks(np.arange(0, 24, 1))
    plt.show()
