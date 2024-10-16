import pandas as pd
from xml.dom.minidom import parse
from lxml import etree
import logging
import numpy as np

bvb_validation_kpis = ["TeamID", "PlayerID", "PlayerNumber", "PlayerName",
                       "PlayTime (min)", "Distance (m)", "Distance/min",
                       "TopSpeed (km/h)", "AvgSpeed (km/h)", "Sprints > 25,2km/h",
                       "Distance Sprints (m)", "Distance/min Sprints",
                       "HighSpeedRuns 19,8-25,2km/h", "Distance HSR (m)",
                       "Distance/min HSR", "Runnings 14,4-19,8kmh/",
                       "Running Distance (m)", "Running Distance/min",
                       "HighIntensityRuns > 14,4km/h", "Distance HIR (m)",
                       "Distance/min HIR", "VeryHighIntensityRuns",
                       "Distance VHIR (m)", "Distance/min VHIR",
                       "Distance IBC", "Sprints IBC", "SpeedRuns IBC",
                       "AvgTime IBC"]

stats_report_kpis = ['Distance', 'TopSpeed', 'Sprints', 'SpeedRuns']


def write_excel(dfl_df, epl_df, match_info, obs):
    """


    :param obs:
    :param epl_df: list of pd.DataFrame
    :param dfl_df: list of pd.DataFrame
    :param match_info: Dict
    """

    if obs is False:
        sheets = ['BVB_Live_EPL', 'Opp_Live_EPL', 'BVB_Live_DFL', 'Opp_Live_DFL']
        excel_name = "Live_Game_" + match_info['match_id'] + "_2.xlsx"
    elif obs is True:
        sheets = ['BVB_Observed_EPL', 'Opp_Observed_EPL', 'BVB_Observed_DFL', 'Opp_Observed_DFL']
        excel_name = "Observed_Game_" + match_info['match_id'] + "_2.xlsx"

    # Write Excel-File. Would need some formatting and additional information to match Falk's application 100%
    writer = pd.ExcelWriter(excel_name, engine="xlsxwriter")

    # Write each dataframe to a different worksheet.
    epl_df[0].to_excel(writer, sheet_name=sheets[0], index=False, startrow=8, header=False)
    epl_df[1].to_excel(writer, sheet_name=sheets[1], index=False, startrow=8, header=False)
    dfl_df[0].to_excel(writer, sheet_name=sheets[2], index=False, startrow=8, header=False)
    dfl_df[1].to_excel(writer, sheet_name=sheets[3], index=False, startrow=8, header=False)

    for sheet in sheets:
        # Get the xlsxwriter workbook and worksheet objects.
        if 'BVB' in sheet:
            teamID_x = match_info['bvb_id']
            teamName = match_info['bvb_name']
        if 'Opp' in sheet:
            teamID_x = match_info['oppo_id']
            teamName = match_info['oppo_name']
        workbook = writer.book
        worksheet = writer.sheets[sheet]
        worksheet.write(0, 0, 'ChyronHego - Tracab Physical Summary')
        worksheet.write(1, 0, 'LeagueID:')
        worksheet.write(1, 1, match_info['comp_id'])
        worksheet.write(2, 0, 'RoundID:')
        worksheet.write(2, 1, match_info['md'])
        worksheet.write(3, 0, 'Game ID:')
        worksheet.write(3, 1, match_info['match_id'])
        worksheet.write(5, 0, 'TeamID:')
        worksheet.write(5, 1, teamID_x)
        worksheet.write(6, 0, 'TeamName')
        worksheet.write(6, 1, teamName)
        # Add a header format.
        header_format = workbook.add_format({
            'bold': False,
            'text_wrap': False,
            'border': 0})

        # Write the column headers with the defined format.
        for col_num, value in enumerate(epl_df[0].columns.values):
            worksheet.write(7, col_num, value, header_format)

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()


