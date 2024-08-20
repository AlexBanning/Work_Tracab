"""
Combine stats monitor and gateway monitor to be able to check the team's previous data but also the gateway status for
the running match
"""

from Database.Tracab_Stats.stats_monitor.TracabStatsMonitor import TracabStatsMonitor # Import the original StatsMonitor class
import tkinter as tk
from TracabModules.Internal.gateway import FeedStatusGUI

EXTR_VERS = '4'
DATA_QUALITY = '0'

class EnhancedStatsMonitor(TracabStatsMonitor):
    def __init__(self):
        super().__init__()  # Initialize the original StatsMonitor GUI
        self.add_new_button()
        self.run()

    def add_new_button(self):
        # print("Adding the new button...")
        self.new_button = tk.Button(self.center_frame, text="Check Gateway", command=self.new_button_action)
        self.new_button.grid(row=3, column=1, pady=4, sticky="nw")

    def new_button_action(self):
        game_id = self.get_game_id()
        vendor = self.get_vendor()
        # print(game_id, vendor)
        app = FeedStatusGUI(DATA_QUALITY, EXTR_VERS, game_id, vendor)

    def run(self):
        self.root.mainloop()  # Start the event loop here

if __name__ == "__main__":
    enhanced_monitor = EnhancedStatsMonitor()
