from typing import Union

from api_response_processor import helpers, data_classes
import copy
from config import constants
import requests
import streamlit as st

def get_box_score(property_id, from_date, to_date):
    headers = helpers.get_headers()
    body = copy.deepcopy(constants.GET_BOX_SCORE_DATA)
    body["method"]["params"]["filters"]["property_group_ids"] = [property_id]
    body["method"]["params"]["filters"]["period"]["daterange-start"] = from_date
    body["method"]["params"]["filters"]["period"]["daterange-end"] = to_date
    try:
        response = requests.post(constants.REPORT_ENDPOINT,
                                 json=body,
                                 headers=headers,
                                 timeout=60)
        if response.status_code == 200:
            return response.json()
        print('Error in calling get reports box score endpoint:', response.status_code)
        print(response.json())
        return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
    return None

def _pct(value):
    if value is None:
        return None
    try:
        return f"{round(float(value) * 100.0, 2)}%"
    except (TypeError, ValueError):
        return None


def build_property_summary(api_response: dict) -> data_classes.PropertySummary:
    result = api_response.get("response", {}).get("result", [])
    report_data = (result[0] if result else {}).get("reportData", {})

    availability_rows = report_data.get("availability", [])
    availability = availability_rows[0] if availability_rows else {}

    pulse_rows = report_data.get("property_pulse") or report_data.get("pulse") or []
    pulse = pulse_rows[0] if pulse_rows else {}

    total_units = availability.get("total_units")
    total_rentable_units = availability.get("total_rentable_units")
    excluded_units = availability.get("excluded_units")
    percent_occupied = availability.get("percent_occupied")
    percent_leased = availability.get("percent_leased")
    avg_not_exposed_leased_units = availability.get("avg_not_exposed_leased_units")

    skips = pulse.get("skips", 0) or 0
    evictions_completed = pulse.get("evictions_completed", 0) or 0

    return data_classes.PropertySummary(
        total_units=total_units,
        total_rentable_units=total_rentable_units,
        excluded_units=excluded_units,
        occupied_units_percentage=_pct(percent_occupied),
        leased_units_percentage=_pct(percent_leased),
        trend_percentage=_pct(avg_not_exposed_leased_units),
        evictions_and_skips_occurred=skips + evictions_completed
    )

def build_unit_summary(api_response: dict) -> data_classes.UnitsSummary:
    result = api_response.get("response", {}).get("result", [])
    report_data = (result[0] if result else {}).get("reportData", {})

    availability = (report_data.get("availability") or [{}])[0]
    pulse = (report_data.get("property_pulse") or report_data.get("pulse") or [{}])[0]

    return data_classes.UnitsSummary(
        count_of_occupied_units=availability.get("occupied_units"),
        count_of_on_notice_rented_units=availability.get("notice_rented_units"),
        count_of_on_notice_unrented_units=availability.get("notice_unrented_units"),
        count_of_vacant_units=availability.get("vacant_units"),
        count_of_vacant_rented_units=availability.get("vacant_rented_units"),
        count_of_vacant_unrented_units=availability.get("vacant_unrented_units"),
        count_of_total_move_ins=pulse.get("move_ins"),
        count_of_total_move_out=pulse.get("move_outs"),
    )


def _extract_lead_metrics(resp: dict) -> dict[str, Union[int, None]]:
    """Pull new_leads, unique_visits_tours, completed, approved from a single API response."""
    result = resp.get("response", {}).get("result", [])
    report = (result[0] if result else {}).get("reportData", {})

    lead_activity = (report.get("lead_activity") or [{}])[0]
    lead_conversions = (report.get("lead_conversions") or [{}])[0]

    return {
        "new_leads": lead_activity.get("new_leads"),
        "unique_visits_tours": lead_activity.get("unique_visits_tours"),
        "completed": lead_conversions.get("completed"),
        "approved": lead_conversions.get("approved"),
    }

