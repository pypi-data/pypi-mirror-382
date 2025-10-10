from datetime import datetime

import pytest

from intuned_browser import process_date

dates = [
    ["22/11/2024 21:19:05", datetime(2024, 11, 22)],
    ["13/12/2024", datetime(2024, 12, 13)],
    ["22/11/2024 15:35:06", datetime(2024, 11, 22)],
    ["01/17/2025 3:00:00 PM CT", datetime(2025, 1, 17)],
    ["10/25/2024", datetime(2024, 10, 25)],
    ["09/18/2024", datetime(2024, 9, 18)],
    ["10/23/2024 12:06 PM CST", datetime(2024, 10, 23)],
    ["11/24/2024", datetime(2024, 11, 24)],
    ["11/28/2024 1:59:59 AM", datetime(2024, 11, 28)],
    ["11/1/2024 10:30:00 PM", datetime(2024, 11, 1)],
    ["12/09/2024 9:00 AM", datetime(2024, 12, 9)],
    ["12/05/2024 9:00 AM", datetime(2024, 12, 5)],
    ["11/07/2024", datetime(2024, 11, 7)],
    ["12/10/2024", datetime(2024, 12, 10)],
    ["10/21/2024", datetime(2024, 10, 21)],
    ["10/08/2024", datetime(2024, 10, 8)],
    ["12/19/2024 - 2:00 PM", datetime(2024, 12, 19)],
    ["11/15/2024", datetime(2024, 11, 15)],
    ["8/16/2019", datetime(2019, 8, 16)],
    ["9/28/2024", datetime(2024, 9, 28)],
    ["5 Dec 2024 8:00 AM PST", datetime(2024, 12, 5)],
    ["11 Sep 2024", datetime(2024, 9, 11)],
    ["November 14, 2024", datetime(2024, 11, 14)],
    ["January 31, 2025, 5:00 pm", datetime(2025, 1, 31)],
    ["22/11/2024 19:45:00", datetime(2024, 11, 22)],
    ["09/01/2025 15:00:00", datetime(2025, 9, 1)],
    ["06/01/2023 11:00:00", datetime(2023, 6, 1)],
    ["04/30/2023 14:00:00", datetime(2023, 4, 30)],
]


@pytest.mark.parametrize("date", dates, ids=lambda x: x[0])
def test_process_date(date: tuple[str, datetime]):
    assert process_date(date[0]) == date[1]
