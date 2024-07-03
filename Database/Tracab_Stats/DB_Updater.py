import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from TracabModules.Internal.database import create_team_stats_table, print_stats_table, create_avg_stats_table
from TracabModules.Internal.tools import get_club_id_mapping
import sqlite3 as sql
import pandas as pd
import time
import threading
import numpy as np
import os, sys

LEAGUE_MAPPING = {
    'MLS': 'mls',
    'Bundesliga': 'bl1',
    '2.Bundesliga': 'bl2',
    'Eredivisie': 'eredivisie',
    'Ekstraklasa': 'ekstraklasa'
}


# Function to update team stats table
def update_team_stats_table(data_path, league, log_text_widget):
    start_time = time.time()

    # Process based on whether it's a single matchday or league folder
    if "MD" in data_path.name:  # Single matchday folder selected
        for match in data_path.iterdir():
            if match.is_dir():
                start_time_match = time.time()
                create_team_stats_table(league, match, log_text_widget)
                log_text_widget.insert(tk.END, f"\nProcessed {match} in {time.time() - start_time_match:.2f} seconds\n")
                log_text_widget.yview(tk.END)  # Scroll to the end of the text widget

        messagebox.showinfo("Success", f"Database updated for {data_path.parts[-3]}, matchday {data_path.name}")
    else:  # League folder selected
        for md in data_path.glob('MD*'):
            if md.is_dir():
                for match in md.iterdir():
                    if match.is_dir():
                        start_time_match = time.time()
                        create_team_stats_table(league, match, log_text_widget)
                        log_text_widget.insert(tk.END, f"\nProcessed {match} in {time.time() - start_time_match:.2f} seconds\n")
                        log_text_widget.yview(tk.END)  # Scroll to the end of the text widget

        messagebox.showinfo("Success", f"Database updated for the complete season of {data_path.parts[-1]}")

    log_text_widget.insert(tk.END, f"DB has been updated in {time.time() - start_time:.2f} seconds\n")


# Function to display the database data in a table
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


# Function to fetch and display the data for a team
def fetch_team_stats(league, season, team_id):
    db_path = f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db'
    with sql.connect(db_path) as conn:
        query = f"SELECT * FROM 'team_stats{team_id}' WHERE Season = {season}"
        team_stats = pd.read_sql_query(query, conn).sort_values(by='Matchday', ascending=True)
        team_stats['Total Distance'] = np.round(team_stats['Total Distance'] / 1000, 2)
        show_data_in_popup(team_stats)


# Function to fetch and display the data for a player
def fetch_player_stats(league, season, player_id):
    db_path = f'N:\\07_QC\\Alex\\Databases\\{league}_stats.db'
    with sql.connect(db_path) as conn:
        query = f"SELECT * FROM 'player_stats' WHERE DlProviderID = {player_id} AND Season = {season}"
        player_stats = pd.read_sql_query(query, conn).sort_values(by=['Matchday'], ascending=True)

        # Drop the 'DlProviderID' column
        player_stats = player_stats.drop(columns=['DlProviderID'])
        player_stats['Total Distance'] = np.round(player_stats['Total Distance'] / 1000, 2)

        show_data_in_popup(player_stats)


# Function to create the avg stats table for a league
def create_avg_stats(league, season):
    club_mapping = get_club_id_mapping(league=league)
    create_avg_stats_table(club_mapping, league=league, season=season, db_update=True, data=True)
    messagebox.showinfo("Success", f"Average stats table created for {league.upper()}, season {season}")


# Function to create the stats reports
def create_stats_report(league, season, log_text_widget):
    for kpi in ['Total Distance', 'Num. Sprints', 'Num. SpeedRuns']:
        print_stats_table(league=league, kpi=kpi, season=season,
                          logo_path=fr'N:\07_QC\Alex\Databases\TeamLogos\{league.upper()}_Logos\{season}',
                          log=log_text_widget)
    messagebox.showinfo("Success", f"Stats-Reports created for {league.upper()}, season {season}")


# Implement threading so the GUI remains responsive while the code is exeucted
def update_in_background(data_path, league, log_text_widget):
    threading.Thread(target=update_team_stats_table, args=(data_path, league, log_text_widget)).start()


# Implement threading so the GUI remains responsive while the code is exeucted
def report_in_background(league, season, log_text_widget):
    threading.Thread(target=create_stats_report, args=(league, season, log_text_widget)).start()


