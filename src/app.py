
from pathlib import Path

import pandas as pd
import gradio as gr
import joblib


# ============================================================
# BALTICTRANSPORT - INTEGRATED ANALYTICS DASHBOARD
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

MODEL_PATH = ROOT / "models" / "tfidf_logreg.joblib"

RAW_GTFS_DIR = ROOT / "data" / "raw" / "gtfs" / "atd"

REPORT_DIR = ROOT / "data" / "processed" / "gtfs"

FIGURE_DIR = ROOT / "reports" / "figures"


# ============================================================
# DATA LOADING
# ============================================================

def load_report(filename):
    path = REPORT_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def get_raw_count(filename):
    path = RAW_GTFS_DIR / filename

    if not path.exists():
        return None

    try:
        return len(
            pd.read_csv(
                path,
                dtype=str,
                skipinitialspace=True
            )
        )
    except Exception:
        return None


def get_chart(filename):
    path = FIGURE_DIR / filename

    if path.exists():
        return str(path)

    return None


def format_count(value):
    if value is None:
        return "Not available"

    return f"{value:,}"


# ============================================================
# LOAD ANALYSIS REPORTS
# ============================================================

routes = load_report("top_20_routes.csv")
stops = load_report("top_20_stops.csv")
stop_usage = load_report("stop_usage.csv")

hourly = load_report("hourly_service_distribution.csv")
weekday = load_report("weekday_service_summary.csv")

exceptions = load_report("calendar_exception_summary.csv")
route_types = load_report("route_type_summary.csv")

quality = load_report("data_quality_checks.csv")


# ============================================================
# DATASET OVERVIEW
# ============================================================

def build_overview():

    route_count = get_raw_count("routes.txt")
    stop_count = get_raw_count("stops.txt")
    trip_count = get_raw_count("trips.txt")
    stop_time_count = get_raw_count("stop_times.txt")

    calendar_count = get_raw_count("calendar.txt")
    exception_count = get_raw_count("calendar_dates.txt")

    overview = f"""
# BalticTransport-NLP

### Latvia Public Transport Analytics and Multilingual NLP

This dashboard combines scheduled public transport analysis
with an experimental multilingual transport text-classification module.

---

## Dataset overview

| Dataset | Records |
|---|---:|
| Routes | {format_count(route_count)} |
| Stops | {format_count(stop_count)} |
| Trips | {format_count(trip_count)} |
| Stop-time records | {format_count(stop_time_count)} |
| Calendar records | {format_count(calendar_count)} |
| Calendar exceptions | {format_count(exception_count)} |

## GTFS analysis status

- Route analysis: Generated
- Stop analysis: Generated
- Timetable analysis: Generated
- Calendar analysis: Generated
- Data-quality analysis: Generated
- Visualizations: 10 charts generated

## Important interpretation

GTFS describes scheduled public transport services.
It does not independently provide actual vehicle positions,
observed delays, passenger counts or punctuality measurements.
"""

    return overview


# ============================================================
# NLP CLASSIFICATION
# ============================================================

def classify(text):

    if not text or not text.strip():
        return {}, "Please enter a transport-related text."

    if not MODEL_PATH.exists():
        return (
            {"Model not ready": 1.0},
            "Predictions are disabled. Collect and review sufficient "
            "real multilingual data, then train and validate a model."
        )

    try:
        model = joblib.load(MODEL_PATH)

        probabilities = model.predict_proba([text])[0]

        scores = dict(
            zip(model.classes_, probabilities)
        )

        best_topic = max(scores, key=scores.get)

        result = (
            f"Predicted topic: {best_topic} "
            f"(confidence: {scores[best_topic]:.1%}). "
            "Experimental result; not for operational decisions."
        )

        return scores, result

    except Exception as error:
        return {}, f"Model error: {error}"


# ============================================================
# DASHBOARD INTERFACE
# ============================================================

