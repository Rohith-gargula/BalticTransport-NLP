
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# BALTICTRANSPORT - GTFS VISUALIZATION MODULE
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT / "data" / "processed" / "gtfs"
OUTPUT_DIR = ROOT / "reports" / "figures"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")


# ============================================================
# COMMON FUNCTIONS
# ============================================================

def load_report(filename):
    path = INPUT_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Missing report: {path}\n"
            "Run python src/gtfs_analysis.py first."
        )

    return pd.read_csv(path)


def save_chart(fig, filename):
    output_path = OUTPUT_DIR / filename

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Created: reports/figures/{filename}")


# ============================================================
# 01. TOP 20 ROUTES
# ============================================================

def plot_top_routes():
    df = load_report("top_20_routes.csv")

    name_column = (
        "route_label"
        if "route_label" in df.columns
        else "route_short_name"
    )

    df[name_column] = df[name_column].fillna(
        df["route_id"]
    ).astype(str)

    df = df.sort_values("trip_count", ascending=False)

    fig, ax = plt.subplots(figsize=(14, 9))

    sns.barplot(
        data=df,
        x="trip_count",
        y=name_column,
        ax=ax
    )

    ax.set_title(
        "Top 20 Routes by Scheduled Trip Count",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("Scheduled Trips")
    ax.set_ylabel("Route")

    save_chart(fig, "01_top_routes.png")


# ============================================================
# 02. TOP 20 STOPS
# ============================================================

def plot_top_stops():
    df = load_report("top_20_stops.csv")

    name_column = (
        "stop_name"
        if "stop_name" in df.columns
        else "stop_id"
    )

    df[name_column] = df[name_column].fillna(
        df["stop_id"]
    ).astype(str)

    df = df.sort_values(
        "scheduled_stop_events",
        ascending=False
    )

    fig, ax = plt.subplots(figsize=(14, 9))

    sns.barplot(
        data=df,
        x="scheduled_stop_events",
        y=name_column,
        ax=ax
    )

    ax.set_title(
        "Top 20 Stops by Scheduled Stop Events",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("Scheduled Stop Events")
    ax.set_ylabel("Stop")

    save_chart(fig, "02_top_stops.png")


# ============================================================
# 03. HOURLY SERVICE DISTRIBUTION
# ============================================================

def plot_hourly_service():
    df = load_report("hourly_service_distribution.csv")

    df = df.sort_values("service_hour")

    fig, ax = plt.subplots(figsize=(13, 6))

    sns.barplot(
        data=df,
        x="service_hour",
        y="scheduled_departure_events",
        ax=ax
    )

    ax.set_title(
        "Scheduled Departure Events by GTFS Service Hour",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("GTFS Service Hour")
    ax.set_ylabel("Scheduled Departure Events")
    ax.tick_params(axis="x", rotation=45)

    save_chart(fig, "03_hourly_service.png")


# ============================================================
# 04. WEEKDAY SERVICE
# ============================================================

def plot_weekday_service():
    df = load_report("weekday_service_summary.csv")

    fig, ax = plt.subplots(figsize=(11, 6))

    sns.barplot(
        data=df,
        x="day",
        y="active_service_records",
        ax=ax
    )

    ax.set_title(
        "Regular Scheduled Service by Weekday",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("Weekday")
    ax.set_ylabel("Active Calendar Service Records")
    ax.tick_params(axis="x", rotation=30)

    save_chart(fig, "04_weekday_service.png")


# ============================================================
# 05. ROUTE TYPES
# ============================================================

def plot_route_types():
    df = load_report("route_type_summary.csv")

    df["route_type"] = df["route_type"].astype(str)

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=df,
        x="route_type",
        y="route_count",
        ax=ax
    )

    ax.set_title(
        "GTFS Routes by Route Type Code",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("GTFS Route Type Code")
    ax.set_ylabel("Number of Routes")

    save_chart(fig, "05_route_types.png")


# ============================================================
# 06. CALENDAR EXCEPTIONS
# ============================================================

def plot_calendar_exceptions():
    df = load_report("calendar_exception_summary.csv")

    if "exception_description" in df.columns:
        category_column = "exception_description"
    else:
        category_column = "exception_type"

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(
        data=df,
        x=category_column,
        y="exception_count",
        ax=ax
    )

    ax.set_title(
        "GTFS Calendar Service Exceptions",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("Exception Type")
    ax.set_ylabel("Number of Exceptions")
    ax.tick_params(axis="x", rotation=20)

    save_chart(fig, "06_calendar_exceptions.png")


# ============================================================
# 07. GEOGRAPHIC STOP DISTRIBUTION
# ============================================================

def plot_stop_locations():
    df = load_report("stop_usage.csv")

    df["stop_lat"] = pd.to_numeric(
        df["stop_lat"], errors="coerce"
    )

    df["stop_lon"] = pd.to_numeric(
        df["stop_lon"], errors="coerce"
    )

    df = df.dropna(subset=["stop_lat", "stop_lon"])

    # Approximate Latvia coordinate bounds.
    # This is a scatter plot, not an administrative boundary map.
    df = df[
        df["stop_lat"].between(55, 59)
        & df["stop_lon"].between(20, 29)
    ]

    fig, ax = plt.subplots(figsize=(10, 9))

    ax.scatter(
        df["stop_lon"],
        df["stop_lat"],
        s=9,
        alpha=0.55
    )

    ax.set_title(
        "Geographic Distribution of GTFS Stops in Latvia",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    save_chart(fig, "07_latvia_stop_distribution.png")


# ============================================================
# 08. ROUTE TRIP DISTRIBUTION
# ============================================================

def plot_route_trip_distribution():
    df = load_report("trips_per_route.csv")

    fig, ax = plt.subplots(figsize=(11, 6))

    sns.histplot(
        data=df,
        x="trip_count",
        bins=30,
        kde=True,
        ax=ax
    )

    ax.set_title(
        "Distribution of Scheduled Trips per Route",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("Scheduled Trips per Route")
    ax.set_ylabel("Number of Routes")

    save_chart(fig, "08_route_trip_distribution.png")


# ============================================================
# 09. STOP EVENT DISTRIBUTION
# ============================================================

def plot_stop_event_distribution():
    df = load_report("stop_usage.csv")

    fig, ax = plt.subplots(figsize=(11, 6))

    sns.histplot(
        data=df,
        x="scheduled_stop_events",
        bins=40,
        kde=True,
        ax=ax
    )

    ax.set_title(
        "Distribution of Scheduled Stop Events",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("Scheduled Stop Events per Stop")
    ax.set_ylabel("Number of Stops")

    save_chart(fig, "09_stop_event_distribution.png")


# ============================================================
# 10. DATA QUALITY
# ============================================================

def plot_data_quality():
    df = load_report("data_quality_checks.csv")

    df["count"] = pd.to_numeric(
        df["count"], errors="coerce"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(12, 7))

    sns.barplot(
        data=df,
        x="count",
        y="quality_check",
        ax=ax
    )

    ax.set_title(
        "GTFS Data Quality Check Results",
        fontsize=16,
        fontweight="bold"
    )
    ax.set_xlabel("Number of Detected Issues")
    ax.set_ylabel("Quality Check")

    if df["count"].max() == 0:
        ax.set_xlim(0, 1)
        ax.text(
            0.5,
            0.5,
            "ALL CHECKS PASSED\nZERO DETECTED ISSUES",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold"
        )

    save_chart(fig, "10_data_quality.png")


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print("=" * 65)
    print("BALTICTRANSPORT - GTFS VISUALIZATION GENERATOR")
    print("=" * 65)

    tasks = [
        plot_top_routes,
        plot_top_stops,
        plot_hourly_service,
        plot_weekday_service,
        plot_route_types,
        plot_calendar_exceptions,
        plot_stop_locations,
        plot_route_trip_distribution,
        plot_stop_event_distribution,
        plot_data_quality
    ]

    for number, task in enumerate(tasks, start=1):
        print(f"\n[{number}/10] {task.__name__}")
        task()

    print("\n" + "=" * 65)
    print("ALL 10 GTFS VISUALIZATIONS GENERATED SUCCESSFULLY")
    print(f"Output folder: {OUTPUT_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    main()
