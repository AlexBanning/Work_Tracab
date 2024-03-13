"""
Purpose of this code is to find the latest HTF videos that were just rendered into .mp4 and then rename them according
STS requirements.

v1.0: 2024/03/08 11:45
    - First version already able to rename the videos accordingly
    - Currently this version needs to be adjusted based on bl1 or bl2 usage
    - SuperCup for BL1 schedule is neglected. NEEDS TO BE ADJUSTED FOR UPCOMING SEASON!!!
v1.1: 2024/03/08 14:20
    - Added additional check for the existence of both or only one HTF
v1.2: 2024/03/12 13:35
    - Added some GUI at the end indicating when files have been renamed
    - Added some logging information
"""
import pandas as pd
import logging
import tkinter as tk
from tkinter import messagebox
import os
from TracabModules.Internal.server_manipulations import choose_file


# Add this at the beginning of your script
logging.basicConfig(level=logging.INFO)

path_htf1 = r'D:\B'
path_htf2 = r'E:\D'

latest_htf1 = choose_file(path_htf1, feed="HTF_1", allowed_types=("MP4 files", "*.mp4"))
latest_htf2 = choose_file(path_htf2, feed="HTF_2", allowed_types=("MP4 files", "*.mp4"))

match = latest_htf1[-13:-6].replace('_', '-')

bl1_schedule = pd.read_excel(r'C:\Users\tracab\Desktop\BL1_HTF_Schedule.xlsx', header=1)

# Right/Left is seen from the benches => Default: left == HTF2
new_htf2 = bl1_schedule.loc[bl1_schedule['3LC'] == match]['High Behind Left'].values[0]
new_htf1 = bl1_schedule.loc[bl1_schedule['3LC'] == match]['High Behind Right'].values[0]

# Rename the available HTFs

logging.info(f"Renaming {latest_htf2} to {path_htf2}\\{new_htf2}")
os.rename(latest_htf2, f"{path_htf2}\\{new_htf2}")
logging.info(f"Renaming {latest_htf1} to {path_htf1}\\{new_htf1}")
os.rename(latest_htf1, f"{path_htf1}\\{new_htf1}")


# Display popup window with information
root = tk.Tk()
root.withdraw()  # Hide the main window
messagebox.showinfo("Renaming HTFs", "Files have been successfully renamed!")
root.mainloop()