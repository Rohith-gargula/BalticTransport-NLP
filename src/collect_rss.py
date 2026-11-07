
from pathlib import Path
import pandas as pd
import feedparser
from email.utils import parsedate_to_datetime

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "rss_sources.csv"
OUTPUT = ROOT / "data" / "raw" / "rss_articles.csv"

COLUMNS = [
    "id", "language", "text", "label", "source",
    "source_url", "published_at", "is_synthetic"
]


def parse_date(entry):
    value = entry.get("published") or entry.get("updated")

    if not value:
        return ""

    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError, OverflowError):
        return ""


def main():
    if not CONFIG.exists():
        raise SystemExit("RSS configuration file not found.")

    sources = pd.read_csv(CONFIG).fillna("")

    required = {
        "id", "source", "language", "feed_url",
        "terms_url", "permission_status"
    }

    if not required.issubset(sources.columns):
        raise SystemExit("RSS configuration is missing required columns.")

    approved = sources[
        sources["permission_status"].str.lower().eq("approved")
    ]

    if approved.empty:
        print("No approved RSS feeds configured.")
        print("Review source terms and permissions before collection.")
        return

    records = []

    for _, source in approved.iterrows():
        if source["language"] not in {"lv", "ru", "en"}:
            print(f"Skipping unsupported language: {source['language']}")
            continue

        if not source["feed_url"].startswith("https://"):
            print(f"Skipping non-HTTPS feed: {source['source']}")
            continue

        print(f"Reading feed: {source['source']}")

        feed = feedparser.parse(
            source["feed_url"],
            request_headers={"User-Agent": "BalticTransport-NLP/1.0"}
        )

        if feed.bozo:
            print(f"Feed warning: {source['source']}: {feed.bozo_exception}")

        for entry in feed.entries:
            article_url = entry.get("link", "").strip()

            if not article_url.startswith("https://"):
                continue

            records.append({
                "id": f"{source['id']}-{len(records) + 1}",
                "language": source["language"],
                "text": "",
                "label": "",
                "source": source["source"],
                "source_url": article_url,
                "published_at": parse_date(entry),
                "is_synthetic": False
            })

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result = pd.DataFrame(records, columns=COLUMNS)
    result.to_csv(OUTPUT, index=False, encoding="utf-8")

    print(f"Collected {len(result)} article metadata records.")
    print(f"Saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
