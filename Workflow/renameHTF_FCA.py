"""
Purpose of this code is to find the latest HTF videos that were just rendered into .mp4 and then rename them according
STS requirements. Adjusted version of renameHTF.py for the special set up in FCA with only one drive being available
"""
import pandas as pd
import os
from TracabModules.Internal.server_manipulations import newest_file

choice = input('Are both HTFs available? Please provide the specific input and press Enter! \n'
               '0: yes \n'
               '1: only HTF_1 (right) \n'
               '2: only HTF_2 (left) \n')

path_htf1 = r'E:\B'
path_htf2 = r'E:\D'

latest_htf1 = newest_file(path_htf1, 'mp4')
latest_htf2 = newest_file(path_htf2, 'mp4')

match = latest_htf1[-13:-6].replace('_', '-')

bl1_schedule = pd.read_excel(r'C:\Users\tracab\Desktop\BL1_HTF_Schedule.xlsx', header=1)

# Right/Left is seen from the benches => Default: left == HTF2

new_htf2 = bl1_schedule.loc[bl1_schedule['3LC'] == match]['High Behind Left'].values[0]
new_htf1 = bl1_schedule.loc[bl1_schedule['3LC'] == match]['High Behind Right'].values[0]

if choice == str(0):
    os.rename(latest_htf2, path_htf2 + '\\' + new_htf2)
    os.rename(latest_htf1, path_htf1 + '\\' + new_htf1)
elif choice == str(1):
    os.rename(latest_htf1, path_htf1 + '\\' + new_htf1)
elif choice == str(2):
    os.rename(latest_htf2, path_htf2 + '\\' + new_htf2)
