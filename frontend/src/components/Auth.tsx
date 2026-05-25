import React, { useState } from "react";
import ApiService from "../services/api";

interface AuthProps {
  onLogin: () => void;
}

const Auth: React.FC<AuthProps> = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    try {
      if (isLogin) {
        await ApiService.login({ username, password });
        onLogin();
      } else {
        await ApiService.register({ username, password, email });
        setIsLogin(true);
      }
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="max-w-md w-full mx-auto bg-white rounded-2xl shadow-xl border border-slate-100 p-8 overflow-hidden">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-extrabold text-slate-900 tracking-tight">
          {isLogin ? "Welcome Back" : "Create Account"}
        </h2>
        <p className="mt-2 text-sm text-slate-500">
          {isLogin 
            ? "Sign in to access your PQC-secured session" 
            : "Register to start experimenting with post-quantum security"}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
          <input 
            type="text" 
            placeholder="johndoe" 
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            value={username} 
            onChange={(e) => setUsername(e.target.value)} 
            required 
          />
        </div>
        {!isLogin && (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
            <input 
              type="email" 
              placeholder="john@example.com" 
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              value={email} 
              onChange={(e) => setEmail(e.target.value)} 
              required 
            />
          </div>
        )}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
          <input 
            type="password" 
            placeholder="••••••••" 
            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
            value={password} 
            onChange={(e) => setPassword(e.target.value)} 
            required 
          />
        </div>
        
        {error && (
          <div className="bg-red-50 border border-red-100 text-red-600 text-sm p-3 rounded-lg flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            {error}
          </div>
        )}

        <button 
          type="submit" 
          className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-purple-200 transition-all active:scale-[0.98]"
        >
          {isLogin ? "Sign In" : "Sign Up"}
        </button>
      </form>

      <div className="mt-8 pt-6 border-t border-slate-100 text-center">
        <button 
          className="text-sm font-semibold text-purple-600 hover:text-purple-700 transition-colors"
          onClick={() => setIsLogin(!isLogin)}
        >
          {isLogin ? "New here? Create an account" : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
};

export default Auth;
