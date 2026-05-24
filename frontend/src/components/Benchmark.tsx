import React, { useState, useEffect } from "react";
import ApiService from "../services/api";

const Benchmark: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const runBenchmark = async () => {
    setLoading(true);
    try {
      const results = await ApiService.runBenchmarks();
      setData(results);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const history = await ApiService.getBenchmarkHistory();
      setData(history);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="benchmark-container">
      <h2>Performance Benchmarking</h2>
      <p>Comparison between Classical (RSA) and Post-Quantum (Kyber) algorithms.</p>
      
      <button onClick={runBenchmark} disabled={loading}>
        {loading ? "Running Benchmarks..." : "Run New Comparison"}
      </button>

      <div className="chart-area">
        {data.map((item, index) => (
          <div key={index} className="bar-group">
            <div className="bar-label">
              <strong>{item.algorithm}</strong> ({item.operation})
            </div>
            <div className="bar-wrapper">
              <div 
                className={`bar ${item.algorithm.includes('Kyber') ? 'pqc' : 'classical'}`}
                style={{ width: `${Math.min(item.execution_time_ms * 10, 100)}%` }}
              >
                {item.execution_time_ms.toFixed(2)} ms
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="analysis-note">
        <h3>Why this matters?</h3>
        <ul>
          <li><strong>RSA-2048:</strong> Fast for encryption, but highly vulnerable to Shor's algorithm on a quantum computer.</li>
          <li><strong>Kyber-512:</strong> Extremely fast performance while remaining resistant to all known quantum attacks.</li>
          <li><strong>Trade-off:</strong> Post-quantum algorithms often have larger keys but much faster computation times than traditional asymmetric crypto.</li>
        </ul>
      </div>
    </div>
  );
};

export default Benchmark;
