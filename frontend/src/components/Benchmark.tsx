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
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
          <div>
            <h2 className="text-2xl font-bold text-slate-900">Performance Benchmarking</h2>
            <p className="text-slate-500 mt-1">Comparison between Classical (RSA) and Post-Quantum (Kyber) algorithms.</p>
          </div>
          <button 
            onClick={runBenchmark} 
            disabled={loading}
            className="inline-flex items-center justify-center px-6 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-semibold transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-100"
          >
            {loading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Running Benchmarks...
              </>
            ) : "Run New Comparison"}
          </button>
        </div>

        <div className="space-y-6">
          {data.length > 0 ? (
            data.map((item, index) => (
              <div key={index} className="group">
                <div className="flex justify-between items-end mb-2">
                  <div className="text-sm font-semibold text-slate-700">
                    {item.algorithm} <span className="text-slate-400 font-normal">({item.operation})</span>
                  </div>
                  <div className="text-sm font-mono font-bold text-purple-600 bg-purple-50 px-2 py-0.5 rounded text-right">
                    {item.execution_time_ms.toFixed(2)} ms
                  </div>
                </div>
                <div className="h-4 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full transition-all duration-1000 ease-out ${
                      item.algorithm.includes('Kyber') 
                        ? 'bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.4)]' 
                        : 'bg-slate-400'
                    }`}
                    style={{ width: `${Math.min(item.execution_time_ms * 10, 100)}%` }}
                  />
                </div>
              </div>
            ))
          ) : (
            <div className="py-12 text-center border-2 border-dashed border-slate-100 rounded-2xl">
              <p className="text-slate-400">No benchmark data available. Run a comparison to see results.</p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-slate-900 rounded-2xl p-8 text-white shadow-xl">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-xl font-bold">Why this matters?</h3>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <h4 className="text-purple-400 font-bold uppercase text-xs tracking-wider">RSA-2048</h4>
            <p className="text-slate-300 text-sm leading-relaxed">
              Fast for encryption, but highly vulnerable to Shor's algorithm on a quantum computer.
            </p>
          </div>
          <div className="space-y-2">
            <h4 className="text-purple-400 font-bold uppercase text-xs tracking-wider">Kyber-512</h4>
            <p className="text-slate-300 text-sm leading-relaxed">
              Extremely fast performance while remaining resistant to all known quantum attacks.
            </p>
          </div>
          <div className="space-y-2">
            <h4 className="text-purple-400 font-bold uppercase text-xs tracking-wider">The Trade-off</h4>
            <p className="text-slate-300 text-sm leading-relaxed">
              Post-quantum algorithms often have larger keys but much faster computation times than traditional asymmetric crypto.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Benchmark;
