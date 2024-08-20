"""
One script to get all tables that are needed for the weekly stats reports
"""
from pathlib import Path
import sqlite3 as sql
import numpy as np
import pandas as pd
import re
from TracabModules.Internal.tools import (get_dfl_player_mapping, get_mls_player_mapping, get_opta_player_mapping,
                                          get_ekstra_player_mapping)
from matplotlib import pyplot as plt
from plottable import ColumnDefinition, Table
from plottable.plots import image
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import PyPDF2
from datetime import datetime

from Database.Tracab_Stats.automatic_updater import setup_logging
import logging

LEAGUE_ID_MAPPING = {'mls': 1,
                     'bl1': 51,
                     'bl2': 52,
                     'eredivisie': 9,
                     'ekstraklasa': 55}

LEAGUE_MAPPING = {
    'mls': 'Major League Soccer',
    'bl1': '1. Bundesliga',
    'bl2': '2. Bundesliga',
    'eredivisie': 'Eredivisie',
    'ekstraklasa': 'Ekstraklasa'
}


def shorten_name(name):
    if pd.isna(name):
        return name  # Handle NaN values if they exist

    # Remove '(M)' suffix
    name = re.sub(r'\s*\(M\)$', '', name)

    # Split the name into parts
    parts = name.split()
    # Split the name into parts
    parts = name.split()

    # Check if the name has more than 2 parts
    if len(parts) > 2:
        # Take the first initial
        first_initial = parts[0]

        # Shorten middle names to initials
        middle_initials = ' '.join([part[0] + '.' for part in parts[1:-1]])

        # Keep the last name as is
        last_name = parts[-1]

        # Combine the parts
        return f'{first_initial} {middle_initials} {last_name}'
    else:
        # Return the name as is if it doesn't have more than 2 parts
        return name


# logger = logging.getLogger("reports_logger")
# setup_logging(Path(r"\\10.49.0.250\tracab_neu\07_QC\Scripts\Database\logging_configs\stats_reports.json"))


# Create player tables
def create_table(df: pd.DataFrame, kpi: str, filename: str) -> None:
    # Define table characteristics
    bg_color = "#212121"
    text_color = "#7ed957"
    plt.rcParams["text.color"] = text_color
    plt.rcParams["font.family"] = "monospace"

    col_defs = [
        ColumnDefinition(name="Rank", textprops={"ha": "center"}, width=0.01),
        ColumnDefinition(name="Name", textprops={"ha": "center"}, width=0.02),
        ColumnDefinition(name=kpi, textprops={"ha": "center", "weight": "bold"}, width=0.01)
    ]

    # fig, ax = plt.subplots(figsize=(15, 22))
    fig, ax = plt.subplots(figsize=(7.9, 8))
    fig.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Create the table
    table = Table(
        df,
        column_definitions=col_defs,
        index_col="Rank",
        row_dividers=True,
        row_divider_kw={"linewidth": 0.5, "linestyle": (0, (1, 5))},
        footer_divider=True,
        textprops={"fontsize": 14},
        col_label_divider_kw={"linewidth": 0.5, "linestyle": "-"},
        column_border_kw={"linewidth": .5, "linestyle": "-"},
        ax=ax,
    )

    # Adjust layout to fit the table tightly
    plt.tight_layout(pad=0.1)

    # Save the figure
    fig.savefig(
        filename,
        facecolor=ax.get_facecolor(),
        dpi=500,
        bbox_inches="tight",
        pad_inches=0.1,  # Adjust padding as needed

    )

    plt.close(fig)


# Create player tables
def create_team_table(df: pd.DataFrame, kpi: str, filename: str, logo_path) -> None:
    # Add paths to team logos
    df['Logo'] = df['TeamName'].apply(lambda x: Path(logo_path) / f'{x}.png')
    df_sorted = df[['Rank', 'Logo', 'TeamName', kpi]]

    # Define table characteristics
    bg_color = "#212121"  # White background color
    text_color = "#7ed957"  # Black text color
    plt.rcParams["text.color"] = text_color
    plt.rcParams["font.family"] = "monospace"

    col_defs = [
        ColumnDefinition(name="Rank", textprops={"ha": "center"}, width=0.01),
        ColumnDefinition(name="Logo", textprops={"ha": "center", "va": "center", 'color': bg_color}, width=0.01,
                         plot_fn=image),
        ColumnDefinition(name="TeamName", textprops={"ha": "left"}, width=0.04),
        ColumnDefinition(name=kpi, textprops={"ha": "center", "weight": "bold"}, width=0.01)
    ]

    fig, ax = plt.subplots(figsize=(15, 22))
    fig.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)

    # Create the table
    table = Table(
        df_sorted,
        column_definitions=col_defs,
        index_col="Rank",
        row_dividers=True,
        row_divider_kw={"linewidth": 0.5, "linestyle": (0, (1, 5))},
        footer_divider=True,
        textprops={"fontsize": 14},
        col_label_divider_kw={"linewidth": 0.5, "linestyle": "-"},
        column_border_kw={"linewidth": .5, "linestyle": "-"},
        ax=ax,
    )

    # Adjust layout to fit the table tightly
    # plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

    # Save the figure
    output_path = Path(
        filename)

    fig.savefig(
        output_path,
        facecolor=ax.get_facecolor(),
        dpi=500,
        bbox_inches="tight",
        pad_inches=0.1,  # Adjust padding as needed

    )

    plt.close(fig)


