from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from ipregistry import IpregistryClient
from timezonefinder import TimezoneFinder
from tzlocal import get_localzone


# Define the function to get timezone from latitude and longitude
def get_timezone(lat: float, lon: float) -> str:
    """
    Returns the timezone of a location as a string

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        str: Timezone string
    """
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    if (
        timezone_str is None
    ):  # if the location is over the ocean or cannot be determined
        timezone_str = str(get_localzone())
    return timezone_str


def get_current_timezone() -> str:
    """
    Get the current timezone of the machine. If will try to get the timezone from the
    IP address, if it fails, it will use the local timezone of the machine.

    Returns:
        str: Timezone string
    """
    local_timezone = str(get_localzone())
    client = IpregistryClient("tryout")
    timezone = client.lookup()._json.get("time_zone", local_timezone)
    if isinstance(timezone, dict):  # if the timezone is a dict, get the value
        timezone = timezone.get("id", local_timezone)

    return timezone


def timestamp_with_timezone(
    lat: float,
    lon: float,
    timestamp: str,
    format: str = "%I:%M:%S %p",
    output_format: Optional[str] = None,
) -> str:
    """
    Returns a timestamp with the timezone of the location.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        timestamp (str): Timestamp to be converted.
        format (str, optional): Format of the timestamp. Defaults to "%I:%M:%S %p".
        output_format (str, optional): Output format the timestamp will be converted to.
            Defaults to None.

    Returns:
        str: Timestamp with the timezone of the location.
    """

    if output_format is None:
        output_format = format

    if not (lat and lon):
        date_obj = datetime.strptime(timestamp.strip(), format)
        date_str = date_obj.strftime(output_format) + " UTC"
        return date_str

    timezone = get_timezone(lat, lon)
    timezone_format = format + " %z"
    date_obj = datetime.strptime(timestamp.strip() + " +0000", timezone_format)
    date_obj = date_obj.astimezone(ZoneInfo(timezone))

    date_str = date_obj.strftime(timezone_format) + f" {timezone}"
    return date_str


def parse_date_str(date: str) -> datetime:
    """
    Parse a date string in the format YYYY-MM-DD or YYYY-MM-DD HH:MM to a datetime object

    Args:
        date (str): Date string in the format YYYY-MM-DD. If None, the current date is
            used + 1 minute

    Returns:
        datetime.datetime: Datetime object
    """
    if date is None:
        # cron str 1 minute after now
        date = datetime.now() + timedelta(minutes=1)
    else:
        # Parse the date to a datetime object even if hour is not provide
        has_hour = len(date.split(" ")) == 2
        if has_hour:
            date = datetime.strptime(date, "%Y-%m-%d %H:%M")
        else:
            date = datetime.strptime(date, "%Y-%m-%d")
            print("Hour not provided, setting it to 5 am")
            # add 5 hours to the date to make it 5 am
            date = date + timedelta(hours=5)

    return date
