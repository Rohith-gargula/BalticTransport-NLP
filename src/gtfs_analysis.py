
from pathlib import Path
import json
import pandas as pd


# ============================================================
# BALTICTRANSPORT-NLP
# Module: GTFS Public Transport Analytics
# Dataset: ATD Latvia GTFS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

GTFS_DIR = ROOT / "data" / "raw" / "gtfs" / "atd"
OUTPUT_DIR = ROOT / "data" / "processed" / "gtfs"
REPORT_DIR = ROOT / "reports" / "gtfs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# 1. DATA LOADING
# ------------------------------------------------------------

def load_gtfs(filename):
    path = GTFS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"GTFS file not found: {path}")

    df = pd.read_csv(
        path,
        dtype=str,
        skipinitialspace=True,
        encoding="utf-8-sig",
        keep_default_na=False
    )

    df.columns = df.columns.str.strip()

    for column in df.columns:
        if df[column].dtype == object:
            df[column] = df[column].str.strip()

    return df


def check_columns(df, filename, required):
    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename}: missing columns {sorted(missing)}"
        )


def save_csv(df, filename):
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  Created: {filename}")


# ------------------------------------------------------------
# 2. DATA QUALITY ANALYSIS
# ------------------------------------------------------------

def build_quality_report(
    routes, stops, trips, stop_times, calendar, exceptions
):
    route_ids = set(routes["route_id"])
    stop_ids = set(stops["stop_id"])
    trip_ids = set(trips["trip_id"])

    regular_services = set(calendar["service_id"])
    exception_services = set(exceptions["service_id"])

    known_services = regular_services | exception_services

    checks = [
        (
            "Duplicate route IDs",
            routes["route_id"].duplicated().sum()
        ),
        (
            "Duplicate stop IDs",
            stops["stop_id"].duplicated().sum()
        ),
        (
            "Duplicate trip IDs",
            trips["trip_id"].duplicated().sum()
        ),
        (
            "Duplicate trip-stop-sequence records",
            stop_times.duplicated(
                subset=["trip_id", "stop_sequence"]
            ).sum()
        ),
        (
            "Trips referencing unknown routes",
            len(set(trips["route_id"]) - route_ids)
        ),
        (
            "Stop times referencing unknown trips",
            len(set(stop_times["trip_id"]) - trip_ids)
        ),
        (
            "Stop times referencing unknown stops",
            len(set(stop_times["stop_id"]) - stop_ids)
        ),
        (
            "Trips without any calendar definition",
            len(set(trips["service_id"]) - known_services)
        ),
        (
            "Stops missing latitude",
            pd.to_numeric(
                stops["stop_lat"], errors="coerce"
            ).isna().sum()
        ),
        (
            "Stops missing longitude",
            pd.to_numeric(
                stops["stop_lon"], errors="coerce"
            ).isna().sum()
        )
    ]

    return pd.DataFrame(
        checks,
        columns=["quality_check", "count"]
    )


# ------------------------------------------------------------
# 3. ROUTE ANALYSIS
# ------------------------------------------------------------

def analyse_routes(routes, trips):
    route_trips = (
        trips.groupby("route_id")
        .size()
        .reset_index(name="trip_count")
    )

    result = route_trips.merge(
        routes,
        on="route_id",
        how="left"
    )

    # Ensure route-name columns exist.
    for column in ["route_short_name", "route_long_name"]:
        if column not in result.columns:
            result[column] = ""

        result[column] = (
            result[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.strip('"')
        )

    # Create readable route labels.
    result["route_label"] = (
        result["route_short_name"]
        + " - "
        + result["route_long_name"]
    )

    result["route_label"] = (
        result["route_label"]
        .str.strip(" -")
    )

    result.loc[
        result["route_label"] == "",
        "route_label"
    ] = result["route_id"]

    columns = [
        "route_id",
        "route_short_name",
        "route_long_name",
        "route_label",
        "route_type",
        "trip_count"
    ]

    result = result[
        [column for column in columns if column in result.columns]
    ].sort_values(
        "trip_count",
        ascending=False
    )

    save_csv(result, "trips_per_route.csv")
    save_csv(result.head(20), "top_20_routes.csv")

    return result


# ------------------------------------------------------------
# 4. STOP ANALYSIS
# ------------------------------------------------------------

def analyse_stops(stops, stop_times):
    visits = (
        stop_times.groupby("stop_id")
        .size()
        .reset_index(name="scheduled_stop_events")
    )

    result = visits.merge(
        stops,
        on="stop_id",
        how="left"
    )

    result["stop_lat"] = pd.to_numeric(
        result["stop_lat"],
        errors="coerce"
    )

    result["stop_lon"] = pd.to_numeric(
        result["stop_lon"],
        errors="coerce"
    )

    result = result.sort_values(
        "scheduled_stop_events",
        ascending=False
    )

    save_csv(result, "stop_usage.csv")
    save_csv(result.head(20), "top_20_stops.csv")

    return result


# ------------------------------------------------------------
# 5. TIMETABLE SERVICE-HOUR ANALYSIS
# ------------------------------------------------------------

def analyse_service_hours(stop_times):
    departure_hours = (
        stop_times["departure_time"]
        .astype(str)
        .str.extract(r"^(\d+):\d{2}:\d{2}$")[0]
    )

    departure_hours = pd.to_numeric(
        departure_hours,
        errors="coerce"
    )

    result = (
        departure_hours.dropna()
        .astype(int)
        .value_counts()
        .sort_index()
        .rename_axis("service_hour")
        .reset_index(name="scheduled_departure_events")
    )

    save_csv(result, "hourly_service_distribution.csv")

    return result


# ------------------------------------------------------------
# 6. WEEKDAY SERVICE ANALYSIS
# ------------------------------------------------------------

def analyse_weekday_service(calendar):
    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday"
    ]

    records = []

    for day in weekdays:
        active_count = (
            pd.to_numeric(
                calendar[day],
                errors="coerce"
            )
            .fillna(0)
            .eq(1)
            .sum()
        )

        records.append({
            "day": day.capitalize(),
            "active_service_records": int(active_count)
        })

    result = pd.DataFrame(records)

    save_csv(result, "weekday_service_summary.csv")

    return result


