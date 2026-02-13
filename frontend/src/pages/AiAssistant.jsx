import React, { useState, useRef, useEffect, useCallback } from 'react';
import { ragApi } from '../api/ragApi';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import '../styles/RagChat.css';

/* ── Inline SVG Icons ──────────────────────────────────────────────── */
const SendIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const ResetIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
  </svg>
);

/* ── Sub-components ────────────────────────────────────────────────── */

function SafetyBadge({ safety }) {
  if (!safety || safety.risk_level === 'low') return null;
  const level = safety.risk_level; // 'medium' | 'high'
  const icons = { medium: '⚠️', high: '🚨' };
  const labels = { medium: 'Moderate Risk', high: 'High Risk — Seek Help Immediately' };
  return (
    <div className={`safety-badge safety-${level}`}>
      <span>{icons[level]}</span>
      <span>{labels[level]}</span>
      {safety.policy_notes && <span className="safety-note"> — {safety.policy_notes}</span>}
    </div>
  );
}

function SourceCard({ source, index }) {
  const [expanded, setExpanded] = useState(false);
  const score = (source.relevance_score * 100).toFixed(0);
  const scoreLabel = score >= 85 ? 'High match' : score >= 70 ? 'Good match' : 'Partial match';
  const scoreColor = score >= 85 ? '#22c55e' : score >= 70 ? '#f59e0b' : '#1a3a52';

  return (
    <div className="source-card" onClick={() => setExpanded(!expanded)}>
      <div className="source-header">
        <span className="source-num">{index + 1}</span>
        <span className="source-title">{source.doc_title || 'Reference Document'}</span>
        {source.page != null && <span className="source-page">p.{source.page}</span>}
        <span className="source-score" style={{ color: scoreColor }}>{scoreLabel}</span>
      </div>
      {expanded && source.supporting_quote && (
        <div className="source-detail">
          <p className="source-quote">"{source.supporting_quote}"</p>
        </div>
      )}
    </div>
  );
}

