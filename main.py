import datetime
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.use('TkAgg')
SESSION_THRESHOLD = 300

if __name__ == '__main__':
    directory = filedialog.askdirectory()
    # read ViewingActivity
    data = pd.read_csv(f"{directory}\\CONTENT_INTERACTION\\ViewingActivity.csv")
    # remove irrelevant rows - trailers, hooks
    data = data[data["Supplemental Video Type"].isna()]
    data = data[data["Profile Name"] == "Martin"]
    data["Duration"] = pd.to_timedelta(data["Duration"])
    data["Start Time"] = pd.to_datetime(data["Start Time"], format="%Y-%m-%d %H:%M:%S")

    durations = pd.array(data["Duration"])
    data["Stop Time"] = data["Start Time"] + data["Duration"]
    # times are in utc, need to be converted to local time TODO change to any local time, not hardcoded Prague,
    #  maybe argument
    data["Start Time"] = data["Start Time"].dt.tz_localize("UCT").dt.tz_convert("CET")
    data["Stop Time"] = data["Stop Time"].dt.tz_localize("UCT").dt.tz_convert("CET")

    # lists for plotting
    hour_count = []
    day_hours = []
    durations = []
    data.index = range(len(data))
    for i in data.index:
        if i < len(data) - 1:
            diff = data.iloc[i]["Start Time"] - data.iloc[i + 1]["Stop Time"]
            if diff.seconds < SESSION_THRESHOLD:
                # print(diff)
                data.at[i + 1, "Stop Time"] = data.loc[i, "Stop Time"]
                data.at[i + 1, "Duration"] += data.loc[i, "Duration"]
                data.drop(i, inplace=True)

    for hour in range(24):
        day_hours.append(hour)
        hour_count.append(list(data["Start Time"].dt.hour).count(hour))
        durations.append(data[data["Start Time"].dt.hour == hour]["Duration"].mean())
    durations_in_minutes = [time.seconds / 60 if time.seconds > 0 else 0 for time in durations]

    fig = plt.figure(layout="constrained")
    gs = fig.add_gridspec(2, 2)
    ax2 = fig.add_subplot(gs[0, :])
    ax12 = fig.add_subplot(gs[1, 0])
    ax11 = fig.add_subplot(gs[1, 1])
    fig.set_figwidth(15)
    ax11.bar(day_hours, hour_count)
    ax11.set_title("Starting times grouped by hour")
    ax11.grid(linestyle="--")
    ax11.set_xticks(np.arange(0, 24, 1))
    ax12.bar(day_hours, durations_in_minutes)
    ax12.set_title("Average session duration")
    ax12.grid(linestyle="--")
    ax12.set_xticks(np.arange(0, 24, 1))
    daily_data = data.groupby(data["Start Time"].dt.date)
    print(daily_data["Duration"].sum())
    print(daily_data["Duration"].sum().dt.seconds)
    ax2.bar(data["Start Time"].dt.date.drop_duplicates(), daily_data["Duration"].sum().dt.seconds / 60)
    plt.show()
