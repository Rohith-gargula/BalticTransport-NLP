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