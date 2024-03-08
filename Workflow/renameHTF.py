"""
Purpose of this code is to find the latest HTF videos that were just rendered into .mp4 and then rename them according
STS requirements.

v1.0: 2024/03/08 11:45
    - First version already able to rename the videos accordingly
    - Currently this version needs to be adjusted based on bl1 or bl2 usage
    - SuperCup for BL1 schedule is neglected. NEEDS TO BE ADJUSTED FOR UPCOMING SEASON!!!
v1.1: 2024/03/08 14:20
    - Added additional check for the existence of both or only one HTF
"""
import pandas as pd
import os
from TracabModules.Internal.server_manipulations import newest_file

choice = input('Are both HTFs available? Please provide the specific input and press Enter! \n'
               '0: yes \n'
               '1: only HTF_1 (right) \n'
               '2: only HTF_2 (left) \n')

path_htf1 = r'D:\B'
path_htf2 = r'E:\D'

latest_htf1 = newest_file(path_htf1, 'mp4')
latest_htf2 = newest_file(path_htf2, 'mp4')

match = latest_htf1[-13:-6].replace('_', '-')

bl2_schedule = pd.read_excel(r'C:\Users\tracab\Desktop\BL2_HTF_Schedule.xlsx', header=1)
# Right/Left is seen from the benches => Default: left == HTF2
new_htf2 = bl2_schedule.loc[bl2_schedule['3LC'] == match]['High Behind Left'].values[0]
new_htf1 = bl2_schedule.loc[bl2_schedule['3LC'] == match]['High Behind Right'].values[0]

# Rename the available HTFs
if choice == str(0):
    os.rename(latest_htf2, path_htf2 + '\\' + new_htf2)
    os.rename(latest_htf1, path_htf1 + '\\' + new_htf1)
elif choice == str(1):
    os.rename(latest_htf1, path_htf1 + '\\' + new_htf1)
elif choice == str(2):
    os.rename(latest_htf2, path_htf2 + '\\' + new_htf2)
