import tkinter as tk
from tkinter import ttk, font as tkfont
import pandas as pd
from TracabModules.External.DataHub import DataHub


# Sample data for Bayern Munich players (Approximate top speed values in km/h)
bayern_players = [
    "Lewandowski", "Neuer", "Müller", "Kimmich", "Goretzka",
    "Davies", "Süle", "Sané", "Boateng", "Coman",
    "Alaba", "Hernández", "Pavard", "Gnabry", "Martínez",
    "Musiala", "Choupo-Moting", "Roca", "Richards", "Zirkzee",
    "Sarr"
]

bayern_speeds = [
    33.5, 33.0, 32.3, 32.8, 33.2,
    35.0, 31.5, 34.7, 32.0, 34.0,
    31.8, 32.5, 32.2, 34.3, 32.7,
    33.5, 32.0, 31.0, 32.5, 33.8,
    32.5
]

bayern_data = {
    'Player': bayern_players,
    'Top Speed': bayern_speeds
}

bayern_df = pd.DataFrame(bayern_data)

# Sample data for Bayer Leverkusen players (Approximate top speed values in km/h)
leverkusen_players = [
    "Hradecky", "Schick", "Diaby", "Amiri", "Wirtz",
    "Tapsoba", "Araujo", "Palacios", "Bender", "Frantz",
    "Bell", "Grill", "Weiser", "Alario", "Sinkgraven",
    "Dragovic", "Baumgartlinger", "Frimpong", "Paulinho", "Aránguiz",
    "Bellarabi"
]

leverkusen_speeds = [
    32.8, 33.5, 33.7, 33.0, 33.4,
    31.5, 32.0, 32.7, 31.8, 32.5,
    30.0, 29.5, 31.2, 33.2, 32.0,
    30.5, 31.0, 33.0, 32.8, 32.0,
    32.5
]

leverkusen_data = {
    'Player': leverkusen_players,
    'Top Speed': leverkusen_speeds
}

leverkusen_df = pd.DataFrame(leverkusen_data)


datahub_download = DataHub()
season_id = datahub_download.season_id()
comp_id = datahub_download.sts_competition_id(tracab_id='51')
matchday_ids = datahub_download.matchday_ids(season_id, comp_id)
speeds = datahub_download.speeds(season_id, comp_id, matchday_ids['30'])

home = 'TSG Hoffenheim'
speeds_home = pd.DataFrame(
    list({f'{x['PlayerFirstName'][0]}. {x['PlayerLastName']}': x['Absolute'] for x in speeds.find_all('ListEntry')
          if x.contents[1]['TeamName'] == home}.items()), columns=['Name', 'Speed']
)

away = 'RB Leipzig'
speeds_away = pd.DataFrame(
    list({f'{x['PlayerFirstName'][0]}. {x['PlayerLastName']}': x['Absolute'] for x in speeds.find_all('ListEntry')
          if x.contents[1]['TeamName'] == away}.items()), columns=['Name', 'Speed']
)


class HighSpeedGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Highspeed Fetcher")
        self.root.iconbitmap("Tracab.ico")
        self.root.configure(bg='#2F4F4F')

        # Adjust the size of the GUI window
        self.root.geometry("700x250")

        # Create a frame to contain the labels and buttons
        self.center_frame = tk.Frame(self.root)
        self.center_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.center_frame.configure(bg='#2F4F4F')

        # Configure row and column weights for center_frame
        self.center_frame.grid_rowconfigure(0, weight=1)
        self.center_frame.grid_columnconfigure(0, weight=1)

        # Team name entries
        tk.Label(self.center_frame, text="Home Team:", fg="#98FB98", bg="#2F4F4F").grid(row=0, column=0, padx=5, pady=2,
                                                                                        sticky="nw")
        self.home_team_entry = tk.Entry(self.center_frame)
        self.home_team_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(self.center_frame, text="Away Team:", fg="#98FB98", bg="#2F4F4F").grid(row=1, column=0, padx=5, pady=2,
                                                                                        sticky="nw")
        self.away_team_entry = tk.Entry(self.center_frame)
        self.away_team_entry.grid(row=1, column=1, padx=5, pady=2, sticky="nw")

        # Button to fetch highspeed dataframes
        self.fetch_button = tk.Button(self.center_frame, text="Fetch Highspeeds", command=self.fetch_highspeeds)
        self.fetch_button.grid(row=2, column=0, columnspan=2, pady=0, sticky="nw")

        # Dataframes to display highspeeds
        self.home_df_text = tk.Text(self.center_frame, wrap=tk.WORD, height=10, width=35, relief='flat')
        self.home_df_text.grid(row=1, column=2, padx=(5,0), pady=0, sticky="nsew", columnspan=2)
        self.home_df_text.config(state=tk.DISABLED, fg="#98FB98" , bg=self.root.cget("bg"))
        self.home_df_text.grid_remove()

        # Vertical Scrollbar for home_df_text
        self.home_scrollbar = ttk.Scrollbar(self.center_frame, orient="vertical", command=self.home_df_text.yview)
        self.home_scrollbar.grid(row=1, column=4, pady=(0), sticky="nse")
        self.home_df_text.config(yscrollcommand=self.home_scrollbar.set)
        self.home_scrollbar.grid_remove()  # Hide the scrollbar initially

        self.away_df_text = tk.Text(self.center_frame, wrap=tk.WORD, height=10, width=35, relief='flat')
        self.away_df_text.grid(row=1, column=4, padx=0, pady=0, sticky="nsew", columnspan=2)
        self.away_df_text.config(state=tk.DISABLED, fg="#98FB98" , bg=self.root.cget("bg"))
        self.away_df_text.grid_remove()

        # Vertical Scrollbar for away_df_text
        self.away_scrollbar = ttk.Scrollbar(self.center_frame, orient="vertical", command=self.away_df_text.yview)
        self.away_scrollbar.grid(row=1, column=7, pady=(0, 2), sticky="nse")
        self.away_df_text.config(yscrollcommand=self.away_scrollbar.set)

        # Configure scrollbar style to match background color
        self.away_scrollbar.grid_remove()  # Hide the scrollbar initially

        # Adjust the window geometry
        self.adjust_window_size()

        self.root.mainloop()

    def fetch_highspeeds(self):
        home_team = self.home_team_entry.get()
        away_team = self.away_team_entry.get()

        # Replace with your function to fetch highspeed dataframes based on home_team and away_team
        home_df = bayern_df.sort_values(by='Top Speed', ascending=False).reset_index(drop=True)
        away_df = leverkusen_df.sort_values(by='Top Speed', ascending=False).reset_index(drop=True)

        if home_df is not None and away_df is not None:
            # Display highspeed dataframes in the text widgets
            self.display_dataframe(home_df, self.home_df_text)
            self.display_dataframe(away_df, self.away_df_text)

            # Update headers
            self.update_headers(home_team, away_team)

            # Show the text widgets
            self.home_df_text.grid()
            self.away_df_text.grid()
            # self.home_scrollbar.grid()
            # self.away_scrollbar.grid()
            # Adjust the window geometry
            self.adjust_window_size()

    def get_highspeed_dataframes(self, home_team, away_team):
        # Placeholder function to return sample dataframes
        home_df = pd.DataFrame({'Player': ['Player1', 'Player2'], 'Highspeed': [20, 22]})
        away_df = pd.DataFrame({'Player': ['PlayerA', 'PlayerB'], 'Highspeed': [21, 23]})
        return home_df, away_df

    def display_dataframe(self, df, text_widget):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, df.to_string(index=False))
        text_widget.config(state=tk.DISABLED)

    def adjust_window_size(self):
        self.root.update_idletasks()  # Update the GUI to finish arranging widgets
        width = self.root.winfo_reqwidth()  # Get the required width of the GUI
        height = self.root.winfo_reqheight()  # Get the required height of the GUI
        self.root.geometry(f"{width}x{height}")  # Set the GUI window size

    def update_headers(self, home_team, away_team):
        bold_font = tkfont.Font(weight='bold')
        self.home_df_text_header = tk.Label(self.center_frame, text=home_team, font=bold_font, fg="white", bg="#2F4F4F",
                                            anchor='center')
        self.home_df_text_header.grid(row=0, column=2, padx=5, pady=(0,5), sticky="nsew")

        self.away_df_text_header = tk.Label(self.center_frame, text=away_team, font=bold_font, fg="white", bg="#2F4F4F",
                                            anchor='center')
        self.away_df_text_header.grid(row=0, column=4, padx=5, pady=(0,5), sticky="nsew")


if __name__ == "__main__":
    HighSpeedGUI()
