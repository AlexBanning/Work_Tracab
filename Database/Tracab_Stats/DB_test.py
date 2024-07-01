import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from TracabModules.Internal.database import create_team_stats_table, print_stats_table, create_avg_stats_table
from TracabModules.Internal.tools import get_club_id_mapping
import sqlite3 as sql
import pandas as pd
import time
import threading


def update_team_stats_table(league, matchday):
    league_paths = {
        'mls': r'N:\01_Tracking-Data\Season_23-24\1 - MLS',
        'bl1': r'N:\01_Tracking-Data\Season_23-24\51 - Bundesliga 1_BL',
        'bl2': r'N:\01_Tracking-Data\Season_23-24\52 - 2.Bundesliga 2_BL',
        'eredivisie': r'N:\01_Tracking-Data\Season_23-24\9 - Eredivisie',
        'ekstraklasa': r'N:\01_Tracking-Data\Season_23-24\55 - Ekstraklasa'
    }

    if league not in league_paths:
        messagebox.showerror("Error", "Unsupported league selected")
        return

    data_path = Path(league_paths[league])
    start_time = time.time()

    def update_in_background():
        if matchday != '-':
            data_path_matchday = data_path / f'MD{matchday}'
            if not data_path_matchday.exists():
                messagebox.showerror("Error", f"Matchday {matchday} data does not exist for league {league}")
                return

            for match in data_path_matchday.iterdir():
                if match.is_dir():
                    start_time_match = time.time()
                    create_team_stats_table(league, match)
                    print(f"Processed {match} in {time.time() - start_time_match:.2f} seconds")

            messagebox.showinfo("Success", f"Database updated for league {league}, matchday {matchday}")
        else:
            for md in data_path.glob('MD*'):
                if md.is_dir() and 'MD' in md.name:
                    print(md)
                    for match in md.iterdir():
                        if match.is_dir():
                            start_time_match = time.time()
                            create_team_stats_table(league, match)
                            print(f"Processed {match} in {time.time() - start_time_match:.2f} seconds")

            messagebox.showinfo("Success", f"Database updated for the complete season of {league}")

        print(f"DB has been updated in {time.time() - start_time:.2f} seconds")

    # Create a thread for the background task
    thread = threading.Thread(target=update_in_background)
    thread.start()


def show_data_in_popup(data):
    # Create a new pop-up window
    popup = tk.Toplevel()
    popup.title("Data")

    # Create a Text widget to display the data
    text = tk.Text(popup, wrap='none')
    text.pack(expand=True, fill='both')

    # Insert the data into the Text widget
    text.insert(tk.END, data.to_string(index=False))

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(popup, orient='vertical', command=text.yview)
    scrollbar.pack(side='right', fill='y')
    text.configure(yscrollcommand=scrollbar.set)


def fetch_team_stats(league, season, team_id):
    db_path = f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db'
    with sql.connect(db_path) as conn:
        query = f"SELECT * FROM 'team_stats{team_id}' WHERE Season = {season}"
        team_stats = pd.read_sql_query(query, conn).sort_values(by='Matchday', ascending=True)
        show_data_in_popup(team_stats)


def fetch_player_stats(league, season, player_id):
    db_path = f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db'
    with sql.connect(db_path) as conn:
        query = f"SELECT * FROM 'player_stats' WHERE DlProviderID = {player_id} AND Season = {season}"
        player_stats = pd.read_sql_query(query, conn).sort_values(by=['Matchday'], ascending=True)

        # Drop the 'DlProviderID' column
        player_stats = player_stats.drop(columns=['DlProviderID'])

        show_data_in_popup(player_stats)


def create_avg_stats(league, season):
    team_info_path = Path(f'N:\\07_QC\\Alex\\Databases\\Team_Infos\\{league.upper()}')
    club_mapping = get_club_id_mapping(team_info_path, league=league)
    create_avg_stats_table(club_mapping, league=league, season=season, db_update=True, data=True)
    messagebox.showinfo("Success", f"Average stats table created for league {league}, season {season}")


def main():
    def toggle_advanced():
        if advanced_frame.winfo_viewable():
            advanced_frame.grid_remove()
            toggle_button.config(text="Show Advanced Functions")
        else:
            advanced_frame.grid()
            toggle_button.config(text="Hide Advanced Functions")

    def on_matchday_update_click():
        league = league_var.get()
        matchday = matchday_entry.get()
        update_team_stats_table(league, matchday)

    def on_season_update_click():
        league = league_var.get()
        matchday = matchday_entry.get()
        update_team_stats_table(league, matchday='-')

    def on_fetch_team_click():
        league = league_var.get()
        season = season_entry.get()
        team_id = team_id_entry.get()
        fetch_team_stats(league, season, team_id)

    def on_fetch_player_click():
        league = league_var.get()
        season = season_entry.get()
        player_id = player_id_entry.get()
        fetch_player_stats(league, season, player_id)

    def on_create_avg_stats_click():
        league = league_var.get()
        season = season_entry.get()
        create_avg_stats(league, season)

    root = tk.Tk()
    root.title("Database Manager")

    league_var = tk.StringVar()

    ttk.Label(root, text="League").grid(column=0, row=0, padx=10, pady=5)
    league_menu = ttk.Combobox(root, textvariable=league_var)
    league_menu['values'] = ('mls', 'bl1', 'bl2', 'eredivisie', 'ekstraklasa')
    league_menu.grid(column=1, row=0, padx=10, pady=5)
    league_menu.current(0)

    ttk.Label(root, text="Matchday").grid(column=0, row=1, padx=10, pady=5)
    matchday_entry = ttk.Entry(root)
    matchday_entry.grid(column=1, row=1, padx=10, pady=5)

    ttk.Button(root, text="Update Matchday", command=on_matchday_update_click).grid(column=0, row=2, padx=10, pady=5,
                                                                             columnspan=1)

    ttk.Button(root, text="Update Season", command=on_season_update_click).grid(column=1, row=2, padx=10, pady=5,
                                                                             columnspan=1)

    toggle_button = ttk.Button(root, text="Show Advanced Functions", command=toggle_advanced)
    toggle_button.grid(column=0, row=3, padx=10, pady=5, columnspan=2)

    advanced_frame = ttk.Frame(root)

    ttk.Label(advanced_frame, text="Season").grid(column=0, row=0, padx=10, pady=5)
    season_entry = ttk.Entry(advanced_frame)
    season_entry.grid(column=1, row=0, padx=10, pady=5)

    ttk.Label(advanced_frame, text="Team ID").grid(column=0, row=1, padx=10, pady=5)
    team_id_entry = ttk.Entry(advanced_frame)
    team_id_entry.grid(column=1, row=1, padx=10, pady=5)

    ttk.Button(advanced_frame, text="Fetch Team Stats", command=on_fetch_team_click).grid(column=0, row=2, padx=10,
                                                                                          pady=5, columnspan=2)

    ttk.Label(advanced_frame, text="Player ID").grid(column=0, row=3, padx=10, pady=5)
    player_id_entry = ttk.Entry(advanced_frame)
    player_id_entry.grid(column=1, row=3, padx=10, pady=5)

    ttk.Button(advanced_frame, text="Fetch Player Stats", command=on_fetch_player_click).grid(column=0, row=4, padx=10,
                                                                                              pady=5, columnspan=2)

    ttk.Button(advanced_frame, text="Create Avg Stats", command=on_create_avg_stats_click).grid(column=0, row=5,
                                                                                                padx=10, pady=5,
                                                                                                columnspan=2)

    advanced_frame.grid(column=0, row=4, padx=10, pady=5, columnspan=2)
    advanced_frame.grid_remove()

    root.mainloop()


if __name__ == "__main__":
    main()