with gr.Blocks(
    title="BalticTransport-NLP",
    theme=gr.themes.Soft()
) as demo:

    gr.Markdown(
        """
        # BalticTransport-NLP

        **Latvia Public Transport Analytics and Multilingual NLP**

        Scheduled transport data analysis combined with
        Latvian, Russian and English transport text research.
        """
    )

    # --------------------------------------------------------
    # TAB 1: OVERVIEW
    # --------------------------------------------------------

    with gr.Tab("Overview"):

        gr.Markdown(build_overview())

        gr.Markdown(
            "### Data-quality validation"
        )

        if not quality.empty:
            gr.Dataframe(
                value=quality,
                label="GTFS Data Quality Results",
                interactive=False
            )
        else:
            gr.Markdown(
                "Data-quality report is not available."
            )

        gr.Markdown(
            """
            **Data source:** ATD Latvia GTFS public transport timetable.

            **Analysis type:** Scheduled public transport service analysis.
            """
        )

    # --------------------------------------------------------
    # TAB 2: ROUTE ANALYSIS
    # --------------------------------------------------------

    with gr.Tab("Route Analysis"):

        gr.Markdown(
            """
            ## Route Analysis

            Examination of routes and their scheduled trip counts.
            """
        )

        gr.Image(
            value=get_chart("01_top_routes.png"),
            label="Top 20 Routes by Scheduled Trip Count",
            interactive=False
        )

        if not routes.empty:
            gr.Dataframe(
                value=routes,
                label="Top 20 Routes",
                interactive=False
            )
        else:
            gr.Markdown("Route report unavailable.")

        gr.Image(
            value=get_chart("08_route_trip_distribution.png"),
            label="Distribution of Scheduled Trips per Route",
            interactive=False
        )

        if not route_types.empty:
            gr.Dataframe(
                value=route_types,
                label="Route Type Summary",
                interactive=False
            )

        gr.Image(
            value=get_chart("05_route_types.png"),
            label="Route Types",
            interactive=False
        )

    # --------------------------------------------------------
    # TAB 3: STOP ANALYSIS
    # --------------------------------------------------------

    with gr.Tab("Stop Analysis"):

        gr.Markdown(
            """
            ## Stop Analysis

            Examination of stop usage based on scheduled
            timetable events. These counts are not passenger counts.
            """
        )

        gr.Image(
            value=get_chart("02_top_stops.png"),
            label="Top 20 Stops",
            interactive=False
        )

        if not stops.empty:
            gr.Dataframe(
                value=stops,
                label="Top 20 Stops by Scheduled Events",
                interactive=False
            )

        gr.Image(
            value=get_chart("07_latvia_stop_distribution.png"),
            label="Geographic Distribution of Stops",
            interactive=False
        )

        gr.Image(
            value=get_chart("09_stop_event_distribution.png"),
            label="Stop Event Distribution",
            interactive=False
        )

    # --------------------------------------------------------
    # TAB 4: TIMETABLE ANALYSIS
    # --------------------------------------------------------

    with gr.Tab("Timetable Analysis"):

        gr.Markdown(
            """
            ## Timetable Analysis

            Examination of scheduled service patterns by hour
            and regular weekday calendar definitions.
            """
        )

        gr.Image(
            value=get_chart("03_hourly_service.png"),
            label="Hourly Scheduled Service",
            interactive=False
        )

        if not hourly.empty:
            gr.Dataframe(
                value=hourly,
                label="Hourly Service Summary",
                interactive=False
            )

        gr.Image(
            value=get_chart("04_weekday_service.png"),
            label="Weekday Service",
            interactive=False
        )

        if not weekday.empty:
            gr.Dataframe(
                value=weekday,
                label="Weekday Service Summary",
                interactive=False
            )

        gr.Markdown(
            """
            **Note:** Weekday summary counts regular calendar
            records. Calendar exceptions must be applied when
            calculating service for a specific date.
            """
        )

    # --------------------------------------------------------
    # TAB 5: CALENDAR ANALYSIS
    # --------------------------------------------------------

    with gr.Tab("Calendar Analysis"):

        gr.Markdown(
            """
            ## Calendar Exceptions

            Added and removed service definitions in the GTFS dataset.
            """
        )

        gr.Image(
            value=get_chart("06_calendar_exceptions.png"),
            label="Calendar Exceptions",
            interactive=False
        )

        if not exceptions.empty:
            gr.Dataframe(
                value=exceptions,
                label="Calendar Exception Summary",
                interactive=False
            )

    # --------------------------------------------------------
    # TAB 6: DATA QUALITY
    # --------------------------------------------------------

    with gr.Tab("Data Quality"):

        gr.Markdown(
            """
            ## Data Quality Assessment

            Validation of GTFS identifiers, relationships
            and required geographic information.
            """
        )

        gr.Image(
            value=get_chart("10_data_quality.png"),
            label="Data Quality Validation",
            interactive=False
        )

        if not quality.empty:
            gr.Dataframe(
                value=quality,
                label="Detailed Quality Checks",
                interactive=False
            )

        gr.Markdown(
            """
            ### Dataset limitations

            - Scheduled data is not live vehicle tracking.
            - Actual delays and punctuality are not measured.
            - Stop-time events do not measure passenger demand.
            - Calendar exceptions are important for date-specific analysis.
            """
        )

    # --------------------------------------------------------
    # TAB 7: NLP CLASSIFICATION
    # --------------------------------------------------------

    with gr.Tab("NLP Classification"):

        gr.Markdown(
            """
            ## Multilingual Transport Text Classification

            Intended languages:

            - Latvian (LV)
            - Russian (RU)
            - English (EN)

            ### Classification topics

            - Delay
            - Safety
            - Tariffs
            - Infrastructure
            - Other

            Enter a transport-related text below.
            """
        )

        text_input = gr.Textbox(
            label="Transport Text",
            lines=5,
            placeholder=(
                "Enter Latvian, Russian or English "
                "transport-related text..."
            )
        )

        classify_button = gr.Button(
            "Classify Text",
            variant="primary"
        )

        topic_scores = gr.Label(
            label="Classification Scores"
        )

        result_message = gr.Textbox(
            label="Result / Model Status",
            interactive=False
        )

        classify_button.click(
            fn=classify,
            inputs=text_input,
            outputs=[topic_scores, result_message]
        )

        gr.Markdown(
            """
            **Research limitation:**

            The current dataset contains only 12 synthetic
            smoke-test examples. This is insufficient for
            meaningful model training or evaluation.

            Predictions remain disabled until sufficient real,
            permitted and reviewed data is collected and a
            valid model is trained and evaluated.
            """
        )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    gr.Markdown(
        """
        ---

        **BalticTransport-NLP**

        GTFS timetable analytics | Multilingual transport NLP

        Research prototype - experimental, not for operational decisions.
        """
    )


# ============================================================
# LAUNCH APPLICATION
# ============================================================

if __name__ == "__main__":
    demo.launch()
