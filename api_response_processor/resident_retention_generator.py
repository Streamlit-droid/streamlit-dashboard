import copy

import requests

from config import constants
import streamlit as st
from api_response_processor import helpers, data_classes

def get_resident_retention(property_id):
    headers = helpers.get_headers()
    body = copy.deepcopy(constants.GET_RESIDENT_RETENTION)
    body["method"]["params"]["filters"]["property_group_ids"] = [property_id]
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

def get_expiring_and_renewals(resp: dict) -> data_classes.ResidentRetentionSummaryForCurrentMonth:
    """
    Extracts expiring_leases and renewals from API response.

    Args:
        resp (dict): API response dictionary

    Returns:
        dict: {
            "expiring_leases": int or None,
            "renewals": int or None
        }
    """
    result = resp.get("response", {}).get("result", [])
    report_data = (result[0] if result else {}).get("reportData", [])
    row = report_data[0] if report_data else {}

    expiring_leases = row.get("expiring_leases")
    renewals = row.get("renewals")

    return data_classes.ResidentRetentionSummaryForCurrentMonth(
        expiring_leases=expiring_leases,
        renewals=renewals
    )

@st.cache_data(ttl="1h")
def build_resident_retention(property_id):
    rr = get_resident_retention(property_id)
    print("Calculated the resident retention summary for " + f"{property_id}")
    return get_expiring_and_renewals(rr)
