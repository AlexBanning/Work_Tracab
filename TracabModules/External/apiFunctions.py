import os
import requests
from requests.structures import CaseInsensitiveDict
import pandas as pd
from bs4 import BeautifulSoup
from TracabModules.Internal.scheduleFunctions import get_tracabID, get_tracabID_demo

import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox


def get_token(url, creds):
    """

    :param url: str with the API-address one wants to do a request from
    :param creds: dict
        containing the username and password need for authentication
    :return:
    """

    headers = CaseInsensitiveDict()
    headers['content-type'] = 'application/json'
    r = requests.post(url, headers=headers, data=creds)
    token = r.content.decode('utf-8')[10:-2]

    return token


def api_lineups(token, match_id):
    """

    :param token:
    :param match_id:
    :return:
    """

    line_up_url = 'https://data.voetbaldatacentre.nl/av/api/match/lineup/' + str(match_id)
    headers = CaseInsensitiveDict()
    headers['accept'] = 'application/json'
    headers['Authorization'] = "Bearer " + token
    # r =  requests.get(line_up_url, headers=headers)
    lineups = requests.get(line_up_url, headers=headers).json()

    try:
        # Changed to now check if a valid matchShirtNumber is available for the player before adding them to the pd.DF
        # home = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
        #                       'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
        #                      zip(lineups['homeTeam']['players'], lineups['homeTeam']['players'],
        #                          lineups['homeTeam']['players'], lineups['homeTeam']['players'])
        #                      if len(z['matchShirtNumber']) != 0 and int(z['matchShirtNumber']) >= 1]
        #                     # and len(z['playerStatus']) != 0]
        #                     ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
        home = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['homeTeam']['players'], lineups['homeTeam']['players'],
                                 lineups['homeTeam']['players'], lineups['homeTeam']['players'])
                             if z['playerStatus'] == 'BASE_PLAYER' or z['playerStatus'] == 'EXTRA_PLAYER']
                            # and len(z['playerStatus']) != 0]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        # away = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
        #                       'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
        #                      zip(lineups['awayTeam']['players'], lineups['awayTeam']['players'],
        #                          lineups['awayTeam']['players'], lineups['awayTeam']['players'])
        #                      if len(z['matchShirtNumber']) != 0 and int(z['matchShirtNumber']) >= 1]
        #                     # and len(z['playerStatus']) != 0]
        #                     ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        away = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['awayTeam']['players'], lineups['awayTeam']['players'],
                                 lineups['awayTeam']['players'], lineups['awayTeam']['players'])
                             if z['playerStatus'] == 'BASE_PLAYER' or z['playerStatus'] == 'EXTRA_PLAYER']
                            # and len(z['playerStatus']) != 0]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
    except KeyError:  # normally one should spefically call the exception one expects to occure and not leave it open
        # to fetch all possible exceptions
        home = pd.DataFrame()
        away = pd.DataFrame()

    return home, away


