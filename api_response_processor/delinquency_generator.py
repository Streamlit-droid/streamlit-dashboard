import copy
from typing import Any

import requests

from api_response_processor import helpers, data_classes
from config import constants
import streamlit as st

def get_resident_aged_receivables(property_id):
    headers = helpers.get_headers()
    body = copy.deepcopy(constants.GET_RESIDENT_AGED_RECEIVABLES)
    body["method"]["params"]["filters"]["property_group_ids"] = [property_id]
    try:
        response = requests.post(constants.REPORT_ENDPOINT,
                                 json=body,
                                 headers=headers,
                                 timeout=60)
        if response.status_code == 200:
            return response.json()
        print('Error in calling resident aged receivables endpoint:', response.status_code)
        print(response.json())
        return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
    return None

def sum_delinquency_buckets(api_response: dict[str, Any]) -> data_classes.DelinquencyForThreeMonths:
    """
    Returns the sums of 'thirty_days', 'sixty_days', and 'ninety_days'
    across all rows in response.result[0].reportData.
    """
    result = api_response.get("response", {}).get("result", [])
    report_data = (result[0] if result else {}).get("reportData", []) or []

    def bucket_sum(key: str) -> float:
        total = 0.0
        for row in report_data:
            try:
                total += float(row.get(key) or 0)
            except (TypeError, ValueError):
                # Skip non-numeric entries
                continue
        return round(total, 2)
    return data_classes.DelinquencyForThreeMonths(
        current_month_delinquency = bucket_sum("thirty_days"),
        last_month_delinquency = bucket_sum("sixty_days"),
        month_before_last_delinquency = bucket_sum("ninety_days")
    )

@st.cache_data(ttl="5h")
def generate_delinquency_report(property_id) -> data_classes.DelinquencyForThreeMonths:
    resident_aged_receivables = get_resident_aged_receivables(property_id)
    print("Calculated the delinquency summary for " + f"{property_id}")
    return sum_delinquency_buckets(resident_aged_receivables)