# Club Stats to Google ---------------------------------------------------------------------------------------
def club_stats_to_table(league: str, season: int, kpi: str) -> None:
    db_path = Path(fr'\\10.49.0.250/tracab_neu/07_QC/Alex/Databases/{league}_stats.db')

    with sql.connect(db_path) as conn:
        query = f"SELECT * FROM 'league_overview_{season}'"
        team_stats = pd.read_sql_query(query, conn)

    # Adjust 'Total Distance' to kilometers and round to two decimal places
    if kpi == 'Total Distance':
        team_stats[kpi] = np.round(team_stats[kpi] / 1000, 2)

    # Select relevant columns and sort by the specified KPI in descending order
    df_sorted = team_stats[['TeamName', kpi]].sort_values(by=kpi, ascending=False)
    df_sorted['Rank'] = df_sorted[kpi].rank(method='min', ascending=False)
    df_sorted['Rank'] = df_sorted['Rank'].apply(lambda x: int(x) if not pd.isna(x) else x)
    df_sorted = df_sorted[['Rank', 'TeamName', kpi]]
    filename = fr'\\10.49.0.250/tracab_neu/07_QC/Alex/StatsReports/{league.upper()}/{league}_{kpi}_{season}.png'
    logo_path = fr'\\10.49.0.250\tracab_neu\07_QC\Alex\TeamLogos\{league.upper()}_Logos\{season}'
    create_team_table(df_sorted, kpi, filename, logo_path)



# Top 10 Players to Google --------------------------------------------------------------------------------------------
def top_ten_players_to_table(league: str, season: int, kpi: str) -> None:
    db_path = Path(fr'\\10.49.0.250/tracab_neu/07_QC/Alex/Databases/{league}_stats.db')
    with sql.connect(db_path) as conn:
        player_query = f"SELECT * FROM 'player_stats' WHERE Season = {season}"
        players = pd.read_sql_query(player_query, conn)

    # Sort DataFrame by selected kpi in descending order
    df_sorted = players.sort_values(by=kpi, ascending=False)

    if kpi == 'HighSpeed':
        # Drop duplicates, keeping the first occurrence (which is the highest 'HighSpeed' due to sorting)
        df_top_players = df_sorted.drop_duplicates(subset='DlProviderID', keep='first')

    if kpi == 'Total Distance':
        # df_sorted['Total Distance'] = np.round(players[kpi] / 1000, 2)
        avg_distance = players.groupby('DlProviderID')[kpi].mean().round(2).reset_index()
        avg_distance['Total Distance'] = np.round(avg_distance[kpi] / 1000, 2)
        avg_distance.columns = ['DlProviderID', 'Avg Distance']

        # 2. Merge the average distance back into the original DataFrame
        players = players.merge(avg_distance, on='DlProviderID')

        # 3. Sort the DataFrame based on 'Total Distance' (or any other criteria)
        df_sorted = players.sort_values(by='Avg Distance', ascending=False)

        # Drop duplicates, keeping the first occurrence (which is the highest kpi score due to sorting)
        df_top_players = df_sorted.drop_duplicates(subset='DlProviderID', keep='first')

    if kpi == 'Num. Sprints':
        avg_sprints = players.groupby('DlProviderID')[kpi].mean().round(2).reset_index()
        avg_sprints.columns = ['DlProviderID', 'Avg Sprints']

        # 2. Merge the average distance back into the original DataFrame
        players = players.merge(avg_sprints, on='DlProviderID')

        # 3. Sort the DataFrame based on 'Total Distance' (or any other criteria)
        df_sorted = players.sort_values(by='Avg Sprints', ascending=False)

        # Drop duplicates, keeping the first occurrence (which is the highest kpi score due to sorting)
        df_top_players = df_sorted.drop_duplicates(subset='DlProviderID', keep='first')

    # Select the top 10 rows
    top_10 = df_top_players.head(10)

    if league == 'bl1' or league == 'bl2':
        # Get player mapping
        player_mapping = get_dfl_player_mapping(league_id=LEAGUE_ID_MAPPING[league], season=season)
    elif league == 'mls':
        player_mapping = get_mls_player_mapping(season_id=season - 2016, return_type='player_ids')
    elif league == 'eredivisie':
        player_mapping = get_opta_player_mapping(season_id=season, league_id=LEAGUE_ID_MAPPING[league])
    elif league == 'ekstraklasa':
        player_mapping = get_ekstra_player_mapping()

    # Add names to top_10
    top_10_with_names = pd.merge(top_10, player_mapping, left_on='DlProviderID', right_on='DlProviderID', how='left')

    filename = fr'\\10.49.0.250/tracab_neu/07_QC/Alex/StatsReports/{league.upper()}/{league}_{kpi}_{season}_players.png'

    # Add a 'Rank' column based on KPI ranking and drop remaining columns
    if kpi == 'Total Distance':
        top_10_with_names = top_10_with_names[['Name', 'Avg Distance']]
        top_10_with_names['Rank'] = top_10_with_names['Avg Distance'].rank(method='min', ascending=False).astype(int)
        top_10_with_names = top_10_with_names[['Rank', 'Name', 'Avg Distance']]
        top_10_with_names = top_10_with_names.rename(columns={'Avg Distance': 'Distance'})
        top_10_with_names['Name'] = top_10_with_names['Name'].apply(shorten_name)  # shorten names
        create_table(top_10_with_names, 'Distance', filename)
    elif kpi == 'Num. Sprints':
        top_10_with_names = top_10_with_names[['Name', 'Avg Sprints']]
        top_10_with_names['Rank'] = top_10_with_names['Avg Sprints'].rank(method='min', ascending=False).astype(int)
        top_10_with_names = top_10_with_names[['Rank', 'Name', 'Avg Sprints']]
        top_10_with_names = top_10_with_names.rename(columns={'Avg Sprints': 'Sprints'})
        top_10_with_names['Name'] = top_10_with_names['Name'].apply(shorten_name)  # shorten names
        create_table(top_10_with_names, 'Sprints', filename)
    else:
        top_10_with_names = top_10_with_names[['Name', kpi]]
        top_10_with_names['Rank'] = top_10_with_names[kpi].rank(method='min', ascending=False).astype(int)
        top_10_with_names = top_10_with_names[['Rank', 'Name', 'HighSpeed']].rename(columns={'HighSpeed': 'Speed'})
        top_10_with_names['Name'] = top_10_with_names['Name'].apply(shorten_name)  # shorten names
        create_table(top_10_with_names, 'Speed', filename)


