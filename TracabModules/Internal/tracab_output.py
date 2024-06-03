import pandas as pd
from xml.dom.minidom import parse
from pathlib import Path

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
    def extract_stats(team_tag):
        team_element = xml_doc_stats.getElementsByTagName(team_tag)[0]
        total_distance = float(team_element.attributes['TotalDistance'].childNodes[0].data.split(' ')[0])
        total_sprints = int(team_element.attributes['TotalSprints'].childNodes[0].data)
        total_speedruns = int(team_element.attributes['TotalSpeedRuns'].childNodes[0].data)
        return {'TotalDistance': total_distance, 'Num. Sprints': total_sprints, 'Num. SpeedRuns': total_speedruns}

    # Extract stats for home and away teams
    home_stats = pd.DataFrame([extract_stats('HomeTeam')])
    away_stats = pd.DataFrame([extract_stats('AwayTeam')])

    return home_stats, away_stats