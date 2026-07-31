import React, { useState, useEffect } from 'react';
import { Users, Activity, Target } from 'lucide-react';
import { api } from '../services/api';

interface LeaderboardEntry {
  username: string;
  email: string;
  total_score: number;
  total_solve_time_seconds: number;
  rank: number;
  is_locked: boolean;
}

interface GateStat {
  gate_id: number;
  unlocked: number;
  completed: number;
}

interface Submission {
  id: number;
  username: string;
  email: string;
  gate_id: number;
  passed: boolean;
  execution_time_ms: number;
  timestamp: string;
}

export default function AdminDashboard() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [stats, setStats] = useState<GateStat[]>([]);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [malpracticeEnabled, setMalpracticeEnabled] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [lbData, statsData, subsData, settingsData] = await Promise.all([
          api.get('/admin/leaderboard'),
          api.get('/admin/stats'),
          api.get('/admin/submissions'),
          api.get('/game/settings'),
        ]);
        setLeaderboard(lbData);
        setStats(statsData);
        setSubmissions(subsData);
        setMalpracticeEnabled(settingsData.malpractice_enabled);
      } catch (error) {
        console.error("Failed to fetch admin data", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const totalPlayers = leaderboard.length;
  const gatesBreached = stats.reduce((acc, curr) => acc + curr.completed, 0);
  const totalExecutions = submissions.length; // From the 100 recent limit, but good enough for demo

  if (loading) {
    return <div className="text-center text-metroid-rune mt-20">Loading Command Center...</div>;
  }

  const handleUnblock = async (username: string) => {
    try {
      await api.post(`/admin/unlock/${username}`, {});
      // Refresh data
      const lbData = await api.get('/admin/leaderboard');
      setLeaderboard(lbData);
    } catch (e) {
      console.error("Failed to unblock user", e);
    }
  };

  const formatSolveTime = (seconds: number): string => {
    if (seconds === 0) return '—';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  };

  const toggleMalpractice = async () => {
    try {
      const newVal = !malpracticeEnabled;
      await api.post('/admin/settings/malpractice', { enabled: newVal });
      setMalpracticeEnabled(newVal);
    } catch (e) {
      console.error("Failed to toggle malpractice setting", e);
    }
  };

  return (
    <div className="flex flex-col gap-8 min-h-[80vh] py-6 animate-[fadeIn_0.5s_ease-out]">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold font-rune rune-glow text-metroid-accent tracking-widest uppercase">Command Center</h2>
        <button 
          onClick={toggleMalpractice}
          className={`flex items-center gap-2 px-4 py-2 rounded-full font-bold uppercase tracking-widest text-sm transition-colors border ${
            malpracticeEnabled 
              ? 'bg-green-500/10 text-green-400 border-green-500/30 hover:bg-green-500/20' 
              : 'bg-red-500/10 text-red-400 border-red-500/30 hover:bg-red-500/20'
          }`}
        >
          Anti-Cheat: {malpracticeEnabled ? 'ON' : 'OFF'}
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Metric Cards */}
        <div className="stone-panel p-6 rounded-2xl flex items-center gap-6 border-t-4 border-t-blue-500 hover:border-t-blue-400 group">
          <div className="p-4 bg-blue-500/10 rounded-xl group-hover:bg-blue-500/20 transition-colors"><Users size={32} className="text-blue-500" /></div>
          <div>
            <div className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Active Players</div>
            <div className="text-4xl font-bold font-mono text-white/90">{totalPlayers}</div>
          </div>
        </div>
        
        <div className="stone-panel p-6 rounded-2xl flex items-center gap-6 border-t-4 border-t-metroid-rune hover:border-t-metroid-runeHover group">
          <div className="p-4 bg-metroid-rune/10 rounded-xl group-hover:bg-metroid-rune/20 transition-colors"><Target size={32} className="text-metroid-rune" /></div>
          <div>
            <div className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Gates Breached</div>
            <div className="text-4xl font-bold font-mono text-white/90">{gatesBreached}</div>
          </div>
        </div>

        <div className="stone-panel p-6 rounded-2xl flex items-center gap-6 border-t-4 border-t-purple-500 hover:border-t-purple-400 group">
          <div className="p-4 bg-purple-500/10 rounded-xl group-hover:bg-purple-500/20 transition-colors"><Activity size={32} className="text-purple-500" /></div>
          <div>
            <div className="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Total Executions</div>
            <div className="text-4xl font-bold font-mono text-white/90">{totalExecutions}</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Leaderboard */}
        <div className="stone-panel p-8 rounded-2xl">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-3 text-white/80"><Target size={24} className="text-metroid-rune drop-shadow-[0_0_10px_rgba(0,255,204,0.5)]"/> Top Scorers</h3>
          <table className="w-full text-left">
            <thead>
              <tr className="text-gray-400 border-b border-white/10 text-xs uppercase tracking-widest">
                <th className="pb-3 font-bold">Rank</th>
                <th className="pb-3 font-bold">Player</th>
                <th className="pb-3 font-bold">Email</th>
                <th className="pb-3 text-right font-bold">Score</th>
                <th className="pb-3 text-right font-bold">Solve Time</th>
                <th className="pb-3 text-right font-bold">Status / Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {leaderboard.slice(0, 10).map((user, idx) => (
                <tr key={idx} className="group hover:bg-white/5 transition-colors">
                  <td className="py-4 text-metroid-rune font-bold text-lg">#{user.rank}</td>
                  <td className="py-4 font-mono text-gray-200 group-hover:text-white transition-colors">{user.username}</td>
                  <td className="py-4 font-mono text-gray-400 text-sm truncate max-w-[200px]" title={user.email}>{user.email}</td>
                  <td className="py-4 text-right font-bold text-metroid-accent">{user.total_score} pts</td>
                  <td className="py-4 text-right font-mono text-gray-400 text-sm">{formatSolveTime(user.total_solve_time_seconds)}</td>
                  <td className="py-4 text-right text-sm">
                    {user.is_locked ? (
                      <div className="flex items-center justify-end gap-2">
                        <span className="text-red-500 font-bold bg-red-500/10 px-2 py-1 rounded">BLOCKED</span>
                        <button onClick={() => handleUnblock(user.username)} className="bg-metroid-accent/20 text-metroid-accent hover:bg-metroid-accent hover:text-black px-2 py-1 rounded transition-colors font-bold text-xs uppercase">
                          Unblock
                        </button>
                      </div>
                    ) : (
                      <span className="text-green-500 font-bold">ACTIVE</span>
                    )}
                  </td>
                </tr>
              ))}
              {leaderboard.length === 0 && (
                <tr><td colSpan={6} className="py-8 text-center text-gray-500 font-mono">No players yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Funnel */}
        <div className="stone-panel p-8 rounded-2xl">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-3 text-white/80"><Activity size={24} className="text-metroid-accent drop-shadow-[0_0_10px_rgba(255,0,85,0.5)]"/> Drop-off Funnel</h3>
          <div className="flex flex-col gap-6">
            {stats.sort((a, b) => a.gate_id - b.gate_id).map((step, idx) => (
              <div key={idx} className="group">
                <div className="flex justify-between text-sm mb-2">
                  <span className="font-bold text-gray-300">Gate {step.gate_id}</span>
                  <span className="font-mono text-gray-400 text-xs bg-black/40 px-2 py-1 rounded">{step.completed} passed / {step.unlocked} unlocked</span>
                </div>
                <div className="w-full bg-black/50 rounded-full h-3 border border-white/5 overflow-hidden">
                  <div 
                    className="bg-gradient-to-r from-metroid-accent to-purple-500 h-full rounded-full transition-all duration-1000 ease-out relative"
                    style={{ width: `${totalPlayers > 0 ? (step.completed / totalPlayers) * 100 : 0}%` }}
                  >
                    <div className="absolute inset-0 bg-white/20 w-full animate-[shimmer_2s_infinite]"></div>
                  </div>
                </div>
              </div>
            ))}
            {stats.length === 0 && (
              <div className="py-8 text-center text-gray-500 font-mono">No data available.</div>
            )}
          </div>
        </div>
      </div>
      
      {/* Submissions Feed */}
      <div className="stone-panel p-8 rounded-2xl">
        <h3 className="text-xl font-bold mb-6 text-white/80">Live Execution Feed</h3>
        <div className="flex flex-col gap-3 font-mono text-sm max-h-96 overflow-y-auto pr-2 custom-scrollbar">
          {submissions.map((sub, idx) => {
            const timeStr = new Date(sub.timestamp).toLocaleTimeString();
            return (
              <div key={idx} className="flex justify-between items-center p-4 bg-black/30 rounded-lg border border-white/5 hover:border-white/20 hover:bg-black/50 transition-colors">
                <span className="text-gray-500 text-xs w-24">{timeStr}</span>
                <span className="text-blue-400 w-1/4 truncate font-bold" title={sub.username}>{sub.username}</span>
                <span className="text-gray-300 w-1/4">Gate <span className="text-metroid-rune">{sub.gate_id}</span></span>
                <span className={`w-24 text-right font-bold px-3 py-1 rounded-full text-xs ${sub.passed ? 'bg-green-500/10 text-green-400 border border-green-500/30' : 'bg-red-500/10 text-red-400 border border-red-500/30'}`}>
                  {sub.passed ? 'PASSED' : 'FAILED'}
                </span>
              </div>
            )
          })}
          {submissions.length === 0 && (
            <div className="py-8 text-center text-gray-500">No recent submissions.</div>
          )}
        </div>
      </div>

    </div>
  );
}
