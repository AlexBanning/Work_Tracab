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

    'mls': r'N:\01_Tracking-Data\Season_23-24\1 - MLS',
    'bl1': r'N:\01_Tracking-Data\Season_24-25\51 - Bundesliga 1_BL',
    'bl2': r'N:\01_Tracking-Data\Season_24-25\52 - 2.Bundesliga 2_BL',
    'eredivisie': r'N:\01_Tracking-Data\Season_24-25\9 - Eredivisie',
    'ekstraklasa': r'N:\01_Tracking-Data\Season_24-25\55 - Ekstraklasa'}

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