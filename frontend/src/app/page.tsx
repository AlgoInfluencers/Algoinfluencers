"use client";

import { Activity, Share2, TrendingUp, Users } from "lucide-react";
import { useEffect, useState } from "react";
import dynamic from 'next/dynamic';
import styles from "./page.module.css";
import SimulationPanel from "@/components/SimulationPanel";
import ViralPrediction from "@/components/ViralPrediction";
import { api } from "@/lib/api";

// Dynamically import the NetworkGraph with SSR disabled since it uses canvas/window
const NetworkGraph = dynamic(() => import('@/components/NetworkGraph'), {
  ssr: false,
  loading: () => <p>Loading graph engine...</p>
});

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [networkStats, setNetworkStats] = useState<{ total_nodes: number; total_edges: number } | null>(null);
  const [networkStatsError, setNetworkStatsError] = useState(false);

  useEffect(() => {
    api.network.getStats()
      .then((res) => setNetworkStats(res.data))
      .catch((err) => {
        console.error("Error fetching network statistics:", err);
        setNetworkStatsError(true);
      });
  }, []);

  const handleNodeClick = (node: any) => {
    setSelectedNode(node);
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarLogo}>
          <Share2 className={styles.logoIcon} />
          <h2>AlgoInfluencers</h2>
        </div>

        <nav className={styles.navLinks}>
          <button
            className={`${styles.navItem} ${activeTab === 'dashboard' ? styles.active : ''}`}
            onClick={() => setActiveTab('dashboard')}
            style={{ background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', width: '100%' }}
          >
            <Activity /> Dashboard
          </button>
          <button
            className={`${styles.navItem} ${activeTab === 'prediction' ? styles.active : ''}`}
            onClick={() => setActiveTab('prediction')}
            style={{ background: 'none', border: 'none', cursor: 'pointer', textAlign: 'left', width: '100%' }}
          >
            <TrendingUp /> Viral Prediction
          </button>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header className={styles.header}>
          <div>
            <h1 className="gradient-text">
              {activeTab === 'dashboard' ? "Platform Overview" : "Viral Content Predictor"}
            </h1>
            <p className="text-secondary">
              {activeTab === 'dashboard' ? "Analyze influence and predict viral trends in real-time." : "Machine learning powered virality scoring based on author and content metrics."}
            </p>
          </div>
        </header>

        {activeTab === 'dashboard' && (
          <>
            {/* Dashboard Metrics */}
            <section className={styles.metricsGrid}>
              <div className={`glass-panel ${styles.metricCard}`}>
                <div className={styles.metricHeader}>
                  <Users size={20} color="var(--accent-secondary)" />
                  <span>Network Nodes</span>
                </div>
                <h3>{networkStats ? networkStats.total_nodes : "—"}</h3>
                <span className={networkStatsError ? styles.neutral : styles.positive}>
                  {networkStatsError ? "Unavailable" : "Loaded dataset"}
                </span>
              </div>

              <div className={`glass-panel ${styles.metricCard}`}>
                <div className={styles.metricHeader}>
                  <Share2 size={20} color="var(--accent-primary)" />
                  <span>Network Edges</span>
                </div>
                <h3>{networkStats ? networkStats.total_edges : "—"}</h3>
                <span className={styles.neutral}>
                  {networkStats ? "Directed connections" : networkStatsError ? "Unavailable" : "Loading..."}
                </span>
              </div>

              <div className={`glass-panel ${styles.metricCard}`}>
                <div className={styles.metricHeader}>
                  <TrendingUp size={20} color="var(--success)" />
                  <span>Influencers</span>
                </div>
                <h3>Top 10%</h3>
                <span className={styles.positive}>High PageRank</span>
              </div>
            </section>

            <div style={{ display: 'flex', gap: '2rem', height: '600px' }}>
              {/* Main Visualization */}
              <section className={`glass-panel ${styles.mainVisPlaceholder}`} style={{ flex: 2 }}>
                <h2 style={{ padding: '0 0 1rem 0' }}>Influence Network Topology</h2>
                <div className={styles.graphMockup} style={{ height: '100%', border: 'none' }}>
                  <NetworkGraph onNodeClick={handleNodeClick} />
                </div>
              </section>

              {/* Simulation Side Panel */}
              <div style={{ flex: 1, height: '100%', overflow: 'auto' }}>
                <SimulationPanel selectedNode={selectedNode} />
              </div>
            </div>
          </>
        )}

        {activeTab === 'prediction' && (
          <ViralPrediction />
        )}
      </main>
    </div>
  );
}
