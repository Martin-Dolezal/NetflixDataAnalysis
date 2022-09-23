import datetime
import tkcalendar
from tkinter import filedialog
from utilities.data_analysis import DataAnalyzer
import matplotlib

import tkinter as tk

matplotlib.use('TkAgg')
SESSION_THRESHOLD = 300

if __name__ == '__main__':
    root = tk.Tk()
    chart_frame = tk.Frame(root)
    chart_frame.pack()
    directory = filedialog.askdirectory()
    analyzer = DataAnalyzer(directory, SESSION_THRESHOLD, root)
    analyzer.get_data()
    analyzer.setup_gui()
    # analyzer.analyze()
    root.mainloop()
