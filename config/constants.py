BASE_URL = "https://apis.entrata.com/ext/orgs/aamliving/v1"
HEADERS = {
    "Content-Type": "application/json",
    "X-Api-Key": ""
}

REPORT_ENDPOINT = f"{BASE_URL}/reports"

GET_BOX_SCORE_DATA = {
    "auth": {
        "type": "apikey"
    },
    "requestId": 15,
    "method": {
        "name": "getReportData",
        "version": "r2",
        "params": {
            "reportName": "box_score",
            "reportVersion": "4.0",
            "filters": {
                "property_group_ids": [
                    100082999
                ],
                "period": {
                    "period_type": "daterange",
                    "daterange-start": "2025-10-25",
                    "daterange-end": "2025-10-30",
                    "allow_future_periods": "true"
                },
                "summarize_by": "property",
                "consolidate_by": "no_consolidation",
                "rows_with_no_data": "0",
                "data_set": ""
            }
        }
    }
}

GET_COMPARATIVE_DELINQUENCY_DATA = {
    "auth": {
        "type": "basic",
        "password": "password",
        "username": "username"
    },
    "requestId": 15,
    "method": {
        "name": "getReportData",
        "version": "r2",
        "params": {
            "reportName": "comparative_delinquency",
            "reportVersion": "2.3",
            "filters": {
                "property_group_ids": [
                    100082999
                ],
                "summarize_by": "summarize_by_period",
                "calculate_delinquency_using": "post_month",
                "period": {
                    "period_type": "pm",
                    "pm": "10/2025",
                    "allow_future_periods": "true"
                },
                "custom_period_date": {
                    "allow_future_periods": "true"
                },
                "custom_period": {
                    "period_type": "today",
                    "allow_future_periods": "true"
                },
                "compare_against_trailing_periods": "0",
                "include_outstanding_delinquency": "0",
                "exclude_write_offs": "0",
                "lease_status_types": [
                    "3",
                    "4",
                    "5"
                ],
                "compare_against_prior_year": "0",
                "include_credit_balances": "0",
                "consolidate_by": "no_consolidation",
                "arrange_by": "0"
            }
        }
    }
}

GET_RESIDENT_AGED_RECEIVABLES = {
    "auth": {
        "type": "basic",
        "password": "password",
        "username": "username"
    },
    "requestId": 15,
    "method": {
        "name": "getReportData",
        "version": "r2",
        "params": {
            "reportName": "resident_aged_receivables",
            "reportVersion": "3.5",
            "filters": {
                "property_group_ids": [
                    100082999
                ],
                "calculate_delinquency_using": "post_month",
                "period": {
                    "period_type": "currentpm",
                    "allow_future_periods": "false"
                },
                "custom_period": {
                    "allow_future_periods": "false"
                },
                "lease_status_type_ids": [
                    "3",
                    "4",
                    "5"
                ],
                "summarize_by": "do_not_summarize",
                "group_by": "group_by_lease",
                "display": "do_not_expand",
                "unpaid_deposit_charges": "0",
                "minimum_unpaid_balance": "",
                "inter_company": "0",
                "lease_occupancy_types": "100",
                "lease_terms": "all",
                "consolidate_by": "no_consolidation",
                "arrange_by_property": 0,
                "subtotals": 0
            }
        }
    }
}

GET_RESIDENT_RETENTION = {
    "auth": {
        "type": "basic",
        "password": "password",
        "username": "username"
    },
    "requestId": 15,
    "method": {
        "name": "getReportData",
        "version": "r2",
        "params": {
            "reportName": "resident_retention",
            "reportVersion": "3.1",
            "filters": {
                "property_group_ids": [
                    100082999
                ],
                "period": {
                    "period_type": "currentcm",
                    "allow_future_periods": "1",
                    "trailing_periods": 0,
                    "future_periods": 0
                },
                "summarize_by": "month",
                "consolidate_by": "no_consolidation",
                "lease_status": "all",
                "early_move_out_grace_period": "0",
                "drill_in_column": "",
                "unit_type_id": "",
                "property_floorplan_id": "",
                "month_id": "",
                "year_id": "",
                "previous_summarize_by": ""
            }
        }
    }
}