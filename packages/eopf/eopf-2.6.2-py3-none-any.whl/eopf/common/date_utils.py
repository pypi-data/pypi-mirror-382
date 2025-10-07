# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""

date_utils.py

utilities to handle date format and conversion

"""

import datetime
import math
from typing import Union

import pandas as pd
import pytz


def get_datetime_from_utc(utcstr: str) -> datetime.datetime:
    """
    Extracr a datetime.datetime from an UTC formatted string
    Parameters
    ----------
    utcstr

    Returns
    -------
    datetime.datetime
    """
    if utcstr.startswith("UTC"):
        if "Z" in utcstr:
            return datetime.datetime.strptime(utcstr, "UTC=%Y-%m-%dT%H:%M:%S.%fZ")
        if "." in utcstr:
            return datetime.datetime.strptime(utcstr, "UTC=%Y-%m-%dT%H:%M:%S.%f")
        return datetime.datetime.strptime(utcstr, "UTC=%Y-%m-%dT%H:%M:%S")
    if "Z" in utcstr:
        return datetime.datetime.strptime(utcstr, "%Y-%m-%dT%H:%M:%S.%fZ")
    if "+" in utcstr:
        # support old EOPF products
        if "." in utcstr:
            # found on S02MSIL1C/L2A
            return datetime.datetime.strptime(utcstr, "%Y-%m-%dT%H:%M:%S.%f%z")
        # found on S03SYNAOD
        return datetime.datetime.strptime(utcstr, "%Y-%m-%dT%H:%M:%S%z")
    if "." in utcstr:
        return datetime.datetime.strptime(utcstr, "%Y-%m-%dT%H:%M:%S.%f")
    return datetime.datetime.strptime(utcstr, "%Y-%m-%dT%H:%M:%S")


def get_datetime_from_yyyymmddthhmmss(datestr: str) -> datetime.datetime:
    """
    Get a datetime.datetime from a yyyymmddthhmmss string
    Parameters
    ----------
    datestr

    Returns
    -------
    datetime.datetime
    """
    return datetime.datetime.strptime(datestr, "%Y%m%dT%H%M%S")


def get_datetime_from_yyyymmdd(datestr: str) -> datetime.datetime:
    """
    Get a datetime.datetime from a yyyymmdd string
    Parameters
    ----------
    datestr

    Returns
    -------
    datetime.datetime
    """
    return datetime.datetime.strptime(datestr, "%Y%m%d")


def get_utc_from_datetime(datet: datetime.datetime) -> str:
    """
    Get an UTC formatted string from a datetime.datetime
    Parameters
    ----------
    datet : a datetime

    Returns
    -------
    string UTC formatted
    """
    return datetime.datetime.strftime(datet, "%Y-%m-%dT%H:%M:%SZ")


def get_utc_str_now() -> str:
    """
    Get UTC str from now()
    Returns
    -------
    UTC formatted string of now()
    """

    return datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%SZ")


def get_julianday_as_double(datet: datetime.datetime) -> float:
    """
    Compute the julian day of a datetime
    Parameters
    ----------
    datet : a datetime

    Returns
    -------
    julien day in float
    """
    year = datet.year
    month = datet.month
    day = datet.day
    hour = datet.hour
    minu = datet.minute
    sec = datet.second
    millisec = datet.microsecond // 1000
    # Conversion to julian day according to
    # http: // en.wikipedia.org / wiki / Julian_day
    # division are integer divisions:
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    julianday: float = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    # now, the division are NOT integer
    julianday += (hour - 12) / 24.0 + minu / 1440.0 + sec / 86400.0
    # now, the millisecond
    julianday += millisec / 86.4e6
    return julianday


def get_julianday_as_int(datet: datetime.datetime) -> int:
    """
    Compute the julian day of a datetime
    Parameters
    ----------
    datet : a datetime

    Returns
    -------
    julien day in int floored
    """

    return math.floor(get_julianday_as_double(datet))


def get_average_julian_day(ptimestartutc: str, ptimestoputc: str) -> float:
    """
    Compute the average julian day between two date
    Parameters
    ----------
    datet : a datetime

    Returns
    -------
    julien day in float
    """

    # Get the validity start date in julian day
    l_timestart_jd = get_julianday_as_double(get_datetime_from_utc(ptimestartutc))
    # Get the validity stop date in julian day
    l_timestop_jd = get_julianday_as_double(get_datetime_from_utc(ptimestoputc))
    # Compute the average date
    return (l_timestart_jd + l_timestop_jd) / 2.0


def get_date_yyyymmdd_from_tm(datet: datetime.datetime) -> str:
    """
    get yyyymmdd formatted str from a datettime
    Parameters
    ----------
    datet

    Returns
    -------
    str formatted yyymmdd
    """
    # Write the date in the formated "UTC=%04d-%02d-%02dT%02d:%02d:%02d"
    return "{:04d}{:02d}{:02d}".format(datet.year, datet.month, datet.day)


def get_date_yyyymmddthhmmss_from_tm(datet: datetime.datetime) -> str:
    """
    get yyyymmddthhmmss formatted str from a datettime
    Parameters
    ----------
    datet

    Returns
    -------
    str formatted yyyymmddthhmmss
    """
    # Write the date in the formated "UTC=%04d-%02d-%02dT%02d:%02d:%02d"
    return str("{:04d}{:02d}{:02d}T{:02d}{:02d}{:02d}").format(
        datet.year,
        datet.month,
        datet.day,
        datet.hour,
        datet.minute,
        datet.second,
    )


def get_date_hhmmss_from_tm(datet: datetime.datetime) -> str:
    """
    get hhmmss formatted str from a datettime
    Parameters
    ----------
    datet

    Returns
    -------
    str formatted hhmmss
    """
    # Write the date in the formated "UTC=%04d-%02d-%02dT%02d:%02d:%02d"
    return str("{:02d}{:02d}{:02d}").format(datet.hour, datet.minute, datet.second)


def get_date_millisecs_from_tm(datet: datetime.datetime) -> str:
    """
    Get the milliseconds str part of a datetime
    Parameters
    ----------
    datet

    Returns
    -------
    milliseconds of the datetime on 3 digits
    """
    return str("{:03d}").format(int(datet.microsecond / 1000.0))


def get_min_datetime_for_timestamp() -> datetime.datetime:
    """
    Get the reference datetime for UTC
    Returns
    -------

    """
    return datetime.datetime.fromtimestamp(0, tz=pytz.UTC)


def convert_to_unix_time(date: Union[str, datetime.datetime]) -> int:
    """Return whether the string can be interpreted as a date.

    Parameters
    ----------
    date: Any
        string or datetime to convert

    Returns
    ----------
    int
        unix time in microseconds
    """

    if isinstance(date, datetime.datetime):
        if date <= get_min_datetime_for_timestamp():
            return 0
        return int(date.timestamp() * 1000000)  # microseconds

    if isinstance(date, str):

        start = pd.to_datetime(datetime.datetime.fromtimestamp(0, tz=pytz.UTC))
        try:
            end = pd.to_datetime(date)
            # Normalize data, if date is incomplete (missing timezone)
            if end.tzinfo is None:
                proxy_date = datetime.datetime(
                    end.year,
                    end.month,
                    end.day,
                    end.hour,
                    end.minute,
                    end.second,
                    0,
                    pytz.UTC,
                )
                end = pd.to_datetime(str(proxy_date))
        except pd.errors.OutOfBoundsDatetime as exc:
            # Just return string if something went wrong.
            raise ValueError(f"{date} cannot be converted to an accepted format!") from exc
        time_delta = (end - start) // pd.Timedelta("1microsecond")
        return time_delta
    raise ValueError(f"{date} cannot be converted to an accepted format!")


def stac_iso8601(_datetime: datetime.datetime) -> str:
    """
    Force _datetime timezone to UTC, convert it to iso format,
    then replace '+00:00' by 'Z' according to STAC specification.
    """
    # ref. https://gitlab.eopf.copernicus.eu/cpm/eopf-cpm/-/issues/725#note_36524
    text = _datetime.replace(tzinfo=datetime.timezone.utc).isoformat()
    if text.endswith("+00:00"):
        return f"{text[:-6]}Z"
    raise ValueError("Python datetime.isoformat did not append '+00:00' to UTC date")


def middle_date(start: datetime.datetime, end: datetime.datetime) -> datetime.datetime:
    """Return the middle time between the start_datetime and the end_datetime."""
    delta = end - start
    return start + 0.5 * delta


def force_utc_iso8601(date_iso8601: str) -> datetime.datetime:
    """Force UTC time zone, from a string in ISO 8601 format."""
    # copy behavior from commit 55b555d0 -> !732 (merged) ToCorrectedDateISO8601
    return datetime.datetime.fromisoformat(date_iso8601).replace(tzinfo=datetime.timezone.utc)