# ------------------------------------------------------------
# 7. CALENDAR EXCEPTION ANALYSIS
# ------------------------------------------------------------

def analyse_exceptions(exceptions):
    exception_values = pd.to_numeric(
        exceptions["exception_type"],
        errors="coerce"
    )

    result = (
        exception_values
        .value_counts()
        .sort_index()
        .rename_axis("exception_type")
        .reset_index(name="exception_count")
    )

    descriptions = {
        1: "Added service",
        2: "Removed service"
    }

    result["exception_description"] = (
        result["exception_type"]
        .map(descriptions)
        .fillna("Unknown exception")
    )

    save_csv(result, "calendar_exception_summary.csv")

    return result


# ------------------------------------------------------------
# 8. ROUTE TYPE ANALYSIS
# ------------------------------------------------------------

def analyse_route_types(routes):
    result = (
        routes.groupby("route_type")
        .size()
        .reset_index(name="route_count")
        .sort_values(
            "route_count",
            ascending=False
        )
    )

    save_csv(result, "route_type_summary.csv")

    return result


# ------------------------------------------------------------
# 9. DATASET DATE COVERAGE
# ------------------------------------------------------------

def analyse_date_coverage(calendar):
    starts = pd.to_datetime(
        calendar["start_date"],
        format="%Y%m%d",
        errors="coerce"
    )

    ends = pd.to_datetime(
        calendar["end_date"],
        format="%Y%m%d",
        errors="coerce"
    )

    return {
        "earliest_calendar_start": (
            str(starts.min().date())
            if starts.notna().any()
            else None
        ),
        "latest_calendar_end": (
            str(ends.max().date())
            if ends.notna().any()
            else None
        )
    }


# ------------------------------------------------------------
# 10. MAIN ANALYTICS PIPELINE
# ------------------------------------------------------------

