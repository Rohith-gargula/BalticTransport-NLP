
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.prepare_data import normalize


def test_normalize_spaces_and_case():
    assert normalize("  HELLO   world ") == "hello world"


def test_normalize_url():
    assert "https://" not in normalize("Read https://example.com today")

