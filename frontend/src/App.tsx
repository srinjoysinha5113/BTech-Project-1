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
    <div className="App">
      <header className="App-header">
        <h1>BTech PQC Project</h1>
        <div className="nav-controls">
          {isAuthenticated && (
            <>
              <button onClick={() => setView("messaging")} className={view === "messaging" ? "active" : ""}>Messaging</button>
              <button onClick={() => setView("benchmark")} className={view === "benchmark" ? "active" : ""}>Benchmark</button>
              <button 
                onClick={() => {
                  sessionStorage.removeItem("token");
                  setIsAuthenticated(false);
                }}
                className="logout-btn"
              >
                Logout
              </button>
            </>
          )}
        </div>
      </header>
      <main>
        {!isAuthenticated ? (
          <Auth onLogin={() => setIsAuthenticated(true)} />
        ) : (
          view === "messaging" ? <SecureMessaging /> : <Benchmark />
        )}
      </main>
    </div>
  );
}

export default App;
