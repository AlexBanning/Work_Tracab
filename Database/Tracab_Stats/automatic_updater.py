from TracabModules.Internal.database import create_team_stats_table, create_avg_stats_table
from TracabModules.Internal.tools import get_club_id_mapping
import time
import logging
import atexit
import json
import logging.config
import logging.handlers
from pathlib import Path

LEAGUE_MAPPING = {
    'mls': r'\\10.49.0.250\tracab_neu\01_Tracking-Data\Season_23-24\1 - MLS',
    'bl1': r'\\10.49.0.250\tracab_neu\01_Tracking-Data\Season_24-25\51 - Bundesliga 1_BL',
    'bl2': r'\\10.49.0.250\tracab_neu\01_Tracking-Data\Season_24-25\52 - 2.Bundesliga 2_BL',
    'eredivisie': r'\\10.49.0.250\tracab_neu\01_Tracking-Data\Season_24-25\9 - Eredivisie',
    'ekstraklasa': r'\\10.49.0.250\tracab_neu\01_Tracking-Data\Season_24-25\55 - Ekstraklasa'
}

logger = logging.getLogger("update_logger")  # __name__ is a common choice


def setup_logging(config_file: Path):
    with open(config_file) as f_in:
        config = json.load(f_in)

    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


def update_team_stats_table(data_path: Path, league: str):
    setup_logging(Path(r'\\10.49.0.250\tracab_neu/07_QC/Scripts/logging_configs/automatic_updater.json'))
    logging.basicConfig(level="ERROR")

    start_time = time.time()
    for md in data_path.glob('MD*'):
        if md.is_dir():
            for match in md.iterdir():
                if match.is_dir():
                    start_time_match = time.time()
                    create_team_stats_table(league, match)
                    elapsed_time = time.time() - start_time_match
                    message = f"Processed {match} in {elapsed_time:.2f} seconds"
                    # print(f'Processed {match} in {elapsed_time:.2f} seconds')
                    logger.info(message)

    total_elapsed_time = time.time() - start_time
    final_message = f"DB of {league} has been updated in {total_elapsed_time:.2f} seconds"
    logger.critical(final_message)


def create_avg_stats(league: str, season: int) -> None:
    club_mapping = get_club_id_mapping(league=league, season=season)
    create_avg_stats_table(club_mapping, league=league, season=season, db_update=True, data=True)
    logger.critical(f"Average stats table created for {league.upper()}, season {season}")


def main() -> None:
    for league in LEAGUE_MAPPING:
        message = f"STARTING TO UPDATE {league}"
        logger.critical(message)
        update_team_stats_table(data_path=Path(LEAGUE_MAPPING[league]), league=league)
        create_avg_stats(league, season=2024)

    message = f"All databases have been updated."
    logger.critical(message)


if __name__ == '__main__':
    main()