def build_leads_summary(api_response_current_wk: dict,
                        api_response_last_wk: dict,
                        api_response_last_before_last_wk: dict,
                        week_date: dict) -> data_classes.LeadsSummaryForThreeWeeks:
    # --- Extract metrics from each response ---
    cur = _extract_lead_metrics(api_response_current_wk)
    prev = _extract_lead_metrics(api_response_last_wk)
    prev2 = _extract_lead_metrics(api_response_last_before_last_wk)
    return data_classes.LeadsSummaryForThreeWeeks(
        # current week
        current_week_start_date=week_date.get("last_saturday"),
        current_week_end_date=week_date.get("today"),
        current_week_new_leads_count=cur["new_leads"],
        current_week_tours_count=cur["unique_visits_tours"],
        current_week_applications_completed_count=cur["completed"],
        current_week_lease_approved_count=cur["approved"],

        last_week_start_date=week_date.get("saturday_before_last_friday"),
        last_week_end_date=week_date.get("last_friday"),
        last_week_new_leads_count=prev["new_leads"],
        last_week_tours_count=prev["unique_visits_tours"],
        last_week_applications_completed_count=prev["completed"],
        last_week_lease_approved_count=prev["approved"],

        week_before_last_start_date=week_date.get("saturday_before_last_to_last_friday"),
        week_before_last_end_date=week_date.get("last_to_last_friday"),
        week_before_last_new_leads_count=prev2["new_leads"],
        week_before_last_tours_count=prev2["unique_visits_tours"],
        week_before_last_applications_completed_count=prev2["completed"],
        week_before_last_lease_approved_count=prev2["approved"],
    )

@st.cache_data(ttl="5h")
def generate_property_unit_lead_summary(property_id):
    week_dates = helpers.get_week_boundaries_fridays()
    box_score_report_current_wk = get_box_score(property_id, week_dates["last_saturday"], week_dates["today"])

    property_summary_current_wk = build_property_summary(box_score_report_current_wk)
    property_summary_dict = {week_dates["last_saturday"] + "-" + week_dates["today"]: property_summary_current_wk}

    box_score_report_last_wk = get_box_score(property_id, week_dates["saturday_before_last_friday"], week_dates["last_friday"])
    property_summary_last_wk = build_property_summary(box_score_report_last_wk)
    property_summary_dict[week_dates["saturday_before_last_friday"] + "-" + week_dates["last_friday"]] = property_summary_last_wk

    box_score_report_last_to_last_wk = get_box_score(property_id, week_dates["saturday_before_last_to_last_friday"], week_dates["last_to_last_friday"])
    property_summary_last_to_last_wk = build_property_summary(box_score_report_last_to_last_wk)
    property_summary_dict [week_dates["saturday_before_last_to_last_friday"] + "-" + week_dates["last_to_last_friday"]] = property_summary_last_to_last_wk

    print("Calculated the property summary for " + f"{property_id}")

    unit_summary_current_wk = build_unit_summary(box_score_report_current_wk)
    unit_summary_dict = {week_dates["last_saturday"] + "-" + week_dates["today"]: unit_summary_current_wk}

    unit_summary_last_wk = build_unit_summary(box_score_report_last_wk)
    unit_summary_dict[week_dates["saturday_before_last_friday"] + "-" + week_dates["last_friday"]] = unit_summary_last_wk

    unit_summary_last_to_last_wk = build_unit_summary(box_score_report_last_to_last_wk)
    unit_summary_dict[week_dates["saturday_before_last_to_last_friday"] + "-" + week_dates[
        "last_to_last_friday"]] = unit_summary_last_to_last_wk
    print("Calculated the unit summary for " + f"{property_id}")

    leads_summary = build_leads_summary(box_score_report_current_wk,
                                        box_score_report_last_wk,
                                        box_score_report_last_to_last_wk,
                                        week_dates)
    print("Calculated the lead summary for " + f"{property_id}")

    return property_summary_dict, unit_summary_dict, leads_summary