def main():
    def toggle_advanced():
        if advanced_frame.winfo_viewable():
            advanced_frame.grid_remove()
            toggle_button.config(text="Show Advanced Functions")
        else:
            advanced_frame.grid()
            toggle_button.config(text="Hide Advanced Functions")

    def select_folder():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            data_path_var.set(folder_selected)
        ttk.Label(root, text="Selected Path:").grid(column=0, row=2, padx=10, pady=5)
        selected_path_label = ttk.Label(root, textvariable=data_path_var)
        selected_path_label.grid(column=1, row=2, padx=5, pady=5)

    def on_update_click():
        data_path = Path(data_path_var.get())
        # Determine league based on data_path
        league = LEAGUE_MAPPING.get(data_path.parts[3].split()[2], None)
        if league is None:
            log_text_widget.insert(tk.END, "Invalid league selected.\n")
            return
        # # Determine the season based on data_path
        # if league == 'mls':
        #     season = f'20{data_path.parts[2].split('_')[1][-2:]}'
        # else:
        #     season = f'20{data_path.parts[2].split('_')[1][:2]}'
        if data_path:
            update_in_background(data_path, league, log_text_widget)
            # create_avg_stats(league, season)

    def on_fetch_team_click():
        league = LEAGUE_MAPPING[league_var.get()]
        season = season_entry.get()
        team_id = team_id_entry.get()
        fetch_team_stats(league, season, team_id)

    def on_fetch_player_click():
        league = LEAGUE_MAPPING[league_var.get()]
        season = season_entry.get()
        player_id = player_id_entry.get()
        fetch_player_stats(league, season, player_id)

    def on_create_avg_stats_click():
        league = LEAGUE_MAPPING[league_var.get()]
        season = season_entry.get()
        create_avg_stats(league, season)

    def on_create_stats_report_click():
        league = LEAGUE_MAPPING[league_var.get()]
        season = season_entry.get()
        report_in_background(league, season, log_text_widget)

    def toggle_log_window():
        if log_frame.winfo_viewable():
            log_frame.grid_remove()
            log_toggle_button.config(text="Show Log")
        else:
            log_frame.grid()
            log_toggle_button.config(text="Hide Log")

    root = tk.Tk()
    root.title("Database Manager")
    # Load Tracab Icon
    exe_dir = getattr(sys, '_MEIPASS', os.getcwd())
    root.iconbitmap(os.path.join(exe_dir, "Tracab.ico"))
    # Set Background colour
    root.configure(bg='#2F4F4F')

    league_var = tk.StringVar()
    data_path_var = tk.StringVar()

    ttk.Button(root, text="Select League/Matchday", command=select_folder).grid(column=0, row=1, padx=10, pady=5,
                                                                                columnspan=2)

    ttk.Button(root, text="Update Database", command=on_update_click).grid(column=0, row=3, padx=10, pady=5,
                                                                           columnspan=2)

    log_toggle_button = ttk.Button(root, text="Show Log", command=toggle_log_window)
    log_toggle_button.grid(column=1, row=4, padx=10, pady=5, columnspan=1)

    toggle_button = ttk.Button(root, text="Show Advanced Functions", command=toggle_advanced)
    toggle_button.grid(column=0, row=4, padx=10, pady=5, columnspan=1)

    advanced_frame = ttk.Frame(root)

    ttk.Label(advanced_frame, text="League").grid(column=0, row=0, padx=10, pady=5)
    league_menu = ttk.Combobox(advanced_frame, textvariable=league_var)
    league_menu['values'] = ('MLS', '1.Bundesliga', '2.Bundesliga', 'Eredivisie', 'Ekstraklasa')
    league_menu.grid(column=1, row=0, padx=10, pady=5)
    league_menu.current(0)

    ttk.Label(advanced_frame, text="Season").grid(column=0, row=1, padx=10, pady=5)
    season_entry = ttk.Entry(advanced_frame)
    season_entry.grid(column=1, row=1, padx=10, pady=5)

    ttk.Label(advanced_frame, text="Team ID").grid(column=0, row=2, padx=10, pady=5)
    team_id_entry = ttk.Entry(advanced_frame)
    team_id_entry.grid(column=1, row=2, padx=10, pady=5)

    ttk.Button(advanced_frame, text="Fetch Team Stats", command=on_fetch_team_click).grid(column=0, row=4, padx=10,
                                                                                          pady=5, columnspan=2)

    ttk.Label(advanced_frame, text="Player ID").grid(column=0, row=3, padx=10, pady=5)
    player_id_entry = ttk.Entry(advanced_frame)
    player_id_entry.grid(column=1, row=3, padx=10, pady=5)

    ttk.Button(advanced_frame, text="Fetch Player Stats", command=on_fetch_player_click).grid(column=0, row=5, padx=10,
                                                                                              pady=5, columnspan=2)

    ttk.Button(advanced_frame, text="Create Avg Stats", command=on_create_avg_stats_click).grid(column=0, row=6,
                                                                                                padx=10, pady=5,
                                                                                                columnspan=2)

    ttk.Button(advanced_frame, text="Create Stats-Reports", command=on_create_stats_report_click).grid(column=0, row=7,
                                                                                                       padx=10, pady=5,
                                                                                                       columnspan=2)

    advanced_frame.grid(column=0, row=3, padx=10, pady=5, columnspan=2)
    advanced_frame.grid_remove()

    log_frame = ttk.Frame(root)
    log_text_widget = ScrolledText(log_frame, width=80, height=20, state='normal')
    log_text_widget.pack(expand=True, fill='both')

    log_frame.grid(column=0, row=6, padx=10, pady=5, columnspan=2)
    log_frame.grid_remove()

    root.mainloop()


if __name__ == "__main__":
    main()
