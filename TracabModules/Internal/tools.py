from datetime import datetime, timedelta


def is_date_in_current_week(date_str):
    # Convert the date string to a datetime object
    date_to_check = datetime.strptime(date_str, '%Y-%m-%d')

    # Get today's date
    today = datetime.today()

    # Calculate the start date of the current week (assuming Monday is the start of the week)
    start_of_week = today - timedelta(days=today.weekday())

    # Calculate the end date of the current week
    end_of_week = start_of_week + timedelta(days=6)

    # Check if the given date falls within the current week
    return start_of_week <= date_to_check <= end_of_week