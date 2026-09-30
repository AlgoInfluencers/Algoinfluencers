import pandas as pd
import re
from pathlib import Path

from transformers import pipeline


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "political_social_cleaned.csv"
OUTPUT_FILE = BASE_DIR / "political_social_sentiment.csv"

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("AlgoInfluencers — NLP / Sentiment Analysis")
print("=" * 60)


# ============================================================
# LOAD CLEANED DATASET
# ============================================================

print("\n📂 Loading cleaned dataset...")

df = pd.read_csv(INPUT_FILE)

print(f"File: {INPUT_FILE.name}")
print(f"Dataset shape: {df.shape}")

print("\nColumns:")
for column in df.columns:
    print(f"• {column}")


# ============================================================
# CHECK TEXT DATA
# ============================================================

print("\n" + "=" * 60)
print("TEXT DATA CHECK")
print("=" * 60)

missing_text = df["clean_text"].isna().sum()

print(f"Missing clean_text values: {missing_text}")
print(f"Total posts: {len(df)}")


# ============================================================
# REMOVE EMPTY TEXT
# ============================================================

df["clean_text"] = df["clean_text"].fillna("").astype(str)

before_count = len(df)

df = df[df["clean_text"].str.strip().str.len() > 0].copy()

removed_empty = before_count - len(df)

print(f"Removed empty posts: {removed_empty}")
print(f"Posts available for sentiment analysis: {len(df)}")


# ============================================================
# LOAD SENTIMENT MODEL
# ============================================================

print("\n" + "=" * 60)
print("LOADING SENTIMENT MODEL")
print("=" * 60)

print(f"\nModel: {MODEL_NAME}")
print("Loading model...")
print("The first run may take some time.")

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model=MODEL_NAME
)

print("\n✅ Sentiment model loaded successfully!")


# ============================================================
# SENTIMENT ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("RUNNING SENTIMENT ANALYSIS")
print("=" * 60)

print(f"\nAnalyzing {len(df)} posts...")
print("This may take some time on CPU.\n")


predicted_sentiments = []
sentiment_confidences = []


for index, text in enumerate(df["clean_text"], start=1):

    result = sentiment_pipeline(
        text,
        truncation=True,
        max_length=512
    )[0]

    label = result["label"].lower()
    confidence = result["score"]

    predicted_sentiments.append(label)
    sentiment_confidences.append(confidence)

    # Progress message every 50 posts
    if index % 50 == 0 or index == len(df):
        print(
            f"Processed {index}/{len(df)} posts "
            f"({index / len(df) * 100:.1f}%)"
        )


# ============================================================
# ADD RESULTS TO DATAFRAME
# ============================================================

df["predicted_sentiment"] = predicted_sentiments
df["sentiment_confidence"] = sentiment_confidences


# ============================================================
# SENTIMENT SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("SENTIMENT SUMMARY")
print("=" * 60)

sentiment_counts = df["predicted_sentiment"].value_counts()

print("\nNumber of posts by sentiment:")

for sentiment, count in sentiment_counts.items():

    percentage = count / len(df) * 100

    print(
        f"{sentiment.capitalize():<10} : "
        f"{count:>4} posts "
        f"({percentage:.2f}%)"
    )


# ============================================================
# AVERAGE CONFIDENCE
# ============================================================

average_confidence = df["sentiment_confidence"].mean()

print(
    f"\nAverage model confidence: "
    f"{average_confidence:.4f}"
)


# ============================================================
# SHOW SAMPLE RESULTS
# ============================================================

print("\n" + "=" * 60)
print("SAMPLE SENTIMENT RESULTS")
print("=" * 60)

for i, (_, row) in enumerate(df.head(5).iterrows(), start=1):

    print(f"\nPost {i}")

    print(
        f"Text: "
        f"{row['clean_text'][:200]}..."
    )

    print(
        f"Predicted sentiment: "
        f"{row['predicted_sentiment']}"
    )

    print(
        f"Confidence: "
        f"{row['sentiment_confidence']:.4f}"
    )


# ============================================================
# SAVE DATASET
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

print("\n" + "=" * 60)
print("✅ NLP ANALYSIS COMPLETE")
print("=" * 60)

print("\nSaved sentiment dataset:")

print(OUTPUT_FILE)

print(f"\nFinal dataset shape: {df.shape}")

print("\nNew columns added:")
print("• predicted_sentiment")
print("• sentiment_confidence")