import pandas as pd
import gspread
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle
import numpy as np
from datetime import datetime, timedelta

# Get schedule data from Schedule-Sheet
gc = gspread.oauth(credentials_filename=
                   'C:\\Users\\alexa\\PycharmProjects\\Work_Tracab\\Script_Learning\\google_creds.json'
                   )
sh = gc.open_by_key("1OOPlbHIG9Di3R5XJVWFzWtwNmim_wkxZPH0wUnLaQUk")
sheet = sh.worksheet("Test")
values = sheet.get(('A1:F1000'))
#  DataFrame with data from selected Google-Sheet
df = pd.DataFrame(values[1:], columns=values[0])

# Create Matrix with 'True' and 'False' to get the shift for each match
shift_matrix = np.full((493, 45), False)

# Create list with all possible time-slots
times = ["00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30", "04:00", "04:30", "05:00", "05:30",
         "06:00", "06:30", "07:00", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00",
         "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00",
         "19:30", "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"]
# Create list with datetime objects with timeslots
lstTime = [datetime.strptime(x, "%H:%M").time() for x in times]
# Check each match and set the shift-times accordingly
# Currently only working for matches that start later than 2:30am -> for shifts that would start on the earlier day
for i, match in enumerate(df.iterrows()):
    ko_time = datetime.strptime(match[1]["KickOff"][11:16], "%H:%M").time()
    ko_date_object = datetime.strptime(match[1]["KickOff"], '%Y-%m-%d %H:%M')
    shift_start = (ko_date_object - timedelta(hours=2.5)).time()
    print(shift_start)
    shift_end = (ko_date_object + timedelta(hours=2.5)).time()
    shift_list = [True if shift_start <= x <= shift_end else False for x in lstTime]
    shift_matrix[i] = shift_list


shift_df = pd.DataFrame(shift_matrix, columns=times)

# Write/Update the google sheet
dispo_sheet = gc.open_by_key("1dsdOvLlpjLwBDQc98mpxz7vY3jzWqR-u-fJNrKB-y88")
new_sheet = dispo_sheet.worksheet("MLS-Dispo")
new_sheet.update([shift_df.columns.values.tolist()] + shift_df.values.tolist())