def tables_to_pdf(image_paths: list[str], output_filename: str, top_heading: str,
                  image_headings: list[str], template_path: str, spacing=20, lower_amount_cm=1.5):
    if len(image_paths) != 5:
        raise ValueError("Exactly 5 image paths are required for this layout.")

    # Convert cm to points
    cm_to_points = 28.35
    lower_amount_points = lower_amount_cm * cm_to_points
    heading_spacing_points = 5  # Spacing between heading and image
    shift_down = 4 * cm  # Shift everything 3 cm lower

    # Read the template PDF
    template_pdf = PyPDF2.PdfReader(template_path)
    output_pdf = PyPDF2.PdfWriter()

    # Get the dimensions of the first page of the template
    template_page = template_pdf.pages[0]
    page_width = float(template_page.mediabox.width)
    page_height = float(template_page.mediabox.height)

    # Create a PDF canvas with A4 page size on an in-memory buffer
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))

    # Set up fonts for headings
    heading_font = 'Helvetica-Bold'
    heading_size = 20  # Font size in points
    c.setFont(heading_font, heading_size)

    # Set the color for headings
    heading_fill_color = HexColor('#7ed957')
    c.setFillColor(heading_fill_color)

    # Set up fonts for subheadings
    sub_heading_font = 'Helvetica-Bold'
    sub_heading_size = 16  # Font size in points
    c.setFont(sub_heading_font, sub_heading_size)

    # Calculate top heading position
    top_heading_width = c.stringWidth(top_heading, heading_font, heading_size)
    top_heading_x = (page_width - top_heading_width) / 2
    top_heading_y = page_height - heading_size - 0.5 * inch - shift_down  # Adjust position from the top

    # Draw top heading
    c.drawString(top_heading_x, top_heading_y, top_heading)

    # Calculate image sizes
    large_image_width = page_width / 1.9
    large_image_height = (page_height - spacing) / 1.9
    small_image_width = page_width / 2.9
    small_image_height = (page_height - spacing) / 3.9

    # Position for headings and images
    y_positions_large_images = [
        page_height - large_image_height - lower_amount_points - heading_size - heading_spacing_points - 0.5 * inch - shift_down,
        page_height - large_image_height - lower_amount_points - heading_size - heading_spacing_points - 0.5 * inch - shift_down
    ]
    y_positions_small_images = [
        page_height - large_image_height - 40 - small_image_height - lower_amount_points - heading_size - heading_spacing_points - 0.5 * inch - shift_down,
        page_height - large_image_height - 40 - small_image_height - lower_amount_points - heading_size - heading_spacing_points - 0.5 * inch - shift_down,
        page_height - large_image_height - 40 - small_image_height - lower_amount_points - heading_size - heading_spacing_points - 0.5 * inch - shift_down
    ]

    # Draw headings and images
    for i in range(2):
        heading = image_headings[i]
        image_x = i * large_image_width
        image_y = y_positions_large_images[i]
        heading_width = c.stringWidth(heading, heading_font, heading_size)
        heading_x = image_x + (large_image_width - heading_width) / 2
        c.drawString(heading_x, image_y + large_image_height + heading_spacing_points, heading)
        c.drawImage(image_paths[i], image_x, image_y, width=large_image_width, height=large_image_height)

    for i in range(0, 3):
        heading = image_headings[i + 2]
        image_x = i * small_image_width
        image_y = y_positions_small_images[i]
        sub_heading_width = c.stringWidth(heading, sub_heading_font, sub_heading_size)
        sub_heading_x = image_x + (small_image_width - sub_heading_width) / 2
        c.drawString(sub_heading_x, image_y + small_image_height + heading_spacing_points, heading)
        c.drawImage(image_paths[i + 2], image_x, image_y, width=small_image_width, height=small_image_height)

    # Finish the canvas drawing
    c.save()

    # Move the buffer to the beginning
    buffer.seek(0)

    # Merge the drawn canvas with the template
    template_page = template_pdf.pages[0]
    new_pdf = PyPDF2.PdfReader(buffer)
    overlay_page = new_pdf.pages[0]

    # Merge the overlay with the template page
    template_page.merge_page(overlay_page)

    # Add the merged page to the output
    output_pdf.add_page(template_page)

    # Write the output PDF to a file
    with open(output_filename, "wb") as output_file:
        output_pdf.write(output_file)


