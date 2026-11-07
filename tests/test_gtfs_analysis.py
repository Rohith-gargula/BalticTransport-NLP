import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import gtfs_analysis


def test_analyse_route_types(monkeypatch):
    routes = pd.DataFrame({
        "route_type": [3, 3, 2, 0, 3]
    })

    saved = {}

    def fake_save_csv(df, filename):
        saved["filename"] = filename

    monkeypatch.setattr(
        gtfs_analysis,
        "save_csv",
        fake_save_csv
    )

    result = gtfs_analysis.analyse_route_types(routes)

    counts = result.set_index("route_type")["route_count"].to_dict()

    assert counts == {0: 1, 2: 1, 3: 3}
    assert result.iloc[0]["route_type"] == 3
    assert result.iloc[0]["route_count"] == 3
    assert saved["filename"] == "route_type_summary.csv"
def test_analyse_service_hours(monkeypatch):
    stop_times = pd.DataFrame({
        "departure_time": [
            "08:00:00",
            "08:30:00",
            "09:15:00",
            "25:10:00",
            "invalid"
        ]
    })

    saved = {}

    def fake_save_csv(df, filename):
        saved["filename"] = filename

    monkeypatch.setattr(
        gtfs_analysis,
        "save_csv",
        fake_save_csv
    )

    result = gtfs_analysis.analyse_service_hours(stop_times)

    counts = result.set_index("service_hour")[
        "scheduled_departure_events"
    ].to_dict()

    assert counts == {8: 2, 9: 1, 25: 1}
    assert saved["filename"] == "hourly_service_distribution.csv"
def test_analyse_weekday_service(monkeypatch):
    calendar = pd.DataFrame({
        "monday": [1, 1, 0],
        "tuesday": [1, 0, 1],
        "wednesday": [0, 0, 1],
        "thursday": ["1", "invalid", None],
        "friday": [0, 1, 0],
        "saturday": [0, 0, 0],
        "sunday": [1, 1, 1]
    })

    saved = {}

    def fake_save_csv(df, filename):
        saved["filename"] = filename

    monkeypatch.setattr(
        gtfs_analysis,
        "save_csv",
        fake_save_csv
    )

    result = gtfs_analysis.analyse_weekday_service(calendar)

    counts = result.set_index("day")[
        "active_service_records"
    ].to_dict()

    assert counts == {
        "Monday": 2,
        "Tuesday": 2,
        "Wednesday": 1,
        "Thursday": 1,
        "Friday": 1,
        "Saturday": 0,
        "Sunday": 3
    }

    assert saved["filename"] == "weekday_service_summary.csv"