def get_observed_stats(report):
    """

    :param report:
    :return:

    """
    try:
        # Parse the XML document
        xml_doc_stats = parse(str(report))
    except FileNotFoundError:
        print(f'The folder {report} does not contain the necessary stats!')
        return

    # Helper function to extract statistics
    def extract_team_stats(team_tag):
        team_element = xml_doc_stats.getElementsByTagName(team_tag)[0]
        total_distance = float(team_element.attributes['TotalDistance'].childNodes[0].data.split(' ')[0])
        total_sprints = int(team_element.attributes['TotalSprints'].childNodes[0].data)
        total_speedruns = int(team_element.attributes['TotalSpeedRuns'].childNodes[0].data)
        return {'Total Distance': total_distance, 'Num. Sprints': total_sprints, 'Num. SpeedRuns': total_speedruns}

    def extract_player_stats(team_tag):
        team_element = xml_doc_stats.getElementsByTagName(team_tag)[0]
        player_elements = [x for x in team_element.childNodes]
        shirt_numbers = [x.getAttribute('No') for x in player_elements if float(x.getAttribute('Distance')) != 0.00]
        total_distances = [float(x.getAttribute('Distance')) for x in player_elements if
                           float(x.getAttribute('Distance')) != 0.00]
        high_speeds = [float(x.getAttribute('MaxSpeed')) for x in player_elements if
                       float(x.getAttribute('MaxSpeed')) != 0.00]
        num_sprints = [float(x.getAttribute('Sprints')) for x in player_elements if
                       float(x.getAttribute('Distance')) != 0.00]
        num_speed_runs = [float(x.getAttribute('SpeedRuns')) for x in player_elements if
                          float(x.getAttribute('Distance')) != 0.00]

        # Create DataFrame using extracted data
        player_data = {
            'ShirtNumber': shirt_numbers,
            'Total Distance': total_distances,
            'HighSpeed': high_speeds,
            'Num. Sprints': num_sprints,
            'Num. SpeedRuns': num_speed_runs
        }

        player_df = pd.DataFrame(player_data)

        return player_df

    # Extract stats for home and away teams
    home_stats = pd.DataFrame([extract_team_stats('HomeTeam')])
    away_stats = pd.DataFrame([extract_team_stats('AwayTeam')])

    # Extract stats for home and away players
    home_player_stats = extract_player_stats('HomeTeam')
    away_player_stats = extract_player_stats('AwayTeam')

    return ({'HomeStats': home_stats, 'AwayStats': away_stats},
            {'HomePlayerStats': home_player_stats, 'AwayPlayerStats': away_player_stats})


def get_validated_stats(filepath, gamelog_info):
    logging.basicConfig(filename='stats_log.log', level=logging.INFO, format='%(asctime)s - %(message)s')

    files = [p for p in filepath.iterdir() if p.is_file() and 'Resolution.xml' in p.name]

    home_stats = pd.DataFrame()
    home_player_stats = pd.DataFrame()
    away_stats = pd.DataFrame()
    away_player_stats = pd.DataFrame()

    # Loop through all PlayerID_Resolution.xml files to fetch KPI-scores for each player
    for file in files:
        #try:
            # Parse the XML file
            tree = etree.parse(str(file))
            root = tree.getroot()

            team_id = root.get('TeamID')
            player_id = root.get('PlayerID')
            shirt_num = root.get('PlayerNumber')

            # Get Stats element
            stats_elements = root.findall(".//Stats")
            if not stats_elements:
                logging.error(f'Stats not found in {file}')
                continue
                # return None

            stats_data = {}
            for stat_elem in stats_elements:
                for kpi in stats_report_kpis:
                    kpi_value = float(stat_elem.findtext(f".//{kpi}", np.nan))
                    stats_data.setdefault(kpi, []).append(kpi_value)

            # Check if any key performance indicator is missing
            if stats_data['Distance'][-1] == 0.0:
                continue

            top_speed = max(stats_data.get('TopSpeed', [np.nan]))

            player = {
                "PlayerID": player_id,
                "ShirtNumber": shirt_num,
                "Total Distance": stats_data['Distance'][-1],
                "HighSpeed": top_speed,
                "Num. Sprints": stats_data['Sprints'][-1],
                "Num. SpeedRuns": stats_data['SpeedRuns'][-1]
            }

        # except etree.XMLSyntaxError as e:
        #     logging.error(f'XML syntax error in {file}: {e}')
        #     # return None
        # except Exception as e:
        #     logging.error(f'Unexpected error in {file}: {e}')
        #   # return None

            if team_id == gamelog_info['HomeId']:
                home_player_stats = pd.concat([home_player_stats, pd.DataFrame([player])])
            else:
                away_player_stats = pd.concat([away_player_stats, pd.DataFrame([player])])

    def aggregate_stats(players_data):
        if players_data.empty:
            return pd.DataFrame()
        totals = players_data[['Total Distance', 'Num. Sprints', 'Num. SpeedRuns']].sum().round(2)
        return pd.DataFrame([totals])

    home_stats = aggregate_stats(home_player_stats)
    away_stats = aggregate_stats(away_player_stats)

    return home_stats, away_stats, home_player_stats, away_player_stats


def get_ekstraklasa_stats(filepath):
    xml_doc = etree.parse(filepath)
