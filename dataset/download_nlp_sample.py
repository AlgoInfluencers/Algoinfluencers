import requests
import pandas as pd
import os

# Hugging Face dataset
DATASET = "arrmlet/political-social-x-us-sentiment-v1"
SPLIT = "train"

# Number of rows we want
TOTAL_ROWS = 1000

# Hugging Face allows up to 100 rows per request
ROWS_PER_REQUEST = 100

all_rows = []

print("Downloading a 1,000-row sample...")
print("This will NOT download the full 1 GB dataset.\n")

for start in range(0, TOTAL_ROWS, ROWS_PER_REQUEST):

    end = start + ROWS_PER_REQUEST - 1

    url = (
        f"https://datasets-server.huggingface.co/rows"
        f"?dataset={DATASET}"
        f"&config=default"
        f"&split={SPLIT}"
        f"&offset={start}"
        f"&length={ROWS_PER_REQUEST}"
    )

    print(f"Downloading rows {start} to {end}...")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()

    rows = [item["row"] for item in data["rows"]]

    all_rows.extend(rows)

print("\nDownloaded rows:", len(all_rows))

# Convert to DataFrame
df = pd.DataFrame(all_rows)

# Keep only useful columns
columns_to_keep = [
    "text",
    "datetime",
    "sentiment_negative",
    "sentiment_neutral",
    "sentiment_positive",
    "mentions_trump",
    "mentions_harris",
    "is_left",
    "is_right",
    "mentions_election",
    "mentions_campaign",
    "mentions_voting",
    "has_political_hashtag"
]

# Keep only columns that actually exist
columns_to_keep = [
    col for col in columns_to_keep
    if col in df.columns
]

df = df[columns_to_keep]

# Save inside the project's dataset/nlp folder
output_path = os.path.join(
    os.path.dirname(__file__),
    "political_social_sample.csv"
)

df.to_csv(output_path, index=False)

print("\n✅ Dataset saved successfully!")
print("Location:")
print(output_path)

print("\nShape:")
print(df.shape)

print("\nColumns:")
for column in df.columns:
    print("•", column)

print("\nFirst 5 posts:")
print(df.head())