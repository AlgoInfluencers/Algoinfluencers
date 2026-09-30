import pandas as pd
from pathlib import Path

import requests


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

TEXT_URL = (
    "https://raw.githubusercontent.com/cardiffnlp/"
    "tweeteval/main/datasets/sentiment/test_text.txt"
)

LABEL_URL = (
    "https://raw.githubusercontent.com/cardiffnlp/"
    "tweeteval/main/datasets/sentiment/test_labels.txt"
)

OUTPUT_FILE = BASE_DIR / "tweeteval_sentiment_sample.csv"

SAMPLE_SIZE = 1000


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("AlgoInfluencers — TweetEval Evaluation Dataset")
print("=" * 60)


# ============================================================
# DOWNLOAD TEXT
# ============================================================

print("\nDownloading TweetEval test texts...")

text_response = requests.get(TEXT_URL)

text_response.raise_for_status()

texts = text_response.text.splitlines()

print(f"Total test texts available: {len(texts)}")


# ============================================================
# DOWNLOAD LABELS
# ============================================================

print("\nDownloading TweetEval test labels...")

label_response = requests.get(LABEL_URL)

label_response.raise_for_status()

labels = label_response.text.splitlines()

print(f"Total test labels available: {len(labels)}")


# ============================================================
# CHECK DATA
# ============================================================

if len(texts) != len(labels):

    raise ValueError(
        "Number of texts and labels do not match."
    )


# ============================================================
# CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(
    {
        "text": texts[:SAMPLE_SIZE],
        "label": [int(x) for x in labels[:SAMPLE_SIZE]]
    }
)


# ============================================================
# CONVERT LABELS TO SENTIMENT
# ============================================================

label_mapping = {
    0: "negative",
    1: "neutral",
    2: "positive"
}

df["true_sentiment"] = df["label"].map(label_mapping)


# ============================================================
# DISPLAY DATASET INFORMATION
# ============================================================

print("\n" + "=" * 60)
print("DATASET INFORMATION")
print("=" * 60)

print(f"\nSample size: {len(df)}")

print("\nColumns:")
for column in df.columns:
    print(f"• {column}")


# ============================================================
# LABEL DISTRIBUTION
# ============================================================

print("\n" + "=" * 60)
print("TRUE SENTIMENT DISTRIBUTION")
print("=" * 60)

print(
    df["true_sentiment"]
    .value_counts()
)


# ============================================================
# SHOW EXAMPLES
# ============================================================

print("\n" + "=" * 60)
print("SAMPLE DATA")
print("=" * 60)

for i, row in df.head(5).iterrows():

    print(f"\nExample {i + 1}")
    print(f"Text: {row['text']}")
    print(f"True label: {row['true_sentiment']}")


# ============================================================
# SAVE
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("\n" + "=" * 60)
print("✅ DOWNLOAD COMPLETE")
print("=" * 60)

print("\nSaved dataset:")
print(OUTPUT_FILE)

print(f"\nShape: {df.shape}")