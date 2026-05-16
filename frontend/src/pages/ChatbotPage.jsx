import { useState, useRef, useEffect } from 'react';
import { apiPost } from '../api/client';

const SAMPLE_QUESTIONS = [
  'What is a balanced diet?',
  'How many calories to lose weight?',
  'Best high-protein foods?',
  'What is BMI and BMR?',
];

export default function ChatbotPage() {
  const [messages, setMessages] = useState([
    {
      id: 0,
      role: 'ai',
      text: 'Hi! I\'m EatRight AI, your personal nutrition assistant. Ask me anything about diet, calories, macros, or healthy eating.',
    },
  ]);
  const [input, setInput]     = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const addMsg = (role, text) =>
    setMessages(prev => [...prev, { id: Date.now() + Math.random(), role, text }]);

  const ask = async (overrideText) => {
    const text = (overrideText ?? input).trim();
    if (!text || loading) return;
    setInput('');
    addMsg('user', text);
    setLoading(true);

    // Build history for context (last 10 turns, excluding the welcome message)
    const history = messages
      .filter(m => m.id !== 0)
      .map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.text }));

    try {
      const res = await apiPost('/api/chatbot/', { question: text, history });
      addMsg('ai', res.ok ? res.answer : (res.message || 'Unable to get an answer.'));
    } catch {
      addMsg('ai', 'Network error. Make sure the Django server is running.');
    }
    setLoading(false);
  };

  const clearChat = () => {
    setMessages([{
      id: 0,
      role: 'ai',
      text: 'Chat cleared! Ask me anything about diet, calories, macros, or healthy eating.',
    }]);
  };

  return (
    <>
      <div className="page-banner">
        <h1>AI Nutrition Chatbot</h1>
        <p>Have a conversation with EatRight AI about diet, nutrition, and wellness.</p>
      </div>

      <div className="chat-page-wrap">
        {/* Sample pills */}
        <div className="chat-pills">
          <span style={{ fontSize: 13, color: '#999' }}>Quick questions:</span>
          {SAMPLE_QUESTIONS.map(q => (
            <button key={q} className="chat-pill" onClick={() => ask(q)} disabled={loading}>
              {q}
            </button>
          ))}
          {messages.length > 1 && (
            <button className="chat-pill" style={{ color: '#999', borderColor: '#ccc' }} onClick={clearChat}>
              Clear chat
            </button>
          )}
        </div>

        {/* Message thread */}
        <div className="chat-thread">
          {messages.map(msg => (
            <div key={msg.id} className={`chat-bubble-row ${msg.role}`}>
              {msg.role === 'ai' && (
                <div className="chat-avatar">🥗</div>
              )}
              <div className={`chat-bubble ${msg.role}`}>
                {msg.text.split('\n').map((line, i) => (
                  <span key={i}>{line}{i < msg.text.split('\n').length - 1 && <br />}</span>
                ))}
              </div>
              {msg.role === 'user' && (
                <div className="chat-avatar user-avatar">👤</div>
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble-row ai">
              <div className="chat-avatar">🥗</div>
              <div className="chat-bubble ai chat-typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div className="chat-input-bar">
          <textarea
            className="chat-input"
            rows="1"
            placeholder="Ask about your diet, nutrition, or health goals…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(); }
            }}
            disabled={loading}
          />
          <button
            className="btn-brand chat-send-btn"
            onClick={() => ask()}
            disabled={loading || !input.trim()}
          >
            {loading ? '…' : '➤'}
          </button>
        </div>
      </div>
    </>
  );
}
