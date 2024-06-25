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
import sys, os

class TracabGameMonitor:
    def __init__(self):
        self.leagues = ['1.Bundesliga', '2.Bundesliga', 'MLS', 'Eredivisie', 'Ekstraklasa']

        self.root = tk.Tk()
        self.root.title("TracabGameMonitor")
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
        tk.Label(self.center_frame, text="Select League:", fg="#98FB98", bg="#2F4F4F").grid(row=0, column=0, padx=5, pady=2,
                                                                                        sticky="nw")
        self.league_var = tk.StringVar(self.root)
        self.league_dropdown = ttk.Combobox(self.center_frame, textvariable=self.league_var, values=self.leagues, state='readonly')
        self.league_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="nw")

        # Input field for entering the GameID
        tk.Label(self.center_frame, text="Enter GameID:", fg="#98FB98", bg="#2F4F4F").grid(row=1, column=0, padx=5, pady=2, sticky="nw")
        self.gameid_var = tk.StringVar(self.root)
        self.gameid_entry = tk.Entry(self.center_frame, textvariable=self.gameid_var)
        self.gameid_entry.grid(row=1, column=1, padx=5, pady=2, sticky="nw")

        # Button to confirm input
        self.confirm_button = tk.Button(self.center_frame, text="Confirm", command=self.show_match_data)
        self.confirm_button.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        # Adjust the window geometry
        self.adjust_window_size()

        self.root.mainloop()

    def adjust_window_size(self):
        self.root.update_idletasks()  # Update the GUI to finish arranging widgets
        width = self.root.winfo_reqwidth()  # Get the required width of the GUI
        height = self.root.winfo_reqheight()  # Get the required height of the GUI
        self.root.geometry(f"{width}x{height}")  # Set the GUI window size

    def show_match_data(self):
        selected_league = self.league_var.get()
        game_id = self.gameid_var.get()
        # Close the current window
        self.root.destroy()

        # Open a new window with match data
        self.match_data_window = tk.Tk()
        self.match_data_window.title(f"Match Data for GameID {game_id}")
        self.match_data_window.configure(bg='#2F4F4F')

        # Display match data (this is a placeholder, you should replace it with actual match data)
        tk.Label(self.match_data_window, text=f"League: {selected_league}", fg="#98FB98", bg="#2F4F4F").pack(padx=10,
                                                                                                             pady=10)
        tk.Label(self.match_data_window, text=f"GameID: {game_id}", fg="#98FB98", bg="#2F4F4F").pack(padx=10, pady=10)

        # Add actual match data here
        # ...

        self.match_data_window.mainloop()

apptest = TracabGameMonitor()