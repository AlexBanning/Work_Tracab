import tkinter as tk
from tkinter import ttk, font as tkfont
from TracabModules.External.DataHub import get_dfl_highspeeds, BL1, BL2


class HighSpeedGUI:
    def __init__(self):
        self.leagues = ['1.Bundesliga', '2.Bundesliga']
        self.teams = {
            '1.Bundesliga': BL1,
            '2.Bundesliga': BL2
        }

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

        # Dropdown list for selecting the league
        tk.Label(self.center_frame, text="Select League:", fg="#98FB98", bg="#2F4F4F").grid(row=0, column=0, padx=5, pady=2,
                                                                                        sticky="nw")
        self.league_var = tk.StringVar(self.root)
        self.league_dropdown = ttk.Combobox(self.center_frame, textvariable=self.league_var, values=self.leagues, state='readonly')
        self.league_dropdown.grid(row=0, column=1, padx=5, pady=2, sticky="nw")

        # Dropdown lists for selecting home and away teams
        tk.Label(self.center_frame, text="Home Team:", fg="#98FB98", bg="#2F4F4F").grid(row=1, column=0, padx=5, pady=2,
                                                                                        sticky="nw")
        self.home_team_var = tk.StringVar(self.root)
        self.home_team_dropdown = ttk.Combobox(self.center_frame, textvariable=self.home_team_var, values=[])
        self.home_team_dropdown.grid(row=1, column=1, padx=5, pady=2, sticky="nw")

        tk.Label(self.center_frame, text="Away Team:", fg="#98FB98", bg="#2F4F4F").grid(row=2, column=0, padx=5, pady=2,
                                                                                        sticky="nw")
        self.away_team_var = tk.StringVar(self.root)
        self.away_team_dropdown = ttk.Combobox(self.center_frame, textvariable=self.away_team_var, values=[])
        self.away_team_dropdown.grid(row=2, column=1, padx=5, pady=2, sticky="nw")

        # Button to fetch highspeed dataframes
        self.fetch_button = tk.Button(self.center_frame, text="Fetch Highspeeds", command=self.fetch_highspeeds)
        self.fetch_button.grid(row=3, column=0, columnspan=2, pady=0, sticky="nw")

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

        self.league_dropdown.bind("<<ComboboxSelected>>", self.update_team_dropdowns)
        self.root.mainloop()

    def update_team_dropdowns(self, event):
        selected_league = self.league_var.get()
        teams_for_selected_league = self.teams.get(selected_league, [])
        self.home_team_dropdown.config(values=teams_for_selected_league)
        self.away_team_dropdown.config(values=teams_for_selected_league)

    def fetch_highspeeds(self):
        league = self.league_var.get()
        home_team = self.home_team_var.get()
        away_team = self.away_team_var.get()

        # Replace with your function to fetch highspeed dataframes based on home_team and away_team
        home_df, away_df = get_dfl_highspeeds(league, home_team, away_team)
        # home_df = bayern_df
        # away_df = leverkusen_df

        if home_df is not None and away_df is not None:
            # Display highspeed dataframes in the text widgets
            self.display_dataframe(home_df, self.home_df_text)
            self.display_dataframe(away_df, self.away_df_text)

            # Update headers
            self.update_headers(home_team, away_team)

            # Show the text widgets
            self.home_df_text.grid()
            self.away_df_text.grid()
            # Adjust the window geometry
            self.adjust_window_size()

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

