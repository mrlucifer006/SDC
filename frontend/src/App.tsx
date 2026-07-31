import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import GateDashboard from './pages/GateDashboard';
import ChallengeView from './pages/ChallengeView';
import AdminDashboard from './pages/AdminDashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import { Shield, LogOut } from 'lucide-react';
import { getAuthToken, removeAuthToken } from './services/api';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  const checkAuth = () => {
    const token = getAuthToken();
    if (token) {
      setIsAuthenticated(true);
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setIsAdmin(payload.role === 'admin');
      } catch (e) {
        setIsAdmin(false);
      }
    } else {
      setIsAuthenticated(false);
      setIsAdmin(false);
    }
  };

  useEffect(() => {
    checkAuth();
    window.addEventListener('auth-change', checkAuth);
    return () => window.removeEventListener('auth-change', checkAuth);
  }, []);

  const handleLogout = () => {
    removeAuthToken();
    checkAuth();
  };

  return (
    <Router>
      <div className="min-h-screen p-6 font-sans">
        <header className="flex justify-between items-center mb-10 pb-4 border-b border-gray-800">
          <div>
            <h1 className="text-3xl font-rune rune-glow text-metroid-rune tracking-widest uppercase">
              Siege of the Five Gates
            </h1>
            <p className="text-gray-400 mt-2">Breach the ancient fortifications</p>
          </div>
          <nav className="flex gap-4 items-center">
            {isAuthenticated ? (
              <>
                {!isAdmin && <Link to="/" className="btn-rune">Gates</Link>}
                {isAdmin && (
                  <Link to="/admin" className="btn-rune !border-metroid-accent !text-metroid-accent hover:!bg-metroid-accent">
                    <Shield size={16} className="inline mr-1" /> Admin
                  </Link>
                )}
                <button 
                  onClick={handleLogout} 
                  className="text-gray-500 hover:text-metroid-rune text-sm flex items-center gap-1 ml-4"
                >
                  <LogOut size={16} /> Logout
                </button>
              </>
            ) : (
              <Link to="/login" className="btn-rune">Login</Link>
            )}
          </nav>
        </header>

        <main>
          <Routes>
            <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
            <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/" />} />
            
            <Route path="/" element={isAuthenticated ? (isAdmin ? <Navigate to="/admin" /> : <GateDashboard />) : <Navigate to="/login" />} />
            <Route path="/challenge/:gateId" element={isAuthenticated && !isAdmin ? <ChallengeView /> : <Navigate to={isAdmin ? "/admin" : "/login"} />} />
            <Route path="/admin" element={isAuthenticated && isAdmin ? <AdminDashboard /> : <Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
