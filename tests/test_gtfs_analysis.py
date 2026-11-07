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
def test_analyse_exceptions(monkeypatch):
    exceptions = pd.DataFrame({
        "exception_type": [1, 1, 2, 3, "invalid", None]
    })

    saved = {}

    def fake_save_csv(df, filename):
        saved["filename"] = filename

    monkeypatch.setattr(
        gtfs_analysis, "save_csv", fake_save_csv
    )

    result = gtfs_analysis.analyse_exceptions(exceptions)

    counts = result.set_index("exception_type")[
        "exception_count"
    ].to_dict()

    descriptions = result.set_index("exception_type")[
        "exception_description"
    ].to_dict()

    assert counts == {1: 2, 2: 1, 3: 1}

    assert descriptions == {
        1: "Added service",
        2: "Removed service",
        3: "Unknown exception"
    }

    assert saved["filename"] == "calendar_exception_summary.csv"
def test_analyse_date_coverage():
    calendar = pd.DataFrame({
        "start_date": [
            "20260101",
            "20260315",
            "invalid"
        ],
        "end_date": [
            "20261231",
            "20261030",
            "invalid"
        ]
    })

    result = gtfs_analysis.analyse_date_coverage(calendar)

    assert result["earliest_calendar_start"] == "2026-01-01"
    assert result["latest_calendar_end"] == "2026-12-31"


def test_analyse_date_coverage_all_invalid():
    calendar = pd.DataFrame({
        "start_date": ["invalid", None],
        "end_date": ["invalid", None]
    })

    result = gtfs_analysis.analyse_date_coverage(calendar)

    assert result["earliest_calendar_start"] is None
    assert result["latest_calendar_end"] is None
def test_analyse_routes(monkeypatch):
    routes = pd.DataFrame({
        "route_id": ["r1", "r2"],
        "route_short_name": ["10", "20"],
        "route_long_name": ["Central", "Airport"],
        "route_type": [3, 3]
    })

    trips = pd.DataFrame({
        "route_id": ["r1", "r1", "r1", "r2", "r3", "r3"]
    })

    saved_files = []

    def fake_save_csv(df, filename):
        saved_files.append((filename, len(df)))

    monkeypatch.setattr(
        gtfs_analysis, "save_csv", fake_save_csv
    )

    result = gtfs_analysis.analyse_routes(routes, trips)

    assert result["route_id"].tolist() == ["r1", "r3", "r2"]
    assert result["trip_count"].tolist() == [3, 2, 1]

    labels = result.set_index("route_id")["route_label"].to_dict()

    assert labels == {
        "r1": "10 - Central",
        "r3": "r3",
        "r2": "20 - Airport"
    }

    assert saved_files == [
        ("trips_per_route.csv", 3),
        ("top_20_routes.csv", 3)
    ]