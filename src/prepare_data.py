from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "sample_smoke_test.csv"
OUTPUT = ROOT / "data" / "processed" / "dataset.csv"
LABELS = {"delay", "safety", "tariffs", "infrastructure", "other"}
LANGS = {"lv", "ru", "en"}

def normalize(text):
    text = str(text or "").lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def main():
    df = pd.read_csv(INPUT)
    required = {"id", "language", "text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    df["text_clean"] = df["text"].map(normalize)
    df = df[df["language"].isin(LANGS) & df["label"].isin(LABELS)]
    df = df[df["text_clean"].str.len() > 0]
    df = df.drop_duplicates(subset=["language", "text_clean"]).reset_index(drop=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"Saved {len(df)} rows to {OUTPUT}")
    if df.get("is_synthetic", pd.Series(False, index=df.index)).astype(str).str.lower().eq("true").all():
        print("NOTICE: all rows are synthetic smoke-test data; do not use for performance claims.")

if __name__ == "__main__":
    main()
