import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api, setAuthToken } from '../services/api';
import { LogIn } from 'lucide-react';

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      // FastAPI OAuth2PasswordRequestForm expects form data
      const data = await api.post('/auth/token', formData, true);
      setAuthToken(data.access_token);
      window.dispatchEvent(new Event('auth-change'));
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] animate-[fadeIn_0.5s_ease-out]">
      <div className="stone-panel p-10 rounded-2xl w-full max-w-md">
        <h2 className="text-3xl font-bold font-rune rune-glow text-metroid-rune mb-8 text-center tracking-widest uppercase">Enter the Gates</h2>
        
        {error && (
          <div className="bg-red-900/30 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg mb-6 backdrop-blur-md">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="flex flex-col gap-5">
          <div className="group">
            <label className="block text-gray-400 text-xs font-bold mb-2 uppercase tracking-widest group-focus-within:text-metroid-rune transition-colors">Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-rune"
              required
              placeholder="Your email..."
            />
          </div>
          
          <div className="group">
            <label className="block text-gray-400 text-xs font-bold mb-2 uppercase tracking-widest group-focus-within:text-metroid-rune transition-colors">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-rune"
              required
              placeholder="••••••••"
            />
          </div>

          <button 
            type="submit" 
            className="btn-rune mt-4 flex items-center justify-center gap-3 w-full"
          >
            <LogIn size={20} /> Authenticate
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-gray-500">
          New challenger? <Link to="/register" className="text-metroid-rune font-bold hover:text-white transition-colors">Register here</Link>
        </div>
      </div>
    </div>
  );
}