def main():

    print("\n" + "=" * 65)
    print("BALTICTRANSPORT - GTFS ANALYTICS")
    print("=" * 65)

    # Load datasets.
    print("\n[1/8] Loading GTFS datasets...")

    routes = load_gtfs("routes.txt")
    stops = load_gtfs("stops.txt")
    trips = load_gtfs("trips.txt")
    stop_times = load_gtfs("stop_times.txt")
    calendar = load_gtfs("calendar.txt")
    exceptions = load_gtfs("calendar_dates.txt")

    counts = {
        "routes": len(routes),
        "stops": len(stops),
        "trips": len(trips),
        "stop_time_records": len(stop_times),
        "calendar_records": len(calendar),
        "calendar_exceptions": len(exceptions)
    }

    for name, count in counts.items():
        print(f"  {name.replace('_', ' ').title()}: {count:,}")

    # Validate required columns.
    print("\n[2/8] Checking dataset structure...")

    check_columns(routes, "routes.txt", [
        "route_id", "route_type"
    ])

    check_columns(stops, "stops.txt", [
        "stop_id", "stop_name", "stop_lat", "stop_lon"
    ])

    check_columns(trips, "trips.txt", [
        "route_id", "service_id", "trip_id"
    ])

    check_columns(stop_times, "stop_times.txt", [
        "trip_id", "stop_id", "arrival_time",
        "departure_time", "stop_sequence"
    ])

    check_columns(calendar, "calendar.txt", [
        "service_id", "monday", "tuesday", "wednesday",
        "thursday", "friday", "saturday", "sunday",
        "start_date", "end_date"
    ])

    check_columns(exceptions, "calendar_dates.txt", [
        "service_id", "date", "exception_type"
    ])

    print("  All required columns are available.")

    # Data quality.
    print("\n[3/8] Running data-quality checks...")

    quality = build_quality_report(
        routes, stops, trips, stop_times, calendar, exceptions
    )

    save_csv(quality, "data_quality_checks.csv")

    # Route analytics.
    print("\n[4/8] Analysing routes...")

    route_summary = analyse_routes(routes, trips)

    # Stop analytics.
    print("\n[5/8] Analysing stops...")

    stop_summary = analyse_stops(stops, stop_times)

    # Timetable analytics.
    print("\n[6/8] Analysing timetable patterns...")

    hourly_summary = analyse_service_hours(stop_times)

    weekday_summary = analyse_weekday_service(calendar)

    exception_summary = analyse_exceptions(exceptions)

    # Route types.
    route_type_summary = analyse_route_types(routes)

    # Date coverage.
    print("\n[7/8] Checking calendar date coverage...")

    date_coverage = analyse_date_coverage(calendar)

    # Build JSON summary.
    print("\n[8/8] Creating final project report...")

    summary = {
        "project": "BalticTransport-NLP",
        "module": "GTFS Public Transport Analytics",
        "dataset": "ATD Latvia GTFS",
        "record_counts": counts,
        "date_coverage": date_coverage,
        "data_quality": {
            row["quality_check"]: int(row["count"])
            for _, row in quality.iterrows()
        },
        "analytics": {
            "routes_analysed": len(route_summary),
            "stops_analysed": len(stop_summary),
            "service_hours_analysed": len(hourly_summary),
            "weekday_categories": len(weekday_summary),
            "route_types": len(route_type_summary),
            "calendar_exception_types": len(exception_summary)
        },
        "limitations": [
            "GTFS describes scheduled public transport services.",
            "It does not provide actual vehicle positions.",
            "It does not establish observed delays or punctuality.",
            "Stop-event counts are timetable records, not passenger counts.",
            "Calendar exceptions must be applied for date-specific service."
        ]
    }

    summary_path = REPORT_DIR / "gtfs_analysis_summary.json"

    with open(
        summary_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Human-readable report.
    report_lines = [
        "BALTICTRANSPORT - GTFS ANALYTICS",
        "=" * 55,
        "",
        "DATASET RECORD COUNTS",
        "-" * 55
    ]

    for name, count in counts.items():
        report_lines.append(f"{name}: {count:,}")

    report_lines.extend([
        "",
        "CALENDAR DATE COVERAGE",
        "-" * 55,
        f"Earliest start: {date_coverage['earliest_calendar_start']}",
        f"Latest end: {date_coverage['latest_calendar_end']}",
        "",
        "DATA QUALITY",
        "-" * 55
    ])

    for _, row in quality.iterrows():
        report_lines.append(
            f"{row['quality_check']}: {int(row['count']):,}"
        )

    report_lines.extend([
        "",
        "ANALYTICS SUMMARY",
        "-" * 55,
        f"Routes analysed: {len(route_summary):,}",
        f"Stops analysed: {len(stop_summary):,}",
        f"Service hours analysed: {len(hourly_summary):,}",
        f"Weekday categories: {len(weekday_summary):,}",
        f"Route types: {len(route_type_summary):,}",
        f"Calendar exception types: {len(exception_summary):,}",
        "",
        "DATA LIMITATIONS",
        "-" * 55
    ])

    report_lines.extend(
        "- " + item for item in summary["limitations"]
    )

    report_path = REPORT_DIR / "gtfs_analysis_summary.txt"

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:
        file.write("\n".join(report_lines))

    # Final output.
    print("\n" + "=" * 65)
    print("DATASET RECORD COUNTS")

    for name, count in counts.items():
        print(f"{name}: {count:,}")

    print("\nCALENDAR DATE COVERAGE")
    print(
        "Earliest start:",
        date_coverage["earliest_calendar_start"]
    )
    print(
        "Latest end:",
        date_coverage["latest_calendar_end"]
    )

    print("\nDATA QUALITY")

    for _, row in quality.iterrows():
        print(
            f"{row['quality_check']}: {int(row['count'])}"
        )

    print("\nDATA LIMITATIONS")

    for item in summary["limitations"]:
        print(f"- {item}")

    print("\nReports saved in:", REPORT_DIR)
    print("GTFS ANALYSIS COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
