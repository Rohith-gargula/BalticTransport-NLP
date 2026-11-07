from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "dataset.csv"
OUT = ROOT / "reports" / "figures"

def main():
    df = pd.read_csv(DATA)
    OUT.mkdir(parents=True, exist_ok=True)
    for col, title, fname in [
        ("language", "Records by language", "language_distribution.png"),
        ("label", "Topic label distribution", "label_distribution.png"),
    ]:
        ax = df[col].value_counts().sort_index().plot(kind="bar", title=title)
        ax.set_xlabel(col); ax.set_ylabel("Rows")
        plt.tight_layout(); plt.savefig(OUT / fname, dpi=160); plt.close()
    df["text_length"] = df["text_clean"].str.split().str.len()
    ax = df.boxplot(column="text_length", by="language")
    ax.set_title("Text length by language"); ax.set_xlabel("Language"); ax.set_ylabel("Words")
    plt.suptitle(""); plt.tight_layout(); plt.savefig(OUT / "text_length_by_language.png", dpi=160); plt.close()
    print(f"Charts saved under {OUT}")

if __name__ == "__main__":
    main()
