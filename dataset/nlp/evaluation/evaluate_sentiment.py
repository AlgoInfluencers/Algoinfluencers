import pandas as pd
from transformers import pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

print("=" * 60)
print("AlgoInfluencers — Sentiment Model Evaluation")
print("=" * 60)

# ------------------------------------------------------------
# 1. LOAD TWEETEVAL DATASET
# ------------------------------------------------------------

print("\nLoading TweetEval dataset...")

file_path = "dataset/nlp/tweeteval_sentiment_sample.csv"

df = pd.read_csv(file_path)

print(f"Dataset shape: {df.shape}")
print(f"Number of tweets: {len(df)}")

print("\nColumns:")
for column in df.columns:
    print(f"• {column}")


# ------------------------------------------------------------
# 2. CHECK TRUE LABELS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("TRUE SENTIMENT DISTRIBUTION")
print("=" * 60)

print(df["true_sentiment"].value_counts())


# ------------------------------------------------------------
# 3. LOAD SENTIMENT MODEL
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("LOADING SENTIMENT MODEL")
print("=" * 60)

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)

print("Model loaded successfully!")


# ------------------------------------------------------------
# 4. PREDICT SENTIMENT
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("RUNNING SENTIMENT PREDICTIONS")
print("=" * 60)

predicted_sentiments = []
prediction_confidences = []

total = len(df)

for i, text in enumerate(df["text"], start=1):

    result = sentiment_pipeline(
        text,
        truncation=True,
        max_length=512
    )[0]

    predicted_sentiments.append(result["label"].lower())
    prediction_confidences.append(result["score"])

    if i % 100 == 0:
        print(f"Processed {i}/{total} tweets")


# Add predictions to dataframe

df["predicted_sentiment"] = predicted_sentiments
df["prediction_confidence"] = prediction_confidences


# ------------------------------------------------------------
# 5. SHOW EXAMPLES
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("TRUE VS PREDICTED SENTIMENT")
print("=" * 60)

for i in range(5):

    print(f"\nExample {i + 1}")

    print("Text:")
    print(df.loc[i, "text"])

    print("True sentiment     :", df.loc[i, "true_sentiment"])
    print("Predicted sentiment:", df.loc[i, "predicted_sentiment"])
    print("Confidence         :", round(
        df.loc[i, "prediction_confidence"], 4
    ))


# ------------------------------------------------------------
# 6. CALCULATE EVALUATION METRICS
# ------------------------------------------------------------

y_true = df["true_sentiment"]
y_pred = df["predicted_sentiment"]

accuracy = accuracy_score(y_true, y_pred)

precision = precision_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

recall = recall_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)

f1 = f1_score(
    y_true,
    y_pred,
    average="macro",
    zero_division=0
)


# ------------------------------------------------------------
# 7. PRINT METRICS
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("MODEL EVALUATION RESULTS")
print("=" * 60)

print(f"\nAccuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")


# ------------------------------------------------------------
# 8. CONFUSION MATRIX
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

labels = ["negative", "neutral", "positive"]

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=labels
)

print("\n             Predicted")
print("             Neg   Neu   Pos")
print("Actual Neg  ", cm[0])
print("Actual Neu  ", cm[1])
print("Actual Pos  ", cm[2])


# ------------------------------------------------------------
# 9. CLASSIFICATION REPORT
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)

print(
    classification_report(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0
    )
)


# ------------------------------------------------------------
# 10. AVERAGE CONFIDENCE
# ------------------------------------------------------------

average_confidence = df["prediction_confidence"].mean()

print("=" * 60)
print("CONFIDENCE")
print("=" * 60)

print(
    f"Average model confidence: {average_confidence:.4f}"
)


# ------------------------------------------------------------
# 11. SAVE RESULTS
# ------------------------------------------------------------

output_file = "dataset/nlp/evaluation/tweeteval_sentiment_evaluated.csv"

df.to_csv(
    output_file,
    index=False
)

print("\n" + "=" * 60)
print("EVALUATION COMPLETE")
print("=" * 60)

print(f"\nSaved results to:")
print(output_file)

print(f"\nFinal shape: {df.shape}")