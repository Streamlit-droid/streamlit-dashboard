from freezegun import freeze_time
from api_response_processor import rent_billed_collected_generator

@freeze_time("2026-01-05")
def test_get_three_months_mm_yyyy():
    date_dict = rent_billed_collected_generator.get_three_months_mm_yyyy()
    assert date_dict["current"] == "01/2026"
    assert date_dict["last"] == "12/2025"
    assert date_dict["last_to_last"] == "11/2025"

@freeze_time("2025-12-05")
def test_get_three_months_mm_yyyy():
    date_dict = rent_billed_collected_generator.get_three_months_mm_yyyy()
    assert date_dict["current"] == "12/2025"
    assert date_dict["last"] == "11/2025"
    assert date_dict["last_to_last"] == "10/2025"