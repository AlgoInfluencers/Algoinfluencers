"""
Generate a realistic Twitter Impressions dataset for training the viral prediction model.

This script creates ~5000 realistic tweet records mimicking real Twitter engagement patterns.
The data follows power-law distributions for followers (most users have few, few have millions),
realistic engagement rate decay with follower count, and temporal posting patterns.

Output: dataset/twitter_viral_tweets.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path
import os

def generate_twitter_dataset(n_samples=5000, seed=42):
    np.random.seed(seed)

    # --- 1. Followers: Power-law distribution (realistic Twitter) ---
    # Most users: 100-10k, some: 10k-100k, few: 100k-1M+
    followers = np.random.lognormal(mean=7.5, sigma=1.8, size=n_samples).astype(int)
    followers = np.clip(followers, 50, 5_000_000)

    # --- 2. Engagement Rate: Inversely correlated with followers (realistic) ---
    # Micro-influencers (< 10k) have 3-8% ER, mega (> 1M) have 0.5-2%
    base_er = 0.08 - np.log1p(followers) * 0.004
    noise = np.random.normal(0, 0.01, size=n_samples)
    engagement_rate = np.clip(base_er + noise, 0.005, 0.15)

    # --- 3. Past Interactions: Correlated with followers & engagement ---
    past_interactions = (followers * engagement_rate * np.random.uniform(0.5, 1.5, size=n_samples)).astype(int)
    past_interactions = np.clip(past_interactions, 1, 500_000)

    # --- 4. Content Sentiment: Slight positive skew (positive content tends to spread) ---
    content_sentiment = np.random.beta(5, 3, size=n_samples) * 2 - 1  # Range: -1 to 1, skewed positive

    # --- 5. Posting Hour: Bimodal distribution (morning & evening peaks) ---
    morning_peak = np.random.normal(10, 1.5, size=n_samples // 2)
    evening_peak = np.random.normal(19, 2.0, size=n_samples - n_samples // 2)
    posting_hour = np.concatenate([morning_peak, evening_peak])
    np.random.shuffle(posting_hour)
    posting_hour = np.clip(posting_hour, 0, 23).astype(int)

    # --- 6. Additional realistic features ---
    # Account age in days
    account_age = np.random.lognormal(mean=6.5, sigma=1.0, size=n_samples).astype(int)
    account_age = np.clip(account_age, 30, 5000)

    # Number of hashtags in the tweet
    num_hashtags = np.random.poisson(lam=2.0, size=n_samples)
    num_hashtags = np.clip(num_hashtags, 0, 10)

    # Has media (image/video) - tweets with media get more impressions
    has_media = np.random.binomial(1, 0.6, size=n_samples)

    # Is a reply (replies generally get fewer impressions)
    is_reply = np.random.binomial(1, 0.25, size=n_samples)

    # --- 7. Impressions: Complex function of all features ---
    # Base impressions from followers
    base_impressions = followers * np.random.uniform(0.15, 0.45, size=n_samples)

    # Engagement multiplier
    engagement_multiplier = 1.0 + engagement_rate * 15

    # Peak hour bonus (9-11 AM, 6-9 PM get more reach)
    peak_bonus = np.where(
        ((posting_hour >= 9) & (posting_hour <= 11)) | ((posting_hour >= 18) & (posting_hour <= 21)),
        np.random.uniform(1.3, 1.8, size=n_samples),
        np.random.uniform(0.7, 1.1, size=n_samples)
    )

    # Sentiment bonus (positive content spreads more)
    sentiment_bonus = 1.0 + np.clip(content_sentiment, 0, 1) * 0.3

    # Media bonus
    media_bonus = np.where(has_media == 1, np.random.uniform(1.4, 2.0, size=n_samples), 1.0)

    # Reply penalty
    reply_penalty = np.where(is_reply == 1, 0.3, 1.0)

    # Hashtag effect (sweet spot is 2-3, too many hurts)
    hashtag_effect = 1.0 + np.where(num_hashtags <= 3, num_hashtags * 0.08, -num_hashtags * 0.02)

    # Calculate impressions with noise
    impressions = (
        base_impressions
        * engagement_multiplier
        * peak_bonus
        * sentiment_bonus
        * media_bonus
        * reply_penalty
        * hashtag_effect
    )
    # Add multiplicative noise
    impressions = impressions * np.random.lognormal(0, 0.4, size=n_samples)
    impressions = np.clip(impressions, 10, 50_000_000).astype(int)

    # --- 8. Virality label ---
    # A tweet is "viral" if its impressions significantly exceed what's expected for that follower count
    # We use impressions-to-follower ratio: viral if in top 15%
    impression_ratio = impressions / (followers + 1)
    viral_threshold = np.percentile(impression_ratio, 85)
    is_viral = (impression_ratio >= viral_threshold).astype(int)

    # --- Build DataFrame ---
    df = pd.DataFrame({
        'followers': followers,
        'engagement_rate': np.round(engagement_rate, 4),
        'past_interactions': past_interactions,
        'content_sentiment': np.round(content_sentiment, 4),
        'posting_hour': posting_hour,
        'account_age_days': account_age,
        'num_hashtags': num_hashtags,
        'has_media': has_media,
        'is_reply': is_reply,
        'impressions': impressions,
        'is_viral': is_viral
    })

    return df


if __name__ == "__main__":
    # Output path
    project_root = Path(__file__).resolve().parents[3]  # backend/app/models -> project root
    output_dir = project_root / "dataset"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "twitter_viral_tweets.csv"

    print("🐦 Generating realistic Twitter Impressions dataset...")
    df = generate_twitter_dataset(n_samples=5000)

    # Print summary statistics
    print(f"\n📊 Dataset shape: {df.shape}")
    print(f"   Viral tweets: {df['is_viral'].sum()} ({df['is_viral'].mean()*100:.1f}%)")
    print(f"   Non-viral:    {(1 - df['is_viral']).sum().astype(int)} ({(1-df['is_viral'].mean())*100:.1f}%)")
    print(f"\n📈 Feature Statistics:")
    print(df.describe().round(2).to_string())
    print(f"\n💾 Saving to: {output_path}")
    df.to_csv(output_path, index=False)
    print("✅ Dataset generated successfully!")
