"use client";

import { useState } from 'react';
import axios from 'axios';
import styles from './ViralPrediction.module.css';

export default function ViralPrediction() {
    const [formData, setFormData] = useState<Record<string, number | string>>({
        followers: 5000,
        engagement_rate: 0.08,
        past_interactions: 120,
        content_sentiment: 0.5,
        posting_hour: 19
    });

    const [prediction, setPrediction] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        const payload = {
            followers: Number(formData.followers) || 0,
            engagement_rate: Number(formData.engagement_rate) || 0,
            past_interactions: Number(formData.past_interactions) || 0,
            content_sentiment: Number(formData.content_sentiment) || 0,
            posting_hour: Number(formData.posting_hour) || 0
        };

        try {
            const res = await axios.post('http://localhost:8000/api/predict/', payload);
            setPrediction(res.data.prediction);
        } catch (err) {
            console.error("Failed to predict", err);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value;
        setFormData({
            ...formData,
            [e.target.name]: val === '' ? '' : parseFloat(val)
        });
    };

    return (
        <div className={`glass-panel ${styles.predictionContainer}`}>
            <div className={styles.formSection}>
                <h3>Test Virality Potential</h3>
                <p className="text-secondary" style={{ marginBottom: '1rem' }}>Enter post parameters to predict the probability of a post going viral.</p>

                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <label>Followers</label>
                        <input type="number" name="followers" value={formData.followers} onChange={handleChange} />
                    </div>

                    <div className={styles.inputGroup}>
                        <label>Avg Engagement Rate (0-1)</label>
                        <input type="number" step="0.01" name="engagement_rate" value={formData.engagement_rate} onChange={handleChange} />
                    </div>

                    <div className={styles.inputGroup}>
                        <label>Past Interactions</label>
                        <input type="number" name="past_interactions" value={formData.past_interactions} onChange={handleChange} />
                    </div>

                    <div className={styles.inputGroup}>
                        <label>Content Sentiment (-1 to 1)</label>
                        <input type="number" step="0.1" name="content_sentiment" value={formData.content_sentiment} onChange={handleChange} />
                    </div>

                    <div className={styles.inputGroup}>
                        <label>Posting Hour (0-23)</label>
                        <input type="number" name="posting_hour" value={formData.posting_hour} onChange={handleChange} />
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
                </div>
            )}
        </div>
    );
}