function FollowUps({ questions, onSelect }) {
  if (!questions || questions.length === 0) return null;
  return (
    <div className="follow-ups">
      <span className="follow-label">Ask a follow-up:</span>
      <div className="follow-chips">
        {questions.map((q, i) => (
          <button key={i} className="follow-chip" onClick={() => onSelect(q)}>
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

function MessageBubble({ msg, onFollowUp }) {
  if (msg.role === 'user') {
    return (
      <div className="msg-row msg-user">
        <div className="msg-bubble user-bubble">
          <p>{msg.content}</p>
          <span className="msg-time">{msg.time}</span>
        </div>
        <div className="msg-avatar user-avatar">👤</div>
      </div>
    );
  }

  // Bot message
  const data = msg.data || {};
  return (
    <div className="msg-row msg-bot">
      <div className="msg-avatar bot-avatar">🧪</div>
      <div className="msg-bubble bot-bubble">
        <SafetyBadge safety={data.safety} />
        <div className="msg-answer" dangerouslySetInnerHTML={{ __html: formatAnswer(data.answer || msg.content) }} />

        {/* Confidence indicator */}
        {data.confidence && data.confidence.score > 0 && data.confidence.basis === 'retrieval' && (
          <div className="confidence-badge" style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '3px 10px', borderRadius: 12, fontSize: '0.75rem',
            marginTop: 6,
            background: data.confidence.score >= 0.85 ? '#dcfce7' :
                        data.confidence.score >= 0.70 ? '#fef9c3' : '#e8eef4',
            color: data.confidence.score >= 0.85 ? '#166534' :
                   data.confidence.score >= 0.70 ? '#854d0e' : '#1a3a52',
          }}>
            <span>{data.confidence.score >= 0.85 ? '🟢' : data.confidence.score >= 0.70 ? '🟡' : '🔵'}</span>
            <span>{data.confidence.label} — {(data.confidence.score * 100).toFixed(0)}% from {data.confidence.num_sources} source{data.confidence.num_sources !== 1 ? 's' : ''}</span>
          </div>
        )}

        {/* Why this answer — only show if meaningful */}
        {data.why_this_answer && data.why_this_answer.trim() !== '' && 
         !['Response generated from retrieved sources.', 'General informational query.', ''].includes(data.why_this_answer.trim()) && (
          <details className="why-section">
            <summary>💡 Why this answer?</summary>
            <p>{data.why_this_answer}</p>
          </details>
        )}

        {/* Sources — only show if there are real, meaningful sources */}
        {data.sources && data.sources.length > 0 && data.sources.some(s => s.relevance_score >= 0.65) && (
          <details className="sources-section">
            <summary>📚 Sources ({data.sources.filter(s => s.relevance_score >= 0.65).length})</summary>
            <div className="sources-list">
              {data.sources.filter(s => s.relevance_score >= 0.65).map((s, i) => (
                <SourceCard key={i} source={s} index={i} />
              ))}
            </div>
          </details>
        )}

        {/* Follow-up questions */}
        <FollowUps questions={data.follow_up_questions} onSelect={onFollowUp} />

        {/* Emergency escalation */}
        {data.safety?.emergency_escalation && (
          <div className="safety-badge safety-high" style={{ marginTop: 12 }}>
            🚨 {data.safety.emergency_escalation.slice(0, 200)}
          </div>
        )}

        <span className="msg-time">{msg.time}</span>
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="msg-row msg-bot">
      <div className="msg-avatar bot-avatar">🧪</div>
      <div className="msg-bubble bot-bubble typing-bubble">
        <div className="typing-dots">
          <span /><span /><span />
        </div>
        <span className="typing-text">Searching knowledge base…</span>
      </div>
    </div>
  );
}

/* ── Helpers ────────────────────────────────────────────────────────── */

function formatAnswer(text) {
  if (!text) return '';
  let html = text;
  
  // Remove useless inline citations like [Source: None, ...] or [Source: Unknown]
  html = html.replace(/\[Source:\s*None[^\]]*\]/gi, '');
  html = html.replace(/\[Source:\s*Unknown[^\]]*\]/gi, '');
  html = html.replace(/📄\s*None[^<\n]*/gi, '');
  
  // Convert [Source: title, page: X, chunk_id: ...] to a subtle inline cite
  html = html.replace(
    /\[Source:\s*([^,\]]+?)(?:,\s*page:?\s*(\d+))?(?:,\s*chunk_id[^\]]*?)?\s*\]/gi,
    (match, title, page) => {
      const cleanTitle = title.trim();
      if (page) return `<cite class="inline-cite" title="${cleanTitle}">${cleanTitle}, p.${page}</cite>`;
      return `<cite class="inline-cite" title="${cleanTitle}">${cleanTitle}</cite>`;
    }
  );
  
  // Newlines to <br/>
  html = html.replace(/\n/g, '<br/>');
  // Bold **text**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Bullet lists: lines starting with - or •
  html = html.replace(/((?:^|\<br\/\>)\s*[-•]\s.+(?:\<br\/\>\s*[-•]\s.+)*)/g, (match) => {
    const items = match.split(/<br\/?>/g).filter(l => l.trim().match(/^[-•]/));
    if (items.length === 0) return match;
    const lis = items.map(i => `<li>${i.replace(/^\s*[-•]\s*/, '')}</li>`).join('');
    return `<ul>${lis}</ul>`;
  });
  return html;
}

function timeNow() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/* ── Welcome message ───────────────────────────────────────────────── */

const WELCOME = {
  role: 'bot',
  content: "Welcome to **PoisonSense AI** 🧪\n\nI'm your safety-first poison information assistant. I provide evidence-based answers with full citations from verified toxicology sources.\n\n**I can help with:**\n- Identifying poison symptoms & first-aid steps\n- Safe storage & prevention guidance\n- 💊 Antidote information & availability\n- 🏥 Finding nearby hospitals & emergency rooms\n- ☎️ Poison control center contacts\n- Emergency contacts & escalation\n\n⚠️ **I am NOT a substitute for professional medical advice.** In an emergency, call your local poison control center or emergency services immediately.",
  data: {
    answer: "Welcome to **PoisonSense AI** 🧪\n\nI'm your safety-first poison information assistant. I provide evidence-based answers with full citations from verified toxicology sources.\n\n**I can help with:**\n- Identifying poison symptoms & first-aid steps\n- Safe storage & prevention guidance\n- 💊 Antidote information & availability\n- 🏥 Finding nearby hospitals & emergency rooms\n- ☎️ Poison control center contacts\n- Emergency contacts & escalation\n\n⚠️ **I am NOT a substitute for professional medical advice.** In an emergency, call your local poison control center or emergency services immediately.",
    follow_up_questions: [
      "What are common household poisons?",
      "What is the antidote for paracetamol overdose?",
      "Find hospitals near me",
    ],
    sources: [],
    safety: { risk_level: 'low' },
  },
  time: timeNow(),
};

/* ═══════════════════════════════════════════════════════════════════════
   Main Component
   ═══════════════════════════════════════════════════════════════════════ */

