import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { ArrowLeft, Play } from 'lucide-react';
import { api, removeAuthToken } from '../services/api';

interface GateDetail {
  id: number;
  name: string;
  desc: string;
  points_awarded: number;
  problem_statement: string;
  sample_input: string;
  sample_output: string;
}

export default function ChallengeView() {
  const { gateId } = useParams();
  const navigate = useNavigate();
  const templates: Record<string, string> = {
    python: 'def solve():\n    # Your logic here\n    pass\n\nsolve()',
    javascript: 'function solve() {\n    // Your logic here\n}\n\nsolve();',
    cpp: '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Your logic here\n    return 0;\n}',
    c: '#include <stdio.h>\n\nint main() {\n    // Your logic here\n    return 0;\n}',
    java: 'class Main {\n    public static void main(String[] args) {\n        // Your logic here\n    }\n}'
  };

  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState(templates['python']);
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [gate, setGate] = useState<GateDetail | null>(null);
  const [fetchError, setFetchError] = useState('');
  const [malpracticeEnabled, setMalpracticeEnabled] = useState(true);

  // Update code template when language changes, only if the user hasn't modified it heavily
  // (For simplicity, we always reset the template on language change in this basic version)
  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    setCode(templates[newLang]);
  };

  useEffect(() => {
    const fetchGate = async () => {
      try {
        const data = await api.get(`/game/gates/${gateId}`);
        setGate(data);
      } catch (err: any) {
        setFetchError(err.message || 'Failed to load gate');
      }
    };
    const fetchSettings = async () => {
      try {
        const data = await api.get('/game/settings');
        setMalpracticeEnabled(data.malpractice_enabled);
      } catch (err) {
        console.error("Failed to fetch settings", err);
      }
    };
    if (gateId) fetchGate();
    fetchSettings();
  }, [gateId]);

  useEffect(() => {
    if (!malpracticeEnabled) return;
    
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'hidden') {
        try {
          await api.post('/auth/malpractice', {});
        } catch (e) {
          // Ignore error if already logged out or locked
        }
        removeAuthToken();
        alert('Malpractice detected: Tab switch or window minimized. You have been locked out.');
        navigate('/login');
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [navigate, malpracticeEnabled]);

  const handleRunCode = async () => {
    setLoading(true);
    setOutput('Connecting to Sandbox...\nCompiling code...');
    
    try {
      const res = await api.post('/game/submit', {
        gate_id: Number(gateId),
        source_code: code,
        language: language
      });
      
      let out = '';
      if (res.compile_output) {
        out += `Compile Output:\n${res.compile_output}\n\n`;
      }
      
      if (res.earned_score !== undefined) {
        out += `Points Awarded: ${res.earned_score} / ${gate?.points_awarded} (${res.passed_cases}/${res.total_cases} tests passed)\n\n`;
      }

      if (res.passed) {
        out += `[+] ALL TESTS PASSED!\n`;
        out += `Execution Time: ${res.time_ms} ms\n`;
        out += `Output:\n${res.stdout}\n`;
      } else {
        out += `[-] SOME TESTS FAILED.\n`;
        out += `Sample Test Passed: ${res.sample_passed}\n`;
        if (res.stdout) out += `Sample Output:\n${res.stdout}\n`;
        if (res.stderr) out += `Error:\n${res.stderr}\n`;
      }
      out += `Status: ${res.passed ? 'ACCEPTED 🟢' : 'FAILED 🔴'}\n`;
      out += `Execution Time: ${res.time_ms || 0}ms`;
      
      setOutput(out);
    } catch (err: any) {
      setOutput(`Error: ${err.message || 'Submission failed'}`);
    } finally {
      setLoading(false);
    }
  };

  if (fetchError) {
    return (
      <div className="flex flex-col items-center justify-center h-[80vh]">
        <div className="text-red-500 mb-4">{fetchError}</div>
        <button onClick={() => navigate('/')} className="btn-rune">Back to Gates</button>
      </div>
    );
  }

  if (!gate) {
    return <div className="text-center text-metroid-rune mt-20">Loading terminal...</div>;
  }

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] animate-[fadeIn_0.5s_ease-out]">
      <div className="mb-6 flex items-center">
        <button onClick={() => navigate('/')} className="text-gray-400 hover:text-white flex items-center gap-2 transition-colors font-bold uppercase tracking-widest text-sm bg-black/20 px-4 py-2 rounded-full border border-white/5 hover:border-white/20">
          <ArrowLeft size={16} /> Back to Gates
        </button>
      </div>

      <div className="flex gap-6 h-full min-h-0">
        {/* Lore / Instructions Pane */}
        <div className="stone-panel p-8 rounded-2xl w-1/3 flex flex-col gap-6 overflow-y-auto custom-scrollbar">
          <h2 className="text-3xl font-bold font-rune rune-glow text-metroid-rune tracking-widest uppercase">{gate.name}</h2>
          
          <div className="prose prose-invert">
            <div className="bg-white/5 p-4 rounded-xl border border-white/10 mb-6">
              <p className="text-gray-300 italic font-serif text-lg leading-relaxed">
                "The ancient mechanism hums with power. Only the one who speaks the true rotation can pass."
              </p>
            </div>
            
            <h3 className="text-xl font-bold mt-4 text-white/90 flex items-center gap-2">
              <span className="w-8 h-px bg-metroid-rune"></span> Problem Statement
            </h3>
            <p className="text-gray-400 mt-3 leading-relaxed whitespace-pre-wrap">{gate.problem_statement}</p>
            
            <div className="mt-6 flex flex-col gap-4">
              <div className="bg-black/40 border border-white/5 rounded-lg p-4">
                <h4 className="text-metroid-accent font-bold text-sm tracking-widest uppercase mb-2">Sample Input</h4>
                <pre className="font-mono text-gray-300 text-sm whitespace-pre-wrap">{gate.sample_input}</pre>
              </div>
              <div className="bg-black/40 border border-white/5 rounded-lg p-4">
                <h4 className="text-metroid-accent font-bold text-sm tracking-widest uppercase mb-2">Sample Output</h4>
                <pre className="font-mono text-gray-300 text-sm whitespace-pre-wrap">{gate.sample_output}</pre>
              </div>
            </div>
            
            <div className="mt-8 p-4 bg-metroid-accent/10 border border-metroid-accent/20 rounded-xl inline-block">
              <p className="text-metroid-accent font-bold text-sm tracking-widest uppercase">Reward</p>
              <p className="text-3xl font-mono font-bold text-white mt-1">{gate.points_awarded} <span className="text-lg text-gray-500">PTS</span></p>
            </div>
          </div>
        </div>

        {/* Editor Pane */}
        <div className="stone-panel rounded-2xl w-2/3 flex flex-col overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.8)]">
          <div className="bg-black/60 px-6 py-3 flex justify-between items-center border-b border-white/10 backdrop-blur-md">
            <div className="flex items-center gap-4">
              <div className="flex gap-2 mr-2">
                <div className="w-3 h-3 rounded-full bg-red-500/50"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/50"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/50"></div>
              </div>
              <select 
                value={language} 
                onChange={handleLanguageChange}
                className="bg-black/40 border border-white/10 text-metroid-rune font-mono text-sm px-3 py-1.5 rounded-md focus:outline-none focus:border-metroid-rune transition-colors cursor-pointer"
              >
                <option value="python">Python 3</option>
                <option value="javascript">JavaScript (Node)</option>
                <option value="cpp">C++ (g++)</option>
                <option value="c">C (gcc)</option>
                <option value="java">Java</option>
              </select>
            </div>
            <button 
              onClick={handleRunCode}
              disabled={loading}
              className="btn-rune !py-2 !px-4 flex items-center gap-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              <Play size={16} className={loading ? "animate-pulse" : ""} /> {loading ? 'Evaluating...' : 'Run Sequence'}
            </button>
          </div>
          
          <div className="flex-1 bg-[#1e1e1e]"
               onCopyCapture={(e) => { if (malpracticeEnabled) { e.preventDefault(); e.stopPropagation(); } }}
               onPasteCapture={(e) => { if (malpracticeEnabled) { e.preventDefault(); e.stopPropagation(); } }}
               onCutCapture={(e) => { if (malpracticeEnabled) { e.preventDefault(); e.stopPropagation(); } }}
               onKeyDownCapture={(e) => {
                 if (malpracticeEnabled && (e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'v' || e.key === 'x' || e.key === 'C' || e.key === 'V' || e.key === 'X')) {
                   e.preventDefault();
                   e.stopPropagation();
                 }
               }}>
            <Editor
              height="100%"
              language={language}
              theme="vs-dark"
              value={code}
              onChange={(val) => setCode(val || '')}
              options={{
                minimap: { enabled: false },
                fontSize: 15,
                fontFamily: "'Fira Code', 'Courier New', monospace",
                padding: { top: 20 },
                scrollBeyondLastLine: false,
                lineHeight: 1.6,
                contextmenu: false
              }}
            />
          </div>

          {/* Console Output */}
          <div className="h-56 bg-black/90 border-t border-white/10 p-6 overflow-y-auto custom-scrollbar relative">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-metroid-rune/30 to-transparent"></div>
            <h4 className="text-gray-500 font-mono text-xs uppercase mb-3 tracking-widest font-bold flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-metroid-rune animate-pulse"></div>
              Terminal Output
            </h4>
            <pre className="font-mono text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">{output || "Awaiting execution..."}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
