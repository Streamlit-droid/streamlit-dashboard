from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class PropertySummary:
    total_units: Union[int, str, None]
    total_rentable_units: Union[int, str, None]
    excluded_units: Union[int, str, None]
    occupied_units_percentage: Union[int, str, None]
    leased_units_percentage: Union[int, str, None]
    trend_percentage: Union[int, str, None]
    evictions_and_skips_occurred: Union[int, str, None]

@dataclass
class UnitsSummary:
    count_of_occupied_units: Union[int, str, None]
    count_of_on_notice_rented_units: Union[int, str, None]
    count_of_on_notice_unrented_units: Union[int, str, None]
    count_of_vacant_units: Union[int, str, None]
    count_of_vacant_rented_units: Union[int, str, None]
    count_of_vacant_unrented_units: Union[int, str, None]
    count_of_total_move_ins: Union[int, str, None]
    count_of_total_move_out: Union[int, str, None]

@dataclass
class ResidentRetentionSummaryForCurrentMonth:
    expiring_leases: Union[int, None]
    renewals: Union[int, None]

@dataclass
class RentSummaryForCurrentAndLastTwoMonths:
    current_month_date: Union[str, None]
    current_month_total_rent_billed: Union[int, None]
    current_month_total_rent_collected: Union[int, None]

    last_month_date: Union[str, None]
    last_month_total_rent_billed: Union[int, None]
    last_month_total_rent_collected: Union[int, None]

    month_before_last_date: Union[str, None]
    month_before_last_total_rent_billed: Union[int, None]
    month_before_last_total_rent_collected: Union[int, None]

@dataclass
class DelinquencyForThreeMonths:
    current_month_delinquency: Union[float, None]
    last_month_delinquency: Union[float, None]
    month_before_last_delinquency: Union[float, None]

@dataclass
class LeadsSummaryForThreeWeeks:
    current_week_start_date: Union[int, str, None]
    current_week_end_date: Union[int, str, None]
    current_week_new_leads_count: Union[int, str, None]
    current_week_tours_count: Union[int, str, None]
    current_week_applications_completed_count: Union[int, str, None]
    current_week_lease_approved_count: Union[int, str, None]

    last_week_start_date: Union[int, str, None]
    last_week_end_date: Union[int, str, None]
    last_week_new_leads_count: Union[int, str, None]
    last_week_tours_count: Union[int, str, None]
    last_week_applications_completed_count: Union[int, str, None]
    last_week_lease_approved_count: Union[int, str, None]

    week_before_last_start_date: Union[int, str, None]
    week_before_last_end_date: Union[int, str, None]
    week_before_last_new_leads_count: Union[int, str, None]
    week_before_last_tours_count: Union[int, str, None]
    week_before_last_applications_completed_count: Union[int, str, None]
    week_before_last_lease_approved_count: Union[int, str, None]