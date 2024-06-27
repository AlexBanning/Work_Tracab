"""
Purpose of this code will be a game monitor for each game that is monitored by Tracab. The game monitor shall take user
input to define the match (based on matchID and league) to fetch the necessary match information and return the teams'
and player statistics for relevant KPIs.
TeamKPIs: Avg. Distance, Avg. Num. Sprints, Avg. Num. SpeedRuns
PlayerKPIs: Top Speed

Design should be relying on existing DFL_Highspeed_Monitor.

1. Receive user input for match information.
2. Take user input to get the teams and their lineups for the match of interest.
3. Fetch the team data and the player data only for those part of the lineup (to reduce load of information).
4. Return data in a similar manner as the DFL_Highspeed_Monitor.

"""
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import pandas as pd
import sqlite3 as sql
from TracabModules.Internal.scheduleFunctions import get_schedule_xml
from TracabModules.Internal.tools import get_club_id_mapping
from lxml import etree
from pathlib import Path
import os
import logging
import sys


class DataFetcher:
    def __init__(self, game_id, league, season):
        # All Feeds
        self.game_id = game_id
        self.league = league.lower()
        self.season = season

    def get_stats_tables(self, league):
        db_path = Path(f'N:/07_QC/Alex/Databases/{league}_stats.db')
        try:
            with sql.connect(db_path) as conn:
                team_query = f"SELECT * FROM 'league_overview_{self.season}'"
                avg_stats_table = pd.read_sql_query(team_query, conn)
                player_query = f"SELECT * FROM 'player_stats'"
                players = pd.read_sql_query(player_query, conn)
                return avg_stats_table, players
        except sql.Error as e:
            print(f"Error connecting to database: {e}")
            return

    def mls(self):
        if self.season == '2024':
            season_id = '8'
        tree = etree.parse(
            fr'\\10.49.0.250\d3_mls\MatchInfo\Feed_01_06_basedata_fixtures_MLS-SEA-0001K{season_id}_MLS-COM-000001.xml')
        root = tree.getroot()

        match = next(
            (
                {
                    'STS-ID': obj.get("MatchId"),
                    'Home': obj.get("HomeTeamName"),
                    'Away': obj.get("GuestTeamName")
                }
                for obj in root.findall('.//Fixture') if obj.get('DlProviderId') == self.game_id
            ),
            None
        )

        avg_stats_table, players = self.get_stats_tables(league=self.league)

        # Get players from active lineup
        lineup_file = fr'\\10.49.0.250\d3_mls\MatchInfo\Feed_02_01_matchinformation_MLS-COM-000001_{match['STS-ID']}.xml'
        gamestats_tree = etree.parse(lineup_file)
        gamestats_root = gamestats_tree.getroot()

        home_players = {
            obj.get('PersonId'): {
                'ShirtNumber': int(obj.get('ShirtNumber')),
                'Name': f'{obj.get('Shortname')}'
            }
            for obj in gamestats_root.findall('.//Team')[0].findall('.//Player')
        }

        away_players = {
            obj.get('PersonId'): {
                'ShirtNumber': int(obj.get('ShirtNumber')),
                'Name': f'{obj.get('Shortname')}'
            }
            for obj in gamestats_root.findall('.//Team')[1].findall('.//Player')
        }

        home_filtered_df = players[players['ObjectID'].isin(home_players.keys())]
        away_filtered_df = players[players['ObjectID'].isin(away_players.keys())]

        # Group by 'ObjectID' and get max HighSpeed value
        home_highspeeds = home_filtered_df.groupby('ObjectID')['HighSpeed'].max().reset_index()
        home_highspeeds['Name'] = home_highspeeds['ObjectID'].map(lambda x: home_players[x]['Name'])
        home_highspeeds['ShirtNumber'] = home_highspeeds['ObjectID'].map(lambda x: home_players[x]['ShirtNumber'])
        home_highspeeds = home_highspeeds[['Name', 'ShirtNumber', 'HighSpeed']].sort_values(by='ShirtNumber')

        # Away Team
        away_highspeeds = away_filtered_df.groupby('ObjectID')['HighSpeed'].max().reset_index()
        away_highspeeds['Name'] = away_highspeeds['ObjectID'].map(lambda x: away_players[x]['Name'])
        away_highspeeds['ShirtNumber'] = away_highspeeds['ObjectID'].map(lambda x: away_players[x]['ShirtNumber'])
        away_highspeeds = away_highspeeds[['Name', 'ShirtNumber', 'HighSpeed']].sort_values(by='ShirtNumber')

        columns_to_keep = ['Total Distance', 'Num. Sprints', 'Num. SpeedRuns']
        home_row = avg_stats_table[avg_stats_table['TeamName'] == match['Home']][columns_to_keep]
        away_row = avg_stats_table[avg_stats_table['TeamName'] == match['Away']][columns_to_keep]

        return home_row, away_row, match['Home'], match['Away'], home_highspeeds, away_highspeeds

    def bundesliga(self):
        if self.league.lower() == 'bl1':
            path = Path(fr'\\10.49.0.250\deltatre\MatchInfo\51\{self.season}\match_facts')

            match = next(x for x in path.iterdir() if self.game_id in x.name)


        else:
            path = Path(fr'\\10.49.0.250\deltatre\MatchInfo\52\{self.season}\match_facts')
            match = next(x for x in path.iterdir() if self.game_id in x.name)

        # Get data from database
        avg_stats_table, players = self.get_stats_tables(league=self.league)

        # Get active players of match
        tree = etree.parse(str(match))
        root = tree.getroot()

        home_name = root.findall('.//team')[0].find('team-metadata').find('name').get('full')

        away_name = root.findall('.//team')[1].find('team-metadata').find('name').get('full')


        home_players = {
            x.find('player-metadata').get('player-key'): {
                'ShirtNumber': int(x.find('player-metadata').get('uniform-number')),
                'Name': x.find('player-metadata').find('name').get('nickname')
            }
            for x in root.findall('.//team')[0].findall('.//player')
        }

        away_players = {
            x.find('player-metadata').get('player-key'): {
                'ShirtNumber': int(x.find('player-metadata').get('uniform-number')),
                'Name': x.find('player-metadata').find('name').get('nickname')
            }
            for x in root.findall('.//team')[1].findall('.//player')
        }

        home_filtered_df = players[players['DlProviderID'].isin(home_players.keys())]
        away_filtered_df = players[players['DlProviderID'].isin(away_players.keys())]

        # Group by 'ObjectID' and get max HighSpeed value
        home_highspeeds = home_filtered_df.groupby('DlProviderID')['HighSpeed'].max().reset_index()
        home_highspeeds['Name'] = home_highspeeds['DlProviderID'].map(lambda x: home_players[x]['Name'])
        home_highspeeds['ShirtNumber'] = home_highspeeds['DlProviderID'].map(lambda x: home_players[x]['ShirtNumber'])
        home_highspeeds = home_highspeeds[['Name', 'ShirtNumber', 'HighSpeed']].sort_values(by='ShirtNumber')

        # Away Team
        away_highspeeds = away_filtered_df.groupby('DlProviderID')['HighSpeed'].max().reset_index()
        away_highspeeds['Name'] = away_highspeeds['DlProviderID'].map(lambda x: away_players[x]['Name'])
        away_highspeeds['ShirtNumber'] = away_highspeeds['DlProviderID'].map(lambda x: away_players[x]['ShirtNumber'])
        away_highspeeds = away_highspeeds[['Name', 'ShirtNumber', 'HighSpeed']].sort_values(by='ShirtNumber')

        columns_to_keep = ['Total Distance', 'Num. Sprints', 'Num. SpeedRuns']
        home_row = avg_stats_table[avg_stats_table['TeamName'] == home_name][columns_to_keep]
        away_row = avg_stats_table[avg_stats_table['TeamName'] == away_name][columns_to_keep]

        return home_row, away_row, home_name, away_name, home_highspeeds, away_highspeeds

    def fetch_data(self):
        league_method_map = {
            'mls': self.mls,
            'bl1': self.bundesliga,
            'bl2': self.bundesliga
        }

        # Fetch the method based on league
        fetch_method = league_method_map.get(self.league)

        if fetch_method:
            return fetch_method()
        else:
            print(f"No method defined for league: {self.league}")
            return None


class TracabGameMonitor:
    def __init__(self):
        self.leagues = ['BL1', 'BL2', 'MLS', 'Eredivisie', 'Ekstraklasa']

        self.root = tk.Tk()
        self.root.title("Tracab GameMonitor")
        # Load Tracab Icon
        exe_dir = getattr(sys, '_MEIPASS', os.getcwd())
        self.root.iconbitmap(os.path.join(exe_dir, "Tracab.ico"))
        # Set Background colour
        self.root.configure(bg='#2F4F4F')

        # Adjust the size of the GUI window
        self.root.geometry("700x250")

        # Create a frame to contain the labels and buttons
        self.center_frame = tk.Frame(self.root)
        self.center_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.center_frame.configure(bg='#2F4F4F')

        # Dropdown list for selecting the league
        tk.Label(self.center_frame, text="Select League:", fg="#98FB98", bg="#2F4F4F").grid(row=0, column=0, padx=5,
                                                                                            pady=2,
                                                                                            sticky="nw")
        self.league_var = tk.StringVar(self.root)
        self.league_dropdown = ttk.Combobox(self.center_frame, textvariable=self.league_var, values=self.leagues,
                                            state='readonly')
        self.league_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="nw")

        # Input field for entering the GameID
        tk.Label(self.center_frame, text="Enter GameID:", fg="#98FB98", bg="#2F4F4F").grid(row=1, column=0, padx=5,
                                                                                           pady=2, sticky="nw")
        self.teamid_var = tk.StringVar(self.root)
        self.teamid_entry = tk.Entry(self.center_frame, textvariable=self.teamid_var)
        self.teamid_entry.grid(row=1, column=1, padx=5, pady=2, sticky="nw")

        # Button to fetch team and player data
        self.fetch_button = tk.Button(self.center_frame, text="Get Data", command=self.fetch_data)
        self.fetch_button.grid(row=3, column=0, columnspan=2, pady=0, sticky="nw")

        # Create a frame to contain the TreeView for displaying dataframes
        self.dataframe_frame = tk.Frame(self.root)
        self.dataframe_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.dataframe_frame.configure(bg='#2F4F4F')

        # Adjust the window geometry
        self.adjust_window_size()

        self.root.mainloop()

    def fetch_data(self):
        league = self.league_var.get()
        game_id = self.teamid_var.get()

        # Replace with your function to fetch highspeed dataframes based on home_team and away_team
        try:
            fetcher = DataFetcher(game_id=game_id, league=league, season="2023")
            home_row, away_row, home_name, away_name, home_highspeeds, away_highspeeds = fetcher.fetch_data()

            # Check if Treeview widgets already exist, if not, create new ones
            if not hasattr(self, 'home_treeview') or not hasattr(self, 'away_treeview'):
                # Create a TreeView to display dataframes
                self.home_treeview = ttk.Treeview(self.dataframe_frame)
                self.away_treeview = ttk.Treeview(self.dataframe_frame)

                # Pack Treeview widgets into the frame
                self.home_treeview.pack(side="left", padx=5, pady=5)
                self.away_treeview.pack(side="right", padx=5, pady=5)

                # Create a style object
                style = ttk.Style()

                # Configure Treeview style with desired background and foreground colors
                style.configure("Treeview", background='#2F4F4F',
                                foreground="#98FB98")  # Light gray background, black text color

                # Apply the style to the Treeview widgets
                self.home_treeview.configure(style="Treeview")
                self.away_treeview.configure(style="Treeview")

            # Otherwise, clear existing contents of Treeview widgets
            else:
                self.home_treeview.delete(*self.home_treeview.get_children())
                self.away_treeview.delete(*self.away_treeview.get_children())

            # Create a style object
            style = ttk.Style()

            # Configure Treeview style with desired background and foreground colors
            style.configure("Treeview", background='#2F4F4F',
                            foreground="#98FB98")  # Light gray background, black text color

            # Apply the style to the Treeview widgets
            self.home_treeview.configure(style="Treeview")
            self.away_treeview.configure(style="Treeview")

            # Pack Treeview widgets into the frame
            self.home_treeview.pack(side="left", padx=5, pady=5)
            self.away_treeview.pack(side="right", padx=5, pady=5)

            # Display dataframes in TreeView
            self.display_dataframe(home_highspeeds, self.home_treeview)
            self.display_dataframe(away_highspeeds, self.away_treeview)

            # Adjust the window geometry
            self.adjust_window_size()
        except FileNotFoundError as e:
            error_msg = f"File not found: {e.filename}"
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)

        except Exception as e:
            error_msg = f"An error occurred: {e}"
            logging.error(error_msg)
            messagebox.showerror("Error", error_msg)

    def adjust_window_size(self):
        self.root.update_idletasks()  # Update the GUI to finish arranging widgets
        width = self.root.winfo_reqwidth()  # Get the required width of the GUI
        height = self.root.winfo_reqheight()  # Get the required height of the GUI
        self.root.geometry(f"{width}x{height}")  # Set the GUI window size

    def display_dataframe(self, dataframe, treeview):
        # Clear previous data
        treeview.delete(*treeview.get_children())

        # Display dataframe columns as headers
        treeview["columns"] = list(dataframe.columns)
        for col in dataframe.columns:
            treeview.heading(col, text=col)

        # Adjust column widths based on content
        for col in dataframe.columns:
            treeview.column(col, width=max(100, len(col) * 10))  # Adjust width based on column name length

        # Insert the data
        for index, row in dataframe.iterrows():
            values = list(row)
            treeview.insert('', 'end', text='', values=values)

        # Remove the first column completely
        treeview["show"] = "headings"


test = TracabGameMonitor()
