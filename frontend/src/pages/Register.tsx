import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';
import { UserPlus } from 'lucide-react';

export default function Register() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      await api.post('/auth/register', { username, email, password });
      // On success, redirect to login
      navigate('/login');
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] animate-[fadeIn_0.5s_ease-out]">
      <div className="stone-panel p-10 rounded-2xl w-full max-w-md">
        <h2 className="text-3xl font-bold font-rune rune-glow text-metroid-accent mb-8 text-center tracking-widest uppercase">New Challenger</h2>
        
        {error && (
          <div className="bg-red-900/30 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg mb-6 backdrop-blur-md">
            {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="flex flex-col gap-5">
          <div className="group">
            <label className="block text-gray-400 text-xs font-bold mb-2 uppercase tracking-widest group-focus-within:text-metroid-accent transition-colors">Username</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input-rune"
              required
              placeholder="Enter your alias..."
            />
          </div>

          <div className="group">
            <label className="block text-gray-400 text-xs font-bold mb-2 uppercase tracking-widest group-focus-within:text-metroid-accent transition-colors">Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-rune"
              required
              placeholder="Comms channel..."
            />
          </div>
          
          <div className="group">
            <label className="block text-gray-400 text-xs font-bold mb-2 uppercase tracking-widest group-focus-within:text-metroid-accent transition-colors">Password</label>
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
            <UserPlus size={20} /> Join the Siege
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-gray-500">
          Already have an account? <Link to="/login" className="text-metroid-accent font-bold hover:text-white transition-colors">Log in</Link>
        </div>
      </div>
    </div>
  );
}
