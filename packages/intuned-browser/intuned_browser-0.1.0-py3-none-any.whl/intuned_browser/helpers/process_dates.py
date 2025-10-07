from datetime import datetime

from dateutil import parser


def process_date(date_string: str) -> datetime | None:
    try:
        # Handle the case where there's a hyphen used as separator
        date_string = date_string.replace(" - ", " ")

        # Parse the date string with dayfirst=False to handle MM/DD/YYYY format
        parsed_date = parser.parse(date_string, dayfirst=False)
        return parsed_date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    except (ValueError, TypeError):
        return None
