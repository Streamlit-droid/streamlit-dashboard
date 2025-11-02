from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo
import streamlit as st
import copy
from config import constants

#new ones
def get_headers():
    api_key = st.secrets["API_KEY"]
    headers = copy.deepcopy(constants.HEADERS)
    headers["X-Api-Key"] = api_key
    return headers

def _last_weekday_on_or_before(d: date, weekday: int) -> date:
    """Most recent 'weekday' on or before d."""
    return d - timedelta((d.weekday() - weekday) % 7)

def get_week_boundaries_fridays() -> dict:
    """
    Returns:
      {
        "today": ...,
        "last_saturday": ...,
        "last_friday": ...,
        "saturday_before_last_friday": ...,
        "last_to_last_friday": ...,
        "saturday_before_last_to_last_friday": ...
      }

    Rules:
    - 'last_saturday' is the most recent Saturday on or before today
      (equals today if today is Saturday).
    - 'last_friday' is the most recent Friday on or before today
      (equals today if today is Friday).
    - 'saturday_before_last_friday' is the Saturday immediately BEFORE that Friday.
    - 'last_to_last_friday' is one week before 'last_friday'.
    - 'saturday_before_last_to_last_friday' is the Saturday immediately BEFORE that Friday.
    """
    FRIDAY = 4  # Monday=0 ... Sunday=6
    SATURDAY = 5
    today = datetime.now(ZoneInfo("America/Chicago")).date()

    last_saturday = _last_weekday_on_or_before(today, SATURDAY)
    last_friday = _last_weekday_on_or_before(last_saturday, FRIDAY)

    # Saturday immediately before a given Friday is 6 days earlier
    saturday_before_last_friday = last_friday - timedelta(days=6)

    last_to_last_friday = last_friday - timedelta(days=7)
    saturday_before_last_to_last_friday = last_to_last_friday - timedelta(days=6)

    return {
        "today": today.isoformat(),
        "last_saturday": last_saturday.isoformat(),
        "last_friday": last_friday.isoformat(),
        "saturday_before_last_friday": saturday_before_last_friday.isoformat(),
        "last_to_last_friday": last_to_last_friday.isoformat(),
        "saturday_before_last_to_last_friday": saturday_before_last_to_last_friday.isoformat(),
    }