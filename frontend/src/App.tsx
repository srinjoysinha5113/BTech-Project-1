import { useState, useEffect } from "react";
import "./App.css";
import Auth from "./components/Auth";
import SecureMessaging from "./components/SecureMessaging";
import Benchmark from "./components/Benchmark";
import ApiService from "./services/api";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [view, setView] = useState<"messaging" | "benchmark">("messaging");

  useEffect(() => {
    const token = ApiService.getToken();
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">Q</span>
            </div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">BTech PQC</h1>
          </div>
          
          <div className="flex items-center gap-4">
            {isAuthenticated && (
              <>
                <nav className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg">
                  <button 
                    onClick={() => setView("messaging")} 
                    className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                      view === "messaging" 
                        ? "bg-white text-purple-600 shadow-sm" 
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    Messaging
                  </button>
                  <button 
                    onClick={() => setView("benchmark")} 
                    className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                      view === "benchmark" 
                        ? "bg-white text-purple-600 shadow-sm" 
                        : "text-slate-600 hover:text-slate-900"
                    }`}
                  >
                    Benchmark
                  </button>
                </nav>
                <button 
                  onClick={() => {
                    sessionStorage.removeItem("token");
                    setIsAuthenticated(false);
                  }}
                  className="ml-4 text-sm font-medium text-slate-500 hover:text-red-600 transition-colors"
                >
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!isAuthenticated ? (
          <div className="mt-12">
            <Auth onLogin={() => setIsAuthenticated(true)} />
          </div>
        ) : (
          <div className="animate-fade-in">
            {view === "messaging" ? <SecureMessaging /> : <Benchmark />}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