export default function AiAssistant() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState(null); // { collections, total_documents }
  const [userLocation, setUserLocation] = useState(null); // { latitude, longitude }
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom — scroll only within the messages container,
  // not the entire page (which caused the page to jump to the bottom)
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
    }
  }, [messages, loading]);

  // Fetch status on mount + get user location
  useEffect(() => {
    // Scroll page to top on mount so the chat is visible from the start
    window.scrollTo(0, 0);

    ragApi.getStatus()
      .then(setStatus)
      .catch(() => setStatus(null));
    
    // Try to get user's location for hospital/center lookups
    const stored = localStorage.getItem('userLocation');
    if (stored) {
      try {
        setUserLocation(JSON.parse(stored));
      } catch {}
    }
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const loc = { latitude: pos.coords.latitude, longitude: pos.coords.longitude };
          setUserLocation(loc);
          localStorage.setItem('userLocation', JSON.stringify(loc));
        },
        () => {}, // silently ignore denial
        { enableHighAccuracy: false, timeout: 5000 }
      );
    }
  }, []);

  // ── Send message ────────────────────────────────────────────────
  const sendMessage = useCallback(async (text) => {
    const trimmed = (text || input).trim();
    if (!trimmed || loading) return;

    // Add user message
    const userMsg = { role: 'user', content: trimmed, time: timeNow() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const data = await ragApi.ask(
        trimmed,
        sessionId,
        userLocation?.latitude || null,
        userLocation?.longitude || null,
      );

      // Capture session id for continuity
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const botMsg = {
        role: 'bot',
        content: data.answer,
        data,
        time: timeNow(),
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error('RAG ask error:', err);
      const errorMsg = {
        role: 'bot',
        content: 'Sorry, something went wrong. Please try again.',
        data: {
          answer: '⚠️ Unable to reach the knowledge base. Make sure the backend is running and PDFs have been ingested.',
          why_this_answer: `Error: ${err?.response?.data?.detail || err.message}`,
          sources: [],
          follow_up_questions: [],
          safety: { risk_level: 'low' },
        },
        time: timeNow(),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading, sessionId, userLocation]);

  // ── Follow-up click ─────────────────────────────────────────────
  const handleFollowUp = useCallback((question) => {
    setInput(question);
    // Small delay to let state update, then send
    setTimeout(() => sendMessage(question), 50);
  }, [sendMessage]);

  // ── Reset chat ──────────────────────────────────────────────────
  const handleReset = async () => {
    if (sessionId) {
      try { await ragApi.resetSession(sessionId); } catch {}
    }
    setMessages([{ ...WELCOME, time: timeNow() }]);
    setSessionId(null);
    setInput('');
  };

  // ── Keyboard handler ───────────────────────────────────────────
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // ── Status helpers ──────────────────────────────────────────────
  const isOnline = status && status.has_data;
  const statusLabel = isOnline ? 'Online' : 'Offline';

  return (
    <>
      <Navbar />
      <div className="rag-page">
        <div className="rag-container">
          {/* ── Header ──────────────────────────────────────────── */}
          <div className="rag-header">
            <div className="rag-header-left">
              <div className="rag-logo">🧪</div>
              <div>
                <h1>PoisonSense AI</h1>
                <p className="rag-subtitle">Citation-backed toxicology assistant</p>
              </div>
            </div>
            <div className="rag-header-right">
              <span className={`status-dot ${isOnline ? 'online' : 'empty'}`}>
                {isOnline ? '●' : '○'} {statusLabel}
              </span>
              <button className="btn-reset" onClick={handleReset} title="Reset conversation">
                <ResetIcon />
              </button>
            </div>
          </div>

          {/* ── Messages ────────────────────────────────────────── */}
          <div className="rag-messages" ref={messagesContainerRef}>
            {messages.map((msg, i) => (
              <MessageBubble key={i} msg={msg} onFollowUp={handleFollowUp} />
            ))}
            {loading && <TypingIndicator />}
          </div>

          {/* ── Input ───────────────────────────────────────────── */}
          <div className="rag-input-area">
            <div className="rag-input-wrap">
              <textarea
                ref={inputRef}
                className="rag-input"
                placeholder="Ask about poisons, symptoms, first aid, prevention…"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                disabled={loading}
              />
              <button
                className="rag-send"
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                title="Send message"
              >
                <SendIcon />
              </button>
            </div>
            <p className="rag-disclaimer">
              <strong>⚠️ Not medical advice.</strong> Always consult a healthcare professional in emergencies.
            </p>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
}
