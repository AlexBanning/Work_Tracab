import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from TracabModules.Internal.database import create_team_stats_table, print_stats_table, create_avg_stats_table
from TracabModules.Internal.tools import get_club_id_mapping
import logging
import sqlite3 as sql
import pandas as pd


class StatsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stats Collection and Analysis")
        self.geometry("600x400")

        self.setup_ui()
        self.setup_logging()

        # Initialize logging window
        self.log_window = None

    def setup_logging(self):
        self.logger = logging.getLogger("StatsLogger")
        self.logger.setLevel(logging.INFO)

        # Create a file handler
        self.logfile = 'stats_log.txt'
        file_handler = logging.FileHandler(self.logfile)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def setup_ui(self):
        # Title
        tk.Label(self, text="Stats DB Handler", font=("Helvetica", 16)).pack(pady=10)

        # League selection
        tk.Label(self, text="Select League:").pack(pady=5)
        self.league = tk.StringVar()
        ttk.Combobox(self, textvariable=self.league, values=["mls", 'bl1', 'bl2']).pack(pady=5)

        # Matchday selection
        tk.Label(self, text="Select Matchday:").pack(pady=5)
        self.matchday_choice = tk.StringVar()
        self.matchday_combobox = ttk.Combobox(self, textvariable=self.matchday_choice, values=["-"])
        self.matchday_combobox.pack(pady=5)

        # Update matchdays button
        tk.Button(self, text="Load Matchdays", command=lambda: self.load_matchdays(self.league.get())).pack(pady=5)

        # Update DB button
        tk.Button(self, text="Update DB", command=self.process_update).pack(pady=5)

        # Generate League Stats button
        tk.Button(self, text="Generate League Stats", command=self.generate_league_stats).pack(pady=5)

        # Generate Printable Table button
        tk.Label(self, text="Select KPI:").pack(pady=5)
        self.kpi_choice = tk.StringVar()
        ttk.Combobox(self, textvariable=self.kpi_choice, values=["Total Distance", "Num. SpeedRuns", "Num. Sprints"]
                     ).pack(pady=5)
        tk.Label(self, text="Select Season:").pack(pady=5)
        self.season = tk.StringVar()
        tk.Entry(self, textvariable=self.season).pack(pady=5)
        tk.Button(self, text="Generate Printable Table", command=self.generate_printable_table).pack(pady=5)

        # Toggle Logging Window button
        tk.Button(self, text="Toggle Logging Window", command=self.toggle_logging_window).pack(pady=5)


    def load_matchdays(self, league):
        if league == 'mls':
            data_path = Path(r'N:\01_Tracking-Data\Season_23-24\1 - MLS')
        elif league == 'bl1':
            data_path = Path(r'N:\01_Tracking-Data\Season_23-24\51 - Bundesliga 1_BL')
        elif league == 'bl2':
            data_path = Path(r'N:\01_Tracking-Data\Season_23-24\52 - 2.Bundesliga 2_BL')
        existing_md_list = [p.name for p in data_path.iterdir() if p.is_dir() and 'MD' in p.name]

        # Define a custom sorting key function
        def sort_key(md):
            return int(md[2:])  # Convert the string to an integer, ignoring the 'MD' part

        # Sort the list using the custom key function
        sorted_md_list = sorted(existing_md_list, key=sort_key)

        self.matchday_combobox['values'] = ['-'] + sorted_md_list

    def process_update(self):
        league_choice = self.league.get()
        choice = self.matchday_choice.get()

        if league_choice and choice:
            if league_choice == 'bl1':
                league = '51 - Bundesliga 1_BL'
            elif league_choice == 'bl2':
                league = '52 - 2.Bundesliga 2_BL'
            elif league_choice == 'mls':
                league = '1 - MLS'
            if choice == '-':
                data_path = Path(fr'N:\01_Tracking-Data\Season_23-24\{league}')
                for md in data_path.iterdir():
                    if md.is_dir() and 'MD' in md.name:
                        for match in md.iterdir():
                            self.logger.info(f"Processing match: {match}")
                            create_team_stats_table(league=league_choice, match_folder=match)
            else:
                data_path = Path(fr'N:\01_Tracking-Data\Season_23-24\{league}\{choice}')
                for match in data_path.iterdir():
                    self.logger.info(f"Processing match: {match}")
                    create_team_stats_table(league=league_choice, match_folder=match)

            messagebox.showinfo("Success", "Data processed successfully!")
        else:
            messagebox.showwarning("Input Error", "Please select a league and a matchday.")

    def generate_league_stats(self):
        league = self.league.get()
        season = self.season.get()
        if league:
            team_info_path = Path(r'N:\07_QC\Alex\Databases\Team_Infos\MLS')
            club_mapping = get_club_id_mapping(team_info_path, league=league)
            create_avg_stats_table(club_mapping, league=league, season=season, db_update=True, data=True)
            messagebox.showinfo("Success", "League stats generated successfully!")
        else:
            messagebox.showwarning("Input Error", "Please select a league.")

    def generate_printable_table(self):
        league = self.league.get()
        kpi = self.kpi_choice.get()
        season = self.season.get()
        if league:
            print_stats_table(league=league, kpi=kpi, season=season,
                              logo_path=fr'C:\Users\a.banning\PycharmProjects\Work_Tracab\TeamLogos\{league.upper()}_Logos')
            messagebox.showinfo("Success", "Printable table generated successfully!")
        else:
            messagebox.showwarning("Input Error", "Please select a league.")

    def toggle_logging_window(self):
        if self.log_window:
            self.log_window.destroy()
            self.log_window = None
        else:
            self.create_logging_window()

    def create_logging_window(self):
        self.log_window = tk.Toplevel(self)
        self.log_window.title("Logging Window")
        self.log_window.geometry("400x300")

        # Scrolled text widget to display log messages
        self.log_text = scrolledtext.ScrolledText(self.log_window, wrap=tk.WORD)
        self.log_text.pack(expand=True, fill="both")

        # Read log file and display content
        with open(self.logfile, 'r') as f:
            log_content = f.read()
            self.log_text.insert(tk.END, log_content)


if __name__ == "__main__":
    app = StatsApp()
    app.mainloop()
