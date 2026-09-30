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
# SENTIMENT FEATURE ENGINEERING
# ============================================================

print("\n" + "=" * 60)
print("SENTIMENT FEATURE ENGINEERING")
print("=" * 60)

# Convert predicted sentiment into numerical features.
# These are one-hot encoded sentiment indicators.

df["sentiment_negative"] = (
    df["predicted_sentiment"] == "negative"
).astype(int)

df["sentiment_neutral"] = (
    df["predicted_sentiment"] == "neutral"
).astype(int)

df["sentiment_positive"] = (
    df["predicted_sentiment"] == "positive"
).astype(int)


print("\nNumerical sentiment features created:")
print("• sentiment_negative")
print("• sentiment_neutral")
print("• sentiment_positive")
print("• sentiment_confidence")


print("\nExample:")

print(
    df[
        [
            "predicted_sentiment",
            "sentiment_confidence",
            "sentiment_negative",
            "sentiment_neutral",
            "sentiment_positive"
        ]
    ].head(5)
)

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

# ============================================================
# NLP RESULT ANALYSIS
# ============================================================

print("\n" + "=" * 60)
print("NLP RESULT ANALYSIS")
print("=" * 60)


# ------------------------------------------------------------
# 1. Sentiment distribution
# ------------------------------------------------------------

print("\n1. SENTIMENT DISTRIBUTION")

sentiment_distribution = (
    df["predicted_sentiment"]
    .value_counts()
    .sort_index()
)

print(sentiment_distribution)


# ------------------------------------------------------------
# 2. Average confidence by sentiment
# ------------------------------------------------------------

print("\n2. AVERAGE CONFIDENCE BY SENTIMENT")

confidence_by_sentiment = (
    df.groupby("predicted_sentiment")["sentiment_confidence"]
    .mean()
    .sort_values(ascending=False)
)

print(confidence_by_sentiment)


# ------------------------------------------------------------
# 3. Low-confidence predictions
# ------------------------------------------------------------

print("\n3. LOW-CONFIDENCE PREDICTIONS")

low_confidence = df[
    df["sentiment_confidence"] < 0.60
]

print(
    f"Predictions below 60% confidence: "
    f"{len(low_confidence)}"
)

print(
    f"Percentage: "
    f"{len(low_confidence) / len(df) * 100:.2f}%"
)


# ------------------------------------------------------------
# 4. Sentiment and political indicators
# ------------------------------------------------------------

print("\n4. SENTIMENT BY POLITICAL INDICATORS")

if "is_left" in df.columns:

    print("\nAverage sentiment confidence for left-indicator posts:")

    left_posts = df[df["is_left"] == 1]

    print(f"Posts: {len(left_posts)}")

    if len(left_posts) > 0:
        print(
            left_posts["predicted_sentiment"]
            .value_counts()
        )


if "is_right" in df.columns:

    print("\nAverage sentiment confidence for right-indicator posts:")

    right_posts = df[df["is_right"] == 1]

    print(f"Posts: {len(right_posts)}")

    if len(right_posts) > 0:
        print(
            right_posts["predicted_sentiment"]
            .value_counts()
        )


# ------------------------------------------------------------
# 5. Election-related posts
# ------------------------------------------------------------

print("\n5. ELECTION-RELATED POSTS")

if "mentions_election" in df.columns:

    election_posts = df[
        df["mentions_election"] == 1
    ]

    print(
        f"Election-related posts: "
        f"{len(election_posts)}"
    )

    if len(election_posts) > 0:
        print(
            election_posts["predicted_sentiment"]
            .value_counts()
        )


# ------------------------------------------------------------
# 6. Campaign-related posts
# ------------------------------------------------------------

print("\n6. CAMPAIGN-RELATED POSTS")

if "mentions_campaign" in df.columns:

    campaign_posts = df[
        df["mentions_campaign"] == 1
    ]

    print(
        f"Campaign-related posts: "
        f"{len(campaign_posts)}"
    )

    if len(campaign_posts) > 0:
        print(
            campaign_posts["predicted_sentiment"]
            .value_counts()
        )