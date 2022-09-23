from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import tkcalendar


class DataAnalyzer():
    def __init__(self, directory, session_threshold, root):
        self.directory = directory
        self.SESSION_THRESHOLD = session_threshold
        self.root = root
        self.data = None
        self.fig = None

    def clean_data(self, data):
        # read ViewingActivity

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

        data.index = range(len(data))
        for i in data.index:
            if i < len(data) - 1:
                diff = data.iloc[i]["Start Time"] - data.iloc[i + 1]["Stop Time"]
                if diff.seconds < self.SESSION_THRESHOLD:
                    # print(diff)
                    data.at[i + 1, "Stop Time"] = data.loc[i, "Stop Time"]
                    data.at[i + 1, "Duration"] += data.loc[i, "Duration"]
                    data.drop(i, inplace=True)
        return data

    def get_data(self):
        data = pd.read_csv(f"{self.directory}\\CONTENT_INTERACTION\\ViewingActivity.csv")
        self.data = self.clean_data(data)

    def setup_gui(self):
        fig = plt.figure(layout="constrained")
        self.fig = fig

        first_date, last_date = self.data["Start Time"].dt.date.min(), self.data["Start Time"].dt.date.max()
        print(type(first_date))
        print(first_date)
        self.start_date = tkcalendar.DateEntry(self.root, selectmode="day")
        self.start_date.set_date(first_date)
        self.start_date.pack(side=tk.LEFT)
        self.end_date = tkcalendar.DateEntry(self.root, selectmode="day")
        self.end_date.set_date(last_date)
        self.end_date.pack(side=tk.LEFT)
        self.button = tk.Button(self.root, command=self.analyze, text="Analyze")
        self.button.pack(side=tk.LEFT)
        gs = self.fig.add_gridspec(2, 2)

        self.ax2 = self.fig.add_subplot(gs[0, :])
        self.ax12 = self.fig.add_subplot(gs[1, 0])
        self.ax11 = self.fig.add_subplot(gs[1, 1])
        self.figure_canvas = FigureCanvasTkAgg(self.fig)
        NavigationToolbar2Tk(self.figure_canvas, window=self.root)
        self.figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def analyze(self):
        self.fig.clear()
        self.ax2 = None
        self.ax12 = None
        self.ax11 = None
        gs = self.fig.add_gridspec(2, 2)
        self.ax2 = self.fig.add_subplot(gs[0, :])
        self.ax12 = self.fig.add_subplot(gs[1, 0])
        self.ax11 = self.fig.add_subplot(gs[1, 1])
        start_date = pd.to_datetime(self.start_date.get_date())
        print(type(start_date))
        end_date = pd.to_datetime(self.end_date.get_date())
        print(end_date)
        data = self.data
        data = data[data["Start Time"].dt.date.between(start_date.date(), end_date.date())]
        hour_count = []
        day_hours = []
        durations = []
        for hour in range(24):
            day_hours.append(hour)
            hour_count.append(list(data["Start Time"].dt.hour).count(hour))
            durations.append(data[data["Start Time"].dt.hour == hour]["Duration"].mean())
        durations_in_minutes = [time.seconds / 60 if time.seconds > 0 else 0 for time in durations]

        # self.fig.set_figwidth(15)
        self.ax11.bar(day_hours, hour_count)
        self.ax11.set_title("Starting times grouped by hour")
        self.ax11.grid(linestyle="--")
        self.ax11.set_xticks(np.arange(0, 24, 1))
        self.ax12.bar(day_hours, durations_in_minutes)
        self.ax12.set_title("Average session duration")
        self.ax12.grid(linestyle="--")
        self.ax12.set_xticks(np.arange(0, 24, 1))
        daily_data = data.groupby(data["Start Time"].dt.date)
        print(daily_data["Duration"].sum().max())
        self.ax2.set_title("Daily minutes spent watching Netflix")
        self.ax2.bar(data["Start Time"].reindex(index=data.index[::-1]).dt.date.drop_duplicates(),
                     daily_data["Duration"].sum().dt.seconds / 60)

        self.figure_canvas.draw()