def get_both_lineups(token, match_id_ere, home_team):
    """
    A function, that fetches lineup information for a single match specified by match_id and our own gamestats to the
    match. Returns four pd.DataFrames containing gamestats information and official lineup information.

    :param token:
    :param match_id_ere:
    :param home_team:
    :return:
    """

    home, away = api_lineups(token, match_id_ere)

    # Get Tracab matchID to download and open Tracab gamestats
    match_id_trac = get_tracabID(home_team)

    if match_id_trac is not None:
        # Add C:temp folder where all final gamestats are available as A network drive
        try:
            os.system(r'net use A: /delete /yes')
            os.system(r'net use A: \\10.49.0.10\temp /user:administrator Bismarck27 /persistent:no')
        except:
            print('The connection to APP-CGN could not be created!')
        with open('A:\\' + str(match_id_trac) + 'Gamestats.xml') as fp:
            data = BeautifulSoup(fp, features='xml')
        # with open(str(match_id_trac) + 'Gamestats.xml') as fp:
        #     data = BeautifulSoup(fp, features='xml')

        # Create two DFs containing the players available in Tracab gamestats
        home_gs = pd.DataFrame(
            [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode(
                'latin').decode(
                'utf-8'),
              'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
             zip(data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'))]
        ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        # firstname  x['sFirstName'].encode('latin').decode('utf-8') + ' ' +
        away_gs = pd.DataFrame(
            [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode(
                'latin').decode(
                'utf-8'),
              'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
             zip(data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'))]
        ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
    else:
        home_gs = pd.DataFrame()
        away_gs = pd.DataFrame()

    return [home, home_gs], [away, away_gs]


def get_both_lineups_demo(token, match_id_ere, home_team):
    """
    A function, that fetches lineup information for a single match specified by match_id and our own gamestats to the
    match. Returns four pd.DataFrames containing gamestats information and official lineup information.

    :param token:
    :param match_id_ere:
    :param home_team:
    :return:
    """

    lineups = api_lineups(token, match_id_ere)
    try:
        # Changed to now check if a valid matchShirtNumber is available for the player before adding them to the pd.DF
        home = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['homeTeam']['players'], lineups['homeTeam']['players'],
                                 lineups['homeTeam']['players'], lineups['homeTeam']['players'])
                             if len(z['matchShirtNumber']) != 0 and int(z['matchShirtNumber']) >= 1]
                            # and len(z['playerStatus']) != 0]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        away = pd.DataFrame([{'Player': x['firstName'] + ' ' + w['infix'] + ' ' + y['lastName'],
                              'jerseyNumber': int(z['matchShirtNumber'])} for x, w, y, z in
                             zip(lineups['awayTeam']['players'], lineups['awayTeam']['players'],
                                 lineups['awayTeam']['players'], lineups['awayTeam']['players'])
                             if len(z['matchShirtNumber']) != 0 and int(z['matchShirtNumber']) >= 1]
                            # and len(z['playerStatus']) != 0]
                            ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
    except KeyError:  # normally one should spefically call the exception one expects to occure and not leave it open
        # to fetch all possible exceptions
        home = pd.DataFrame()
        away = pd.DataFrame()

    # Get Tracab matchID to download and open Tracab gamestats
    match_id_trac = get_tracabID_demo(home_team)

    if match_id_trac is not None:
        # Add C:temp folder where all final gamestats are available as A network drive
        try:
            os.system(r'net use A: /delete /yes')
            os.system(r'net use A: \\10.49.0.10\temp /user:administrator Bismarck27 /persistent:no')
        except:
            print('The connection to APP-CGN could not be created!')
        with open('A:\\' + str(match_id_trac) + 'Gamestats.xml') as fp:
            data = BeautifulSoup(fp, features='xml')
        # with open(str(match_id_trac) + 'Gamestats.xml') as fp:
        #     data = BeautifulSoup(fp, features='xml')

        # Create two DFs containing the players available in Tracab gamestats
        home_gs = pd.DataFrame(
            [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode(
                'latin').decode(
                'utf-8'),
              'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
             zip(data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[0].find('Roster').find_all('Player'))]
        ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)

        # firstname  x['sFirstName'].encode('latin').decode('utf-8') + ' ' +
        away_gs = pd.DataFrame(
            [{'Player': x['sFirstName'].encode('latin').decode('utf-8') + ' ' + y['sLastName'].encode(
                'latin').decode(
                'utf-8'),
              'jerseyNumber': int(z['iJerseyNo'])} for x, y, z in
             zip(data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'),
                 data.find('Hego').find_all('Team')[1].find('Roster').find_all('Player'))]
        ).sort_values(by=['jerseyNumber'], axis=0, ascending=True)
    else:
        home_gs = pd.DataFrame()
        away_gs = pd.DataFrame()

    return [home, home_gs], [away, away_gs]


def get_wrong_players(home, away):
    """
    :param home:
    :param away:
    :return:
    """

    home_check = pd.merge(home[0], home[1], on=['# Home'], how='left', indicator='exists')
    away_check = pd.merge(away[0], away[1], on=['# Away'], how='left', indicator='exists')
    # add column to show if each row in first DataFrame exists in second
    home_check['exists'] = np.where(home_check.exists != 'both', True, False)
    away_check['exists'] = np.where(away_check.exists != 'both', True, False)

    home_wrong = np.where(home_check['exists'] == True)
    home_wrong_player = home_check.iloc[home_wrong[0]].rename(columns={'Player_x': 'Player',
                                                                       'jerseyNumber': 'Nr. EreInfo'
                                                                       }
                                                              ).sort_values(by=['Player'], axis=0)
    away_wrong = np.where(away_check['exists'] == True)
    away_wrong_player = away_check.iloc[away_wrong[0]].rename(columns={'Player_x': 'Player',
                                                                       'jerseyNumber': 'Nr. EreInfo'
                                                                       }
                                                              ).sort_values(by=['Player'], axis=0)

    home_wrong_player = home_wrong_player.drop(['Player_y', 'exists'], axis=1)
    away_wrong_player = away_wrong_player.drop(['Player_y', 'exists'], axis=1)

    return home_wrong_player, away_wrong_player


class DataFrameViewer(tk.Tk):
    def __init__(self, df1, df2, homename, awayname):
        tk.Tk.__init__(self)
        self.title('API Information')

        # Adjust the default window size
        self.geometry('800x500')  # Adjust as needed

        # Create a PanedWindow
        paned_window = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Display DataFrame 1
        frame1 = ttk.Frame(paned_window)
        paned_window.add(frame1)

        self.label1 = ttk.Label(frame1, text=homename)
        self.label1.pack(pady=5)

        # Create vertical scrollbar for tree1
        yscrollbar1 = ttk.Scrollbar(frame1, orient='vertical')
        yscrollbar1.pack(side='right', fill='y')

        # Create horizontal scrollbar for tree1
        xscrollbar1 = ttk.Scrollbar(frame1, orient='horizontal')
        xscrollbar1.pack(side='bottom', fill='x')

        self.tree1 = ttk.Treeview(frame1, yscrollcommand=yscrollbar1.set, xscrollcommand=xscrollbar1.set)
        self.tree1["columns"] = list(df1.columns)
        self.tree1["show"] = "headings"

        for col in df1.columns:
            self.tree1.heading(col, text=col)
            self.tree1.column(col, anchor=tk.CENTER)

        for i, row in df1.iterrows():
            values = [row[col] for col in df1.columns]
            self.tree1.insert("", "end", values=values)

        yscrollbar1.config(command=self.tree1.yview)
        xscrollbar1.config(command=self.tree1.xview)

        self.tree1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Display DataFrame 2
        frame2 = ttk.Frame(paned_window)
        paned_window.add(frame2)

        self.label2 = ttk.Label(frame2, text=awayname)
        self.label2.pack(pady=5)

        # Create vertical scrollbar for tree2
        yscrollbar2 = ttk.Scrollbar(frame2, orient='vertical')
        yscrollbar2.pack(side='right', fill='y')

        # Create horizontal scrollbar for tree2
        xscrollbar2 = ttk.Scrollbar(frame2, orient='horizontal')
        xscrollbar2.pack(side='bottom', fill='x')

        self.tree2 = ttk.Treeview(frame2, yscrollcommand=yscrollbar2.set, xscrollcommand=xscrollbar2.set)
        self.tree2["columns"] = list(df2.columns)
        self.tree2["show"] = "headings"

        for col in df2.columns:
            self.tree2.heading(col, text=col)
            self.tree2.column(col, anchor=tk.CENTER)

        for i, row in df2.iterrows():
            values = [row[col] for col in df2.columns]
            self.tree2.insert("", "end", values=values)

        yscrollbar2.config(command=self.tree2.yview)
        xscrollbar2.config(command=self.tree2.xview)

        self.tree2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class DataFrameSelectorApp:
    def __init__(self, root, df):
        self.root = root
        self.root.title("Match selection")

        self.df = df
        self.selected_index = None

        # Create and place widgets
        self.label_info = ttk.Label(root, text='Please enter the row index of the match (1 to ' + str(len(df)) +
                                               '):')
        self.label_info.pack(pady=10)

        self.entry_index = ttk.Entry(root)
        self.entry_index.pack(pady=10)

        self.button_submit = ttk.Button(root, text="Submit", command=self.on_submit)
        self.button_submit.pack(pady=10)

        # Display DataFrame
        self.tree = ttk.Treeview(root)
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = ""

        # Currently not displaying the column name
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=300, anchor=tk.CENTER)
            # Display the column name in bold
            self.tree.tag_configure(f"{col}_tag", font=('Helvetica', 10, 'bold'))

        for i, row in df.iterrows():
            self.tree.insert("", i, values=list(row))

        self.tree.pack(pady=10)

    def on_submit(self):
        try:
            index = int(self.entry_index.get()) - 1
            if 0 <= index < len(self.df):
                self.selected_index = index
                self.root.destroy()  # Close the Tkinter window
            else:
                tk.messagebox.showerror("Error", "Invalid row. Please enter a valid number.")
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid input. Please enter a valid number.")
