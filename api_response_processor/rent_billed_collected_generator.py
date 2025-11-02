from typing import Optional, Any
from datetime import date

from api_response_processor import helpers, data_classes
import copy
from config import constants
import requests

def get_comparative_delinquency(property_id, month):
    headers = helpers.get_headers()
    body = copy.deepcopy(constants.GET_COMPARATIVE_DELINQUENCY_DATA)
    body["method"]["params"]["filters"]["property_group_ids"] = [property_id]
    body["method"]["params"]["filters"]["period"]["pm"] = month #MM/YYYY
    try:
        response = requests.post(constants.REPORT_ENDPOINT,
                                 json=body,
                                 headers=headers,
                                 timeout=60)
        if response.status_code == 200:
            return response.json()
        print('Error in calling comparative delinquency endpoint:', response.status_code)
        print(response.json())
        return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
    return None

def _mm_yyyy(year: int, month: int) -> str:
    return f"{month:02d}/{year}"

def get_three_months_mm_yyyy() -> dict[str, str]:
    """
    Returns month labels in MM/YYYY for:
      - current
      - last
      - last_to_last
    If ref_date is not provided, uses today's date.
    """
    d = date.today()
    y, m = d.year, d.month

    # current
    current = _mm_yyyy(y, m)

    # last month
    last_y, last_m = (y - 1, 12) if m == 1 else (y, m - 1)
    last = _mm_yyyy(last_y, last_m)

    # last-to-last month
    if m >= 3:
        prev2_y, prev2_m = y, m - 2
    elif m == 2:
        prev2_y, prev2_m = y - 1, 12
    else:  # m == 1
        prev2_y, prev2_m = y - 1, 11
    last_to_last = _mm_yyyy(prev2_y, prev2_m)

    return {
        "current": current,
        "last": last,
        "last_to_last": last_to_last,
    }

def _to_int(v) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(round(float(v)))
    except (TypeError, ValueError):
        return None

def _extract_rent_metrics(resp: dict[str, Any]) -> dict[str, Optional[int]]:
    """
    Payload shape:
    response.result[0].reportData -> list with one row dict.
    Uses amount_due_0 (billed) and total_allocations_0 (collected).
    """
    result = resp.get("response", {}).get("result", [])
    first_result = result[0] if isinstance(result, list) and result else {}
    report_data = first_result.get("reportData", [])

    # Normalize to the first row dict
    if isinstance(report_data, list):
        row = report_data[0] if report_data else {}
    elif isinstance(report_data, dict):
        row = next((v[0] for v in report_data.values() if isinstance(v, list) and v), {})
    else:
        row = {}

    return {
        "billed": row.get("amount_due_0"),
        "collected": row.get("total_allocations_0"),
    }

def generate_rent_billed_collected_summary(property_id) -> data_classes.RentSummaryForCurrentAndLastTwoMonths:
    three_months_mm_yyyy = get_three_months_mm_yyyy()

    current_month_summary = _extract_rent_metrics(get_comparative_delinquency(property_id, three_months_mm_yyyy["current"]))
    last_month_summary = _extract_rent_metrics(get_comparative_delinquency(property_id, three_months_mm_yyyy["last"]))
    last_to_last_month_summary = _extract_rent_metrics(get_comparative_delinquency(property_id, three_months_mm_yyyy["last_to_last"]))

    print("Calculated the rent billed collected summary for " + f"{property_id}")
    return data_classes.RentSummaryForCurrentAndLastTwoMonths(
        current_month_date = three_months_mm_yyyy["current"],
        current_month_total_rent_billed = current_month_summary["billed"],
        current_month_total_rent_collected = current_month_summary["collected"],

        last_month_date = three_months_mm_yyyy["last"],
        last_month_total_rent_billed = last_month_summary["billed"],
        last_month_total_rent_collected= last_month_summary["collected"],

        month_before_last_date = three_months_mm_yyyy["last_to_last"],
        month_before_last_total_rent_billed = last_to_last_month_summary["billed"],
        month_before_last_total_rent_collected = last_to_last_month_summary["collected"],
    )