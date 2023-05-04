import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle
import numpy as np
from datetime import datetime, timedelta

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# here enter the id of your google sheet
SAMPLE_SPREADSHEET_ID_input = "1dsdOvLlpjLwBDQc98mpxz7vY3jzWqR-u-fJNrKB-y88"
SAMPLE_RANGE_NAME = 'A1:F307'


# Function to call in data from Google-Sheet

def main():
    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "C:\\Users\\tracab.CHYRONHEGO\\Documents\\PythonFun\\Script_Learning\\google_creds.json",
                SCOPES)  # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                      range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])

    if not values_input and not values_expansion:
        print('No data found.')


main()

#  DataFrame with data from selected Google-Sheet
df = pd.DataFrame(values_input[1:], columns=values_input[0])

# Create Matrix with 'True' and 'False' to get the shift for each match
shift_matrix = np.full((306, 30), False)

# Create list with all possible time-slots
times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30","14:00", "14:30",
         "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
         "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"]
# Create list with datetime objects with timeslots
lstTime = [datetime.strptime(x, "%H:%M").time() for x in times]
# Check each match and set the shift-times accordingly
for i, match in enumerate(df.iterrows()):
    ko_time = datetime.strptime(match[1]["KickOff"][11:16], "%H:%M").time()
    ko_date_object = datetime.strptime(match[1]["KickOff"], '%Y-%m-%d %H:%M')
    shift_start = (ko_date_object - timedelta(hours=2.5)).time()
    shift_end = (ko_date_object + timedelta(hours=2.5)).time()
    shift_list = [True if shift_start <= x <= shift_end else False for x in lstTime]
    shift_matrix[i] = shift_list




# Set column names of final DF to time-slots
times = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30","14:00", "14:30",
         "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30",
         "21:00", "21:30", "22:00", "22:30", "23:00", "23:30"]
lstTime = [datetime.strptime(x, "%H:%M").time() for x in times]

shift_df = pd.DataFrame(shift_matrix, columns=times)


"""
Write a Google Sheet
"""
df = shift_df
SAMPLE_SPREADSHEET_ID_input = '1dsdOvLlpjLwBDQc98mpxz7vY3jzWqR-u-fJNrKB-y88'

# change the range if needed
SAMPLE_RANGE_NAME = 'A1:AA1000'


def Create_Service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    # print(SCOPES)

    cred = None

    if os.path.exists('token_write.pickle'):
        with open('token_write.pickle', 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            cred = flow.run_local_server()

        with open('token_write.pickle', 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, 'service created successfully')
        # return service
    except Exception as e:
        print(e)
        # return None


# change 'my_json_file.json' by your downloaded JSON file.
Create_Service('C:\\Users\\tracab.CHYRONHEGO\\Documents\\PythonFun\\Script_Learning\\google_creds.json',
               'sheets', 'v4', ['https://www.googleapis.com/auth/spreadsheets'])


def Export_Data_To_Sheets():
    response_date = service.spreadsheets().values().update(
        spreadsheetId='1dsdOvLlpjLwBDQc98mpxz7vY3jzWqR-u-fJNrKB-y88',
        valueInputOption='RAW',
        range=SAMPLE_RANGE_NAME,
        body=dict(
            majorDimension='ROWS',
            values=df.T.reset_index().T.values.tolist())
    ).execute()
    print('Sheet successfully Updated')


Export_Data_To_Sheets()