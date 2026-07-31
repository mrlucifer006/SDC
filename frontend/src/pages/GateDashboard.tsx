import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Unlock, Trophy, ChevronDown, ChevronUp } from 'lucide-react';
import { api } from '../services/api';

interface Gate {
  id: number;
  name: string;
  desc: string;
  points_awarded: number;
  unlocked: boolean;
  completed: boolean;
}

interface LeaderboardEntry {
  username: string;
  total_score: number;
  total_solve_time_seconds: number;
  rank: number;
}

export default function GateDashboard() {
  const navigate = useNavigate();
  const [gates, setGates] = useState<Gate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [lbLoading, setLbLoading] = useState(true);
  const [showLeaderboard, setShowLeaderboard] = useState(true);

  useEffect(() => {
    const fetchGates = async () => {
      try {
        const data = await api.get('/game/gates');
        setGates(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch gates');
      } finally {
        setLoading(false);
      }
    };
    fetchGates();
  }, []);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const data = await api.get('/game/leaderboard');
        setLeaderboard(data);
      } catch (err) {
        console.error('Failed to fetch leaderboard', err);
      } finally {
        setLbLoading(false);
      }
    };
    fetchLeaderboard();
    const interval = setInterval(fetchLeaderboard, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="text-center text-metroid-rune mt-20">Loading gates...</div>;
  if (error) return <div className="text-center text-red-500 mt-20">{error}</div>;

  const formatSolveTime = (seconds: number): string => {
    if (seconds === 0) return '—';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}h ${m}m`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
  };

  return (
    <div className="flex flex-col items-center min-h-[80vh] py-10 relative">
      {/* Leaderboard Panel */}
      <div className="w-full max-w-3xl mb-10 animate-[fadeIn_0.5s_ease-out]">
        <button
          onClick={() => setShowLeaderboard(!showLeaderboard)}
          className="w-full flex items-center justify-between px-6 py-4 stone-panel rounded-2xl border border-white/5 hover:border-metroid-rune/30 transition-all group"
        >
          <div className="flex items-center gap-3">
            <Trophy size={22} className="text-yellow-500 drop-shadow-[0_0_8px_rgba(234,179,8,0.4)]" />
            <span className="text-lg font-bold text-white/80 tracking-wide uppercase">Leaderboard</span>
            <span className="text-xs font-mono text-gray-500 bg-black/30 px-2 py-0.5 rounded-full">{leaderboard.length} players</span>
          </div>
          {showLeaderboard ? (
            <ChevronUp size={20} className="text-gray-500 group-hover:text-metroid-rune transition-colors" />
          ) : (
            <ChevronDown size={20} className="text-gray-500 group-hover:text-metroid-rune transition-colors" />
          )}
        </button>

        {showLeaderboard && (
          <div className="stone-panel rounded-b-2xl border-t-0 px-6 pb-6 pt-2 animate-[fadeIn_0.3s_ease-out] -mt-4 rounded-t-none border border-white/5 border-t-white/[0.02]">
            {lbLoading ? (
              <div className="text-center text-gray-500 py-6 font-mono text-sm">Loading rankings...</div>
            ) : leaderboard.length === 0 ? (
              <div className="text-center text-gray-500 py-6 font-mono text-sm">No players ranked yet.</div>
            ) : (
              <table className="w-full text-left mt-2">
                <thead>
                  <tr className="text-gray-500 border-b border-white/5 text-xs uppercase tracking-widest">
                    <th className="pb-2 font-bold w-16">Rank</th>
                    <th className="pb-2 font-bold">Player</th>
                    <th className="pb-2 text-right font-bold">Score</th>
                    <th className="pb-2 text-right font-bold">Solve Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/[0.03]">
                  {leaderboard.slice(0, 10).map((entry) => (
                    <tr key={entry.rank} className="group hover:bg-white/[0.03] transition-colors">
                      <td className="py-3 font-bold text-lg">
                        {entry.rank === 1 ? (
                          <span className="text-yellow-500 drop-shadow-[0_0_6px_rgba(234,179,8,0.4)]">🥇</span>
                        ) : entry.rank === 2 ? (
                          <span className="text-gray-300">🥈</span>
                        ) : entry.rank === 3 ? (
                          <span className="text-amber-600">🥉</span>
                        ) : (
                          <span className="text-gray-500 font-mono text-sm">#{entry.rank}</span>
                        )}
                      </td>
                      <td className="py-3 font-mono text-gray-200 group-hover:text-white transition-colors">{entry.username}</td>
                      <td className="py-3 text-right font-bold text-metroid-accent">{entry.total_score} <span className="text-xs text-gray-500">pts</span></td>
                      <td className="py-3 text-right font-mono text-gray-500 text-sm">{formatSolveTime(entry.total_solve_time_seconds)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>

      <h2 className="text-3xl font-bold font-rune mb-12 text-transparent bg-clip-text bg-gradient-to-r from-gray-200 to-gray-500 tracking-[0.2em] uppercase">Select Your Target</h2>
      <div className="flex flex-col gap-6 w-full max-w-3xl">
        {gates.map((gate, idx) => (
          <div 
            key={gate.id} 
            className={`stone-panel p-8 rounded-2xl flex items-center justify-between transition-all duration-500 group animate-[fadeIn_0.5s_ease-out_both] ${gate.unlocked ? 'cursor-pointer hover:border-metroid-rune/50 hover:shadow-[0_0_30px_rgba(0,255,204,0.15)] transform hover:-translate-y-2' : 'opacity-60 cursor-not-allowed grayscale-[50%]'}`}
            style={{ animationDelay: `${idx * 150}ms` }}
            onClick={() => gate.unlocked && navigate(`/challenge/${gate.id}`)}
          >
            <div className="flex items-center gap-8">
              <div className="text-6xl font-rune font-bold text-white/5 group-hover:text-white/10 transition-colors">0{gate.id}</div>
              <div>
                <h3 className={`text-2xl font-bold mb-1 ${gate.unlocked ? 'text-metroid-rune rune-glow group-hover:scale-[1.02] transition-transform origin-left' : 'text-gray-500'}`}>
                  {gate.name}
                </h3>
                <p className="text-gray-400 group-hover:text-gray-300 transition-colors">{gate.desc}</p>
                <div className="mt-3 inline-block px-3 py-1 bg-metroid-accent/10 border border-metroid-accent/30 text-metroid-accent rounded-full text-xs font-bold tracking-wider">
                  {gate.points_awarded} PTS
                </div>
              </div>
            </div>
            <div className="relative">
              {gate.unlocked ? (
                <>
                  <Unlock size={32} className={`transition-all duration-500 ${gate.completed ? 'text-green-400 drop-shadow-[0_0_10px_rgba(74,222,128,0.5)]' : 'text-metroid-rune group-hover:scale-125'}`} />
                  {gate.completed && <div className="absolute inset-0 bg-green-400/20 blur-xl rounded-full"></div>}
                </>
              ) : (
                <Lock size={32} className="text-gray-600" />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