def merge_pdfs(pdf_list, output_filename):
    # Create a PDF writer object
    pdf_writer = PyPDF2.PdfWriter()

    # Loop through all the PDF files
    for pdf in pdf_list:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf)

        # Add all pages of the current PDF to the writer object
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

    # Get the current date
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Combine the base filename with the current date
    output_filename = f'{output_filename}_{current_date}.pdf'

    # Write the merged PDF to a file
    with open(output_filename, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)


leagues = ['mls', 'bl1', 'bl2', 'eredivisie', 'ekstraklasa']
kpis = ['Total Distance', 'Num. Sprints', 'HighSpeed']

pdf_files = [r'\\10.49.0.250\tracab_neu\07_QC\Alex\PDF_templates\deckblatt.pdf']


def main() -> None:
    for league in leagues:
        season = 2023 if league == 'bl1' else 2024
        for kpi in kpis:
            if kpi != 'HighSpeed':
                club_stats_to_table(league=league, season=season, kpi=kpi)
            top_ten_players_to_table(league=league, season=season, kpi=kpi)

        # Report creation
        image_paths = [
            fr"\\10.49.0.250\tracab_neu\07_QC\Alex\StatsReports\{league.upper()}\{league}_Num. Sprints_{season}.png",
            fr"\\10.49.0.250\tracab_neu\07_QC\Alex\StatsReports\{league.upper()}\{league}_Total Distance_{season}.png",
            fr"\\10.49.0.250\tracab_neu\07_QC\Alex\StatsReports\{league.upper()}\{league}_Total Distance_{season}_players.png",
            fr"\\10.49.0.250\tracab_neu\07_QC\Alex\StatsReports\{league.upper()}\{league}_HighSpeed_{season}_players.png",
            fr"\\10.49.0.250\tracab_neu\07_QC\Alex\StatsReports\{league.upper()}\{league}_Num. Sprints_{season}_players.png"]

        output_filename = fr'\\10.49.0.250\tracab_neu\07_QC\Alex\StatsReports\{league}_report'
        pdf_files.append(output_filename)

        image_headings = [
            "Number of Sprints",
            "Total Distance [km]",
            "Total Distance - Players [km]",
            "Top 10 Highspeeds [km/h]",
            "Number of Sprints - Players"
        ]

        top_heading = f'{LEAGUE_MAPPING[league]} Season {season}'
        template_path = fr'\\10.49.0.250\tracab_neu\07_QC\Alex\PDF_templates\{league}_template.pdf'
        tables_to_pdf(image_paths, output_filename, top_heading, image_headings, template_path)
        print(f'\n {league}: DONE')

    merge_pdfs(pdf_files, r'\\10.49.0.250\tracab_neu\07_QC\Alex\StatsReports\tracab_report')
    print(f'\n Final Report: DONE')


if __name__ == '__main__':
    main()

