import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from TracabModules.Internal.gateway import GatewayDownloader
from mplsoccer import Pitch

game_id = '2374222'
vendor_id = '5'
extr_vers = '4'
data_quality = '1'

downloader = GatewayDownloader(game_id, vendor_id, data_quality, extr_vers)
"""
Heatmap
"""

tf05_data, tf05_success = downloader.download_tf05_feed()
heatmap_string = tf05_data['HomeTeam']['Players'][3]['Heatmap']


# Parse heatmap string into numpy array
def parse_heatmap_string(heatmap_string, x_zones=20, y_zones=14):
    heatmap_data = np.array([int(char) for char in heatmap_string]).reshape((y_zones, x_zones))
    return heatmap_data


def draw_football_pitch(ax):
    """Draw a football pitch on the given axes."""
    # Pitch dimensions and colors
    pitch_length = 105  # in meters
    pitch_width = 68  # in meters
    line_width = 2
    line_color = 'white'
    pitch_color = 'green'

    # Plot the pitch
    ax.set_xlim(0, pitch_length)
    ax.set_ylim(0, pitch_width)
    ax.set_facecolor(pitch_color)

    # Halfway line and center circle
    ax.plot([pitch_length / 2, pitch_length / 2], [0, pitch_width], color=line_color, linewidth=line_width)
    center_circle = plt.Circle((pitch_length / 2, pitch_width / 2), 9.15, color=line_color, fill=False,
                               linewidth=line_width)
    ax.add_patch(center_circle)

    # Calculate dimensions relative to pitch size
    penalty_area_length = pitch_length * (16.5 / 105)  # 16.5 meters as a fraction of pitch_length
    penalty_area_width = pitch_width * (40.3 / 68)  # 40.3 meters as a fraction of pitch_width
    goal_area_length = pitch_length * (5.5 / 105)  # 5.5 meters as a fraction of pitch_length
    goal_area_width = pitch_width * (18.3 / 68)  # 18.3 meters as a fraction of pitch_width
    penalty_spot_size = pitch_width * (0.2 / 68)

    # Home penalty area
    ax.add_patch(plt.Rectangle((0, (pitch_width - penalty_area_width) / 2), penalty_area_length, penalty_area_width,
                               color=line_color, fill=False, linewidth=line_width))
    # Home goal area
    ax.add_patch(
        plt.Rectangle((0, (pitch_width - goal_area_width) / 2), goal_area_length, goal_area_width, color=line_color,
                      fill=False, linewidth=line_width))
    # Away penalty area
    ax.add_patch(
        plt.Rectangle((pitch_length - penalty_area_length, (pitch_width - penalty_area_width) / 2), penalty_area_length,
                      penalty_area_width, color=line_color, fill=False, linewidth=line_width))
    # Away goal area
    ax.add_patch(plt.Rectangle((pitch_length - goal_area_length, (pitch_width - goal_area_width) / 2), goal_area_length,
                               goal_area_width, color=line_color, fill=False, linewidth=line_width))

    # Penalty spots and center spot
    ax.add_patch(plt.Circle((11, pitch_width / 2), penalty_spot_size, color=line_color))
    ax.add_patch(plt.Circle((pitch_length - 11, pitch_width / 2), penalty_spot_size, color=line_color))
    ax.add_patch(plt.Circle((pitch_length / 2, pitch_width / 2), penalty_spot_size, color=line_color))

    # Axes labels and title
    ax.set_xlabel('Length (m)')
    ax.set_ylabel('Width (m)')
    ax.set_title('Football Pitch')

    # Add playing direction label
    ax.text(pitch_length / 2, -7, 'Left to Right', ha='center', color='black', fontsize=15, fontweight='bold')


def visualize_heatmap_on_pitch(heatmap_array, title="Heatmap on Football Pitch", save_path=None):
    """Visualize the heatmap on a football pitch."""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Draw football pitch
    draw_football_pitch(ax)

    # Overlay heatmap
    cmap = plt.get_cmap('magma')  # colormap
    im = ax.imshow(heatmap_array, cmap=cmap, alpha=0.7, extent=[0, 105, 0, 68], origin='lower')

    # Add colorbar
    cbar = fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.7)
    cbar.set_label('Intensity')

    # Set title
    ax.set_title(title)

    # Hide axis and ticks
    ax.axis('off')

    # Save or show plot
    if save_path:
        plt.savefig(save_path, dpi=300)
        plt.close(fig)
    else:
        plt.show()


# Parse heatmap string
heatmap_array = parse_heatmap_string(heatmap_string, x_zones=20, y_zones=14)

# Visualize heatmap on football pitch
visualize_heatmap_on_pitch(heatmap_array, title="Heatmap on Football Pitch",
                           save_path="player_heatmap.png")


"""
Pass Network
"""
tf09_data, tf09_success = downloader.download_tf09_feed()

successul_passes = [x['SuccessfulPasses'] for x in tf09_data['HomeTeam']['Players']]

passes = {
    obj['Jersey']: obj['SuccessfulPasses']
    for obj in tf09_data['HomeTeam']['Players']
}

passes_df = pd.DataFrame()
for player in passes:
    df = pd.DataFrame(passes[player])
    df['PasserNumber'] = player
    passes_df = pd.concat([passes_df, df])
