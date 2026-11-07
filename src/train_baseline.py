from pathlib import Path
import json
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "dataset.csv"
MODEL_DIR = ROOT / "models"

def main():
    df = pd.read_csv(DATA)
    # Small smoke-test set may not have enough samples per class for a split.
    counts = df["label"].value_counts()
    if len(df) < 30 or counts.min() < 2:
        raise SystemExit("Dataset too small for meaningful evaluation. Collect and label more real data first.")
    X_train, X_test, y_train, y_test = train_test_split(
        df["text_clean"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=50000, sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    report = classification_report(y_test, pred, output_dict=True, zero_division=0)
    metrics = {"accuracy": accuracy_score(y_test, pred), "classification_report": report,
               "confusion_matrix": confusion_matrix(y_test, pred, labels=model.classes_).tolist(),
               "labels": model.classes_.tolist(), "random_state": 42}
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_DIR / "tfidf_logreg.joblib")
    (MODEL_DIR / "baseline_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
