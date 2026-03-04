"use client";

import { useState } from 'react';
import { api } from '@/lib/api';
import styles from './SimulationPanel.module.css';

export default function SimulationPanel({
    selectedNode,
}: {
    selectedNode: any;
}) {
    const [modelType, setModelType] = useState('ic');
    const [running, setRunning] = useState(false);
    const [result, setResult] = useState<any>(null);

    const runSimulation = async () => {
        if (!selectedNode) return;

        setRunning(true);
        try {
            const res = await api.simulation.run({
                model_type: modelType,
                seed_nodes: [selectedNode.id],
                probability: 0.15,
                steps: 10
            });
            setResult(res.data);
        } catch (err) {
            console.error("Simulation failed", err);
        } finally {
            setRunning(false);
        }
    };

    return (
        <div className={`glass-panel ${styles.panel}`}>
            <div className={styles.header}>
                <h3>Influence Diffusion Simulator</h3>
                <select
                    className={styles.select}
                    value={modelType}
                    onChange={(e) => setModelType(e.target.value)}
                >
                    <option value="ic">Independent Cascade</option>
                    <option value="lt">Linear Threshold</option>
                </select>
            </div>

            <div className={styles.content}>
                {!selectedNode ? (
                    <div className={styles.emptyState}>
                        <p>Select a node from the graph to use as the seed for the simulation.</p>
                    </div>
                ) : (
                    <div className={styles.activeState}>
                        <div className={styles.seedInfo}>
                            <span>Seed Node:</span>
                            <strong>@{selectedNode.username}</strong>
                            <span className={styles.badge}>Influence: {selectedNode.influence_score || 0}</span>
                        </div>

                        <button
                            className={`btn-primary ${styles.simBtn}`}
                            onClick={runSimulation}
                            disabled={running}
                        >
                            {running ? 'Simulating...' : `Simulate ${modelType.toUpperCase()} Spread`}
                        </button>

                        {result && (
                            <div className={styles.resultBox}>
                                <div className={styles.resultStat}>
                                    <span>Total Reached</span>
                                    <h4>{result.total_activated} Users</h4>
                                </div>
                                <div className={styles.resultStat}>
                                    <span>Network Reach</span>
                                    <h4>{result.reach_percentage}%</h4>
                                </div>

                                <div className={styles.timeline}>
                                    <p className={styles.timelineTitle}>Propagation Timeline</p>
                                    <div className={styles.timelineBar}>
                                        {result.history.map((step: any, idx: number) => (
                                            <div
                                                key={idx}
                                                className={styles.timelineStep}
                                                style={{ width: `${Math.max(5, (step.new_activations.length / result.total_activated) * 100)}%` }}
                                                title={`Step ${step.step}: ${step.new_activations.length} new`}
                                            ></div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
