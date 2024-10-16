"""
Purpose of this code is to find the latest HTF videos that were just rendered into .mp4 and then rename them according
STS requirements.

v0.0: 2024/03/08 11:45
    - First version already able to rename the videos accordingly
    - Currently this version needs to be adjusted based on bl1 or bl2 usage
    - SuperCup for BL1 schedule is neglected. NEEDS TO BE ADJUSTED FOR UPCOMING SEASON!!!
v0.1: 2024/03/08 14:20
    - Added additional check for the existence of both or only one HTF
v0.2: 2024/03/12 13:35
    - Added some GUI at the end indicating when files have been renamed
    - Added some logging information
    - Added additional functions and modularity
v1.0: 2024/03/20 15:30
    - Added additional fail-safe if wrong files get selected
    - Final version, ready to be implemented in workflow
v1.1: 2024/04/04 17:00
    - Added fail-safe for wrong 3LCs
    - Corrected fail-safe for selection of only one file
"""
import os

import pandas as pd
import logging
from TracabModules.Internal.server_manipulations import choose_file, display_popup, rename_htf_files
from tkinter import Tk, messagebox
import sys

# Constants
DEFAULT_PATH_HTF1 = r'E:\D'
BL1_SCHEDULE_PATH = os.getcwd() + '\\BL2_HTF_Schedule.xlsx'
ALLOWED_FILE_TYPES = ("MP4 files", "*.mp4")

# Add this at the beginning of your script
logging.basicConfig(level=logging.INFO)

# Initialize Tkinter root window
root = Tk()
root.withdraw()  # Hide the root window

latest_htf1 = choose_file(DEFAULT_PATH_HTF1, title="Select HTF_2", allowed_types=("MP4 files", "*.mp4"), keyword='_2.mp4')

if latest_htf1:
    match = latest_htf1[-13:-6].replace('_', '-')

bl1_schedule = pd.read_excel(BL1_SCHEDULE_PATH, header=1)

try:
    new_htf1 = bl1_schedule.loc[bl1_schedule['3LC'] == match]['High Behind Right'].values[0]
except IndexError:
    messagebox.showwarning('Invalid 3LC in selected file/-s',
                           f'Please select the correct file/-s and check the 3LC!')
    root.destroy()  # Destroy the Tkinter root window
    sys.exit()
# Rename the available HTFs
if latest_htf1:
    rename_htf_files(latest_htf1, new_htf1)

root.destroy()
sys.exit()
