"use client";

import { useState } from 'react';
import { api } from '@/lib/api';
import styles from './ViralPrediction.module.css';

const PLATFORMS = ['Instagram', 'X', 'TikTok', 'YouTube Shorts'];
const CONTENT_TYPES = ['text', 'image', 'video', 'carousel'];
const TOPICS = ['Sports', 'Technology', 'Politics', 'Education', 'Entertainment', 'Lifestyle'];

export default function ViralPrediction() {
    const [formData, setFormData] = useState<Record<string, number | string>>({
        views: 500000,
        likes: 25000,
        comments: 3000,
        shares: 8000,
        engagement_rate: 0.08,
        sentiment_score: 0.5,
        platform: 'X',
        content_type: 'text',
        topic: 'Technology',
        hashtags: '#tech #ai',
        posting_hour: 19,
        posting_month: 6
    });

    const [prediction, setPrediction] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        const payload = {
            views: Number(formData.views) || 0,
            likes: Number(formData.likes) || 0,
            comments: Number(formData.comments) || 0,
            shares: Number(formData.shares) || 0,
            engagement_rate: Number(formData.engagement_rate) || 0,
            sentiment_score: Number(formData.sentiment_score) || 0,
            platform: String(formData.platform),
            content_type: String(formData.content_type),
            topic: String(formData.topic),
            hashtags: String(formData.hashtags || ''),
            posting_hour: Number(formData.posting_hour) || 0,
            posting_month: Number(formData.posting_month) || 1
        };

        try {
            const res = await api.predict.viralProbability(payload);
            setPrediction(res.data.prediction);
        } catch (err) {
            console.error("Failed to predict", err);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const val = e.target.value;
        const isNumericField = ['views', 'likes', 'comments', 'shares', 'engagement_rate', 'sentiment_score', 'posting_hour', 'posting_month'].includes(e.target.name);
        setFormData({
            ...formData,
            [e.target.name]: isNumericField ? (val === '' ? '' : parseFloat(val)) : val
        });
    };

    return (
        <div className={`glass-panel ${styles.predictionContainer}`}>
            <div className={styles.formSection}>
                <h3>Test Virality Potential</h3>
                <p className="text-secondary" style={{ marginBottom: '1rem' }}>
                    Predict whether a social media post will go viral based on its engagement metrics and metadata.
                </p>

                <form onSubmit={handleSubmit} className={styles.form}>
                    {/* Row: Platform, Content Type, Topic */}
                    <div className={styles.formRow}>
                        <div className={styles.inputGroup}>
                            <label>Platform</label>
                            <select name="platform" value={formData.platform} onChange={handleChange} className={styles.selectInput}>
                                {PLATFORMS.map(p => <option key={p} value={p}>{p}</option>)}
                            </select>
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Content Type</label>
                            <select name="content_type" value={formData.content_type} onChange={handleChange} className={styles.selectInput}>
                                {CONTENT_TYPES.map(ct => <option key={ct} value={ct}>{ct}</option>)}
                            </select>
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Topic</label>
                            <select name="topic" value={formData.topic} onChange={handleChange} className={styles.selectInput}>
                                {TOPICS.map(t => <option key={t} value={t}>{t}</option>)}
                            </select>
                        </div>
                    </div>

                    {/* Row: Views, Likes, Comments, Shares */}
                    <div className={styles.formRow}>
                        <div className={styles.inputGroup}>
                            <label>Views</label>
                            <input type="number" name="views" value={formData.views} onChange={handleChange} />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Likes</label>
                            <input type="number" name="likes" value={formData.likes} onChange={handleChange} />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Comments</label>
                            <input type="number" name="comments" value={formData.comments} onChange={handleChange} />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Shares</label>
                            <input type="number" name="shares" value={formData.shares} onChange={handleChange} />
                        </div>
                    </div>

                    {/* Row: Engagement Rate, Sentiment, Hour, Month */}
                    <div className={styles.formRow}>
                        <div className={styles.inputGroup}>
                            <label>Engagement Rate (0–1)</label>
                            <input type="number" step="0.01" name="engagement_rate" value={formData.engagement_rate} onChange={handleChange} />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Sentiment (−1 to 1)</label>
                            <input type="number" step="0.1" name="sentiment_score" value={formData.sentiment_score} onChange={handleChange} />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Posting Hour (0–23)</label>
                            <input type="number" name="posting_hour" value={formData.posting_hour} onChange={handleChange} />
                        </div>
                        <div className={styles.inputGroup}>
                            <label>Posting Month (1–12)</label>
                            <input type="number" name="posting_month" value={formData.posting_month} onChange={handleChange} />
                        </div>
                    </div>

                    {/* Hashtags */}
                    <div className={styles.inputGroup}>
                        <label>Hashtags</label>
                        <input type="text" name="hashtags" value={formData.hashtags} onChange={handleChange} placeholder="#viral #fyp #tech" />
                    </div>

                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? 'Analyzing...' : 'Predict Virality'}
                    </button>
                </form>
            </div>

            {prediction && (
                <div className={styles.resultSection}>
                    <h4>Prediction Results</h4>
                    <div className={styles.scoreCircle}>
                        <span className={styles.scoreValue}>{prediction.score}%</span>
                        <span className={styles.scoreLabel}>Viral Probability</span>
                    </div>

                    <div className={prediction.viral ? styles.viralYes : styles.viralNo}>
                        {prediction.viral ? "🔥 High Potential to go Viral!" : "📉 Unlikely to go Viral."}
                    </div>

                    {prediction.model_type && (
                        <div className={styles.modelInfo}>
                            <span>Model: {prediction.model_type}</span>
                            {prediction.model_auc && <span>AUC: {prediction.model_auc}</span>}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
