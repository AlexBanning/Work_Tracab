import pandas as pd
from TracabModules.External.DataHub import DataHub
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import logging
import sys, os


class TracabStatsMonitor:
    def __init__(self):
        self.leagues = ['BL1', 'BL2']
        self.event_list = ['Offside']

        self.root = tk.Tk()
        self.root.title("DFL Event Fetcher")
        # Load Tracab Icon
        self.exe_dir = getattr(sys, '_MEIPASS', os.getcwd())
        self.root.iconbitmap(os.path.join(self.exe_dir, "Tracab.ico"))
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
        tk.Label(self.center_frame, text="Enter 3LC of the match:", fg="#98FB98", bg="#2F4F4F").grid(row=1, column=0, padx=5,
                                                                                           pady=2, sticky="nw")
        self.game_var = tk.StringVar(self.root)
        self.game_entry = tk.Entry(self.center_frame, textvariable=self.game_var)
        self.game_entry.grid(row=1, column=1, padx=5, pady=2, sticky="nw")
        #
        # Input field for entering the SeasonID
        tk.Label(self.center_frame, text="Select Event Type:", fg="#98FB98", bg="#2F4F4F").grid(row=2, column=0, padx=5,
                                                                                             pady=2, sticky="nw")
        self.event_var = tk.StringVar(self.root)
        self.event_dropdown = ttk.Combobox(self.center_frame, textvariable=self.event_var, values=self.event_list)
        self.event_dropdown.grid(row=2, column=1, padx=5, pady=2, sticky="nw")

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
        matches = pd.read_excel(os.path.join(self.exe_dir, f"{league}_HTF_Schedule.xlsx"), header=1)
        print(self.game_var.get())
        game_id = matches.loc[matches['3LC'] == self.game_var.get()]['DFL-MAT-ID'].values[0]
        print(game_id)
        event = self.event_var.get()

        datahub_download = DataHub()

        events_df = datahub_download.match_events(match_id=game_id, event=event)

        # # Replace with your function to fetch highspeed dataframes based on home_team and away_team
        # try:
        #     fetcher = DataFetcher(game_id=game_id, league=league, season=season)
        #     result = fetcher.fetch_data()
#
        #     if not result:
        #         raise DataFetchError("No data available. Please check again once lineups are available.")
#
        #     home_row, away_row, home_name, away_name, home_highspeeds, away_highspeeds = result
#
        #     # # Check and update or create label for home team name
        #     if hasattr(self, 'home_name_label'):
        #         self.home_name_label.config(text=home_name)
        #     else:
        #         self.home_name_label = tk.Label(self.center_frame, text=home_name, fg="#98FB98", bg="#2F4F4F",
        #                                         font=("Helvetica", 10, "bold"))
        #         self.home_name_label.grid(row=4, column=0, columnspan=2, padx=5, pady=2, sticky="w")
##
        #     # # Check and update or create label for away team name
        #     if hasattr(self, 'away_name_label'):
        #         self.away_name_label.config(text=away_name)
        #     else:
        #         self.away_name_label = tk.Label(self.center_frame, text=away_name, fg="#98FB98", bg="#2F4F4F",
        #                                         font=("Helvetica", 10, "bold"))
        #         self.away_name_label.grid(row=4, column=2, columnspan=2, padx=5, pady=2, sticky="w")
#
        #     # Center the labels horizontally
        #     self.center_frame.grid_columnconfigure(0, weight=1)
        #     self.center_frame.grid_columnconfigure(1, weight=1)
#
        #     # Assuming the values are already extracted from your data
        #     home_distance = home_row['Total Distance'].iloc[0]
        #     away_distance = away_row['Total Distance'].iloc[0]
        #     home_sprints = home_row['Num. Sprints'].iloc[0]
        #     away_sprints = away_row['Num. Sprints'].iloc[0]
        #     home_speedruns = home_row['Num. SpeedRuns'].iloc[0]
        #     away_speedruns = away_row['Num. SpeedRuns'].iloc[0]
#
        #     # Define the labels with mixed fonts
        #     def create_stat_row(label_attr_prefix, label_text, home_value, away_value, row):
        #         # Home Team Label
        #         home_label_name = f'{label_attr_prefix}_home_label'
        #         if hasattr(self, home_label_name):
        #             getattr(self, home_label_name).config(text=f"{home_value}")
        #         else:
        #             setattr(self, home_label_name,
        #                     tk.Label(self.center_frame, text=f"{home_value}", fg="#98FB98", bg="#2F4F4F",
        #                              font=("Helvetica", 10, "bold")))
        #             getattr(self, home_label_name).grid(row=row, column=1, sticky="w")
#
        #         # Away Team Label
        #         away_label_name = f'{label_attr_prefix}_away_label'
        #         if hasattr(self, away_label_name):
        #             getattr(self, away_label_name).config(text=f"{away_value}")
        #         else:
        #             setattr(self, away_label_name,
        #                     tk.Label(self.center_frame, text=f"{away_value}", fg="#98FB98", bg="#2F4F4F",
        #                              font=("Helvetica", 10, "bold")))
        #             getattr(self, away_label_name).grid(row=row, column=3, sticky="w")
#
        #         # Static Labels
        #         tk.Label(self.center_frame, text=f"{label_text}: ", fg="#98FB98", bg="#2F4F4F",
        #                  font=("Helvetica", 10)).grid(row=row, column=0, sticky="w")
        #         tk.Label(self.center_frame, text=f"{label_text}: ", fg="#98FB98", bg="#2F4F4F",
        #                  font=("Helvetica", 10)).grid(row=row, column=2, sticky="w")
#
        #     # Create rows for each stat
        #     create_stat_row("distance", "Distance", f"{home_distance}km", f"{away_distance}km", 5)
        #     create_stat_row("sprints", "Sprints", home_sprints, away_sprints, 6)
        #     create_stat_row("speedruns", "SpeedRuns", home_speedruns, away_speedruns, 7)
#
        # Check if Treeview widgets already exist, if not, create new ones
        if not hasattr(self, 'home_treeview'):
            # Create a TreeView to display dataframes
            self.home_treeview = ttk.Treeview(self.dataframe_frame, height=len(events_df))

            # Pack Treeview widgets into the frame
            self.home_treeview.pack(side="left", padx=5, pady=5)

            # Create a style object
            style = ttk.Style()

            # Configure Treeview style with desired background and foreground colors
            style.configure("Treeview", background='#2F4F4F',
                            foreground="#98FB98")  # Light gray background, black text color

            # Apply the style to the Treeview widgets
            self.home_treeview.configure(style="Treeview")

        # Otherwise, clear existing contents of Treeview widgets
        else:
            self.home_treeview.delete(*self.home_treeview.get_children())

        # Create a style object
        style = ttk.Style()

        # Configure Treeview style with desired background and foreground colors
        style.configure("Treeview", background='#2F4F4F',
                        foreground="#98FB98")  # Light gray background, black text color

        # Apply the style to the Treeview widgets
        self.home_treeview.configure(style="Treeview")

        # Pack Treeview widgets into the frame
        self.home_treeview.pack(side="left", padx=5, pady=5)
#
        # Display dataframes in TreeView
        self.display_dataframe(events_df, self.home_treeview)
#
        # Adjust the window geometry
        self.adjust_window_size()
    # except FileNotFoundError as e:
    #     error_msg = f"File not found: {e.filename}"
    #     logging.error(error_msg)
    #     messagebox.showerror("Error", error_msg)
#
        # except Exception as e:
        #     error_msg = f"An error occurred: {e}"
        #     logging.error(error_msg)
        #     messagebox.showerror("Error", error_msg)

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
            # if col == 'Name':
            #     treeview.heading(col, text=team_indicator)
            # else:
            treeview.heading(col, text=col)

        # Adjust column widths based on content
        for col in dataframe.columns:
            if col == 'Player':
                treeview.column(col, width=100)  # Adjust width based on column name length
            elif col == 'Minute':
                treeview.column(col, width=30)  # Adjust width based on column name length
            elif col == 'Team':
                treeview.column(col, width=40)  # Adjust width based on column name length

        # treeview.tag_configure('red', background='red', foreground='white')

        # Insert the data and recolour rows if the player's high speed is above 35 km/h
        for index, row in dataframe.iterrows():
            values = list(row)
            # Display dataframe rows
            # if row['Speed'] >= 35:
            #     treeview.insert('', 'end', text='', values=values, tags=('red',))
            # else:
            treeview.insert('', 'end', text='', values=values)

        # Remove the first column completely
        treeview["show"] = "headings"

    # def get_game_id(self):
    #     return self.game_id_var.get()
#
    # def get_vendor(self):
    #     if self.league_var.get() == 'BL2' or self.league_var.get() == 'BL1' or self.league_var.get() == 'MLS':
    #         vendor = '4'
    #         return vendor


def main() -> None:
    TracabStatsMonitor()


if __name__ == '__main__':
    main()
