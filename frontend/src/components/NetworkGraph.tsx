"use client";

import { useEffect, useRef, useState, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import axios from 'axios';

export default function NetworkGraph({ onNodeClick }: { onNodeClick?: (node: any) => void }) {
    const fgRef = useRef();
    const [graphData, setGraphData] = useState({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch graph data from backend
        axios.get('http://localhost:8000/api/network/')
            .then(res => {
                setGraphData(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching network data:", err);
                setLoading(false);
            });
    }, []);

    const handleNodeClick = useCallback((node: any) => {
        if (onNodeClick) {
            onNodeClick(node);
        }

        // Center/zoom on node
        if (fgRef.current) {
            // @ts-ignore
            fgRef.current.centerAt(node.x, node.y, 1000);
            // @ts-ignore
            fgRef.current.zoom(8, 2000);
        }
    }, [onNodeClick]);

    if (loading) {
        return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--text-secondary)' }}>
            Loading Network Topology...
        </div>;
    }

    return (
        <div style={{ width: '100%', height: '100%', minHeight: '500px' }}>
            <ForceGraph2D
                ref={fgRef}
                graphData={graphData}
                nodeLabel="username"
                nodeColor={(node: any) => node.influence_score > 50 ? 'var(--warning)' : (node.influence_score > 20 ? 'var(--accent-primary)' : 'var(--accent-secondary)')}
                nodeRelSize={6}
                nodeVal={(node: any) => Math.max(1, (node.influence_score || 0) / 10)}
                linkColor={() => 'rgba(255, 255, 255, 0.1)'}
                onNodeClick={handleNodeClick}
                backgroundColor="transparent"
                enableNodeDrag={true}
                enableZoomPanInteraction={true}
            />
        </div>
    );
}
