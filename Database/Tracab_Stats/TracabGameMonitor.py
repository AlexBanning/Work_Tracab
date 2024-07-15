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
from TracabModules.Internal.database import DataFetcher
import logging


class TracabGameMonitor:
    def __init__(self):
        self.leagues = ['BL1', 'BL2', 'MLS', 'Eredivisie', 'Ekstraklasa']

        self.root = tk.Tk()
        self.root.title("Tracab GameMonitor")
        # Load Tracab Icon
        # exe_dir = getattr(sys, '_MEIPASS', os.getcwd())
        # self.root.iconbitmap(os.path.join(exe_dir, "Tracab.ico"))
        # Set Background colour
        self.root.configure(bg='#2F4F4F')

        # Adjust the size of the GUI window
        self.root.geometry("700x250")

        # Create a frame to contain the labels and button
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
        self.game_id_var = tk.StringVar(self.root)
        self.game_id_entry = tk.Entry(self.center_frame, textvariable=self.game_id_var)
        self.game_id_entry.grid(row=1, column=1, padx=5, pady=2, sticky="nw")

        # Input field for entering the SeasonID
        tk.Label(self.center_frame, text="Enter SeasonID:", fg="#98FB98", bg="#2F4F4F").grid(row=2, column=0, padx=5,
                                                                                             pady=2, sticky="nw")
        self.season_id_var = tk.StringVar(self.root)
        self.season_id_entry = tk.Entry(self.center_frame, textvariable=self.season_id_var)
        self.season_id_entry.grid(row=2, column=1, padx=5, pady=2, sticky="nw")

        # Button to fetch team and player data
        self.fetch_button = tk.Button(self.center_frame, text="Get Data", command=self.fetch_data)
        self.fetch_button.grid(row=3, column=0, columnspan=2, pady=5, sticky="nw")

        # Create a frame to contain the TreeView for displaying dataframes
        self.dataframe_frame = tk.Frame(self.root)
        self.dataframe_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.dataframe_frame.configure(bg='#2F4F4F')

        # Adjust the window geometry
        self.adjust_window_size()

        self.root.mainloop()

    def fetch_data(self):
        league = self.league_var.get()
        game_id = self.game_id_var.get()
        season = self.season_id_var.get()

        # Replace with your function to fetch highspeed dataframes based on home_team and away_team
        try:
            fetcher = DataFetcher(game_id=game_id, league=league, season=season)
            home_row, away_row, home_name, away_name, home_highspeeds, away_highspeeds = fetcher.fetch_data()

            # Test labels for team values
            tk.Label(self.center_frame, text=home_name, fg="#98FB98", bg="#2F4F4F", font=("Helvetica", 10, "bold")
                     ).grid(row=4, column=0, padx=5, pady=2, sticky="nw")
            tk.Label(self.center_frame, text=away_name, fg="#98FB98", bg="#2F4F4F", font=("Helvetica", 10, "bold")
                     ).grid(row=4, column=1, padx=5, pady=2, sticky="nw")

            # Center the label horizontally
            self.center_frame.grid_columnconfigure(0, weight=1)
            self.center_frame.grid_columnconfigure(1, weight=1)

            # Display total distance
            tk.Label(self.center_frame, text=f'Avg. Distance: {home_row['Total Distance'].iloc[0]}km',
                     fg="#98FB98", bg="#2F4F4F").grid(row=5, column=0, padx=5, pady=2, sticky="nw")
            tk.Label(self.center_frame, text=f'Avg. Distance: {away_row['Total Distance'].iloc[0]}km',
                     fg="#98FB98", bg="#2F4F4F").grid(row=5, column=1, padx=5, pady=2, sticky="nw")

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
            self.display_dataframe(home_highspeeds, self.home_treeview, team_indicator='Home')
            self.display_dataframe(away_highspeeds, self.away_treeview, team_indicator='Away')

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

    def display_dataframe(self, dataframe, treeview, team_indicator):
        # Clear previous data
        treeview.delete(*treeview.get_children())
        new_names = {'ShirtNumber': '#', 'HighSpeed': 'Speed'}
        dataframe = dataframe.rename(columns=new_names)
        # Display dataframe columns as headers
        treeview["columns"] = list(dataframe.columns)
        for col in dataframe.columns:
            if col == 'Name':
                treeview.heading(col, text=team_indicator)
            else:
                treeview.heading(col, text=col)

        # Adjust column widths based on content
        for col in dataframe.columns:
            if col == 'Name':
                treeview.column(col, width=max(120, len(col) * 20))  # Adjust width based on column name length
            elif col == '#':
                treeview.column(col, width=25)  # Adjust width based on column name length
            else:
                treeview.column(col, width=len(col) * 10)  # Adjust width based on column name length

        # Insert the data
        for index, row in dataframe.iterrows():
            values = list(row)
            treeview.insert('', 'end', text='', values=values)

        # Remove the first column completely
        treeview["show"] = "headings"


def main() -> None:
    TracabGameMonitor()


if __name__ == '__main__':
    main()
