import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [question, setQuestion] = useState('Why does increasing temperature increase evaporation?');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function run() {
    setLoading(true); setError('');
    try {
      const response = await fetch(`${API}/api/v1/reason`, {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question, max_iterations: 8, candidate_count: 4})
      });
      if (!response.ok) throw new Error(await response.text());
      setResult(await response.json());
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }

  return <main>
    <header><span className="eyebrow">RETRIEVAL-AUGMENTED REASONING</span><h1>RARE Agent</h1><p>MCTS exploration + A6/A7 retrieval + RAFS-style factuality selection.</p></header>
    <section className="query">
      <textarea value={question} onChange={e => setQuestion(e.target.value)} rows="4" />
      <button disabled={loading} onClick={run}>{loading ? 'Reasoning…' : 'Run RARE'}</button>
      {error && <div className="error">{error}</div>}
    </section>
    {result && <>
      <section className="hero"><div><span className="badge">SELECTED {result.action}</span><h2>{result.answer}</h2></div><div className="score"><strong>{Math.round(result.factuality_score * 100)}%</strong><span>factuality</span></div></section>
      <section className="grid">
        <div className="card"><h3>Evidence</h3>{result.evidence.map(e => <article key={e.id}><b>{e.title}</b><small>{e.score}</small><p>{e.text}</p></article>)}</div>
        <div className="card"><h3>Statement checks</h3>{result.statement_checks.map((s, i) => <div className="check" key={i}><span className={s.supported ? 'ok' : 'bad'}>{s.supported ? 'SUPPORTED' : 'NOT SUPPORTED'}</span><p>{s.statement}</p></div>)}</div>
      </section>
      <section className="card"><h3>Candidate trajectories</h3><div className="candidates">{result.candidate_trajectories.map(c => <article key={c.id}><div><b>{c.action}</b><span>{Math.round(c.factuality_score * 100)}%</span></div><p>{c.summary}</p></article>)}</div></section>
    </>}
  </main>
}

createRoot(document.getElementById('root')).render(<App />);
