import { useState, useRef, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bot, Send } from 'lucide-react';
import { apiPost } from '../api/client';
import GlassCard from '../components/GlassCard';

const SAMPLE_QUESTIONS = [
  '🥗 Balanced diet basics',
  '🔥 Daily calories for weight loss',
  '💪 Best high-protein foods',
  '📊 What is BMI and BMR?',
  '🍳 Healthy cooking methods',
  '🌶️ Best Indian spices for health',
];

const formatTime = (timestamp) => new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

export default function ChatbotPage() {
  const [messages, setMessages] = useState([
    {
      id: 0,
      role: 'ai',
      text: 'Hi! I\'m EatRight AI, your personalized nutrition assistant. I can help you with diet planning, calorie targets, macronutrient breakdown, cooking tips, and practical strategies for your health goals. Ask me anything about food, nutrition, weight loss, muscle gain, or healthy Indian cuisine! 🥗',
      at: Date.now(),
    },
  ]);
  const [input, setInput]     = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const addMsg = (role, text) =>
    setMessages(prev => [...prev, { id: Date.now() + Math.random(), role, text, at: Date.now() }]);

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
      text: 'Chat cleared! Ask me anything about diet planning, cooking methods, macronutrients, Indian cuisine, meal prep strategies, or your personalized nutrition goals.',
      at: Date.now(),
    }]);
  };

  return (
    <motion.main className="page-motion">
      <section className="form-shell" style={{ marginTop: 14 }}>
        <GlassCard className="p-3 mb-3" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
              AI Nutrition Chatbot <span className="online-dot" />
            </h1>
            <p style={{ color: '#9ca3af', margin: '6px 0 0' }}>Have a conversation with EatRight AI about diet, nutrition, and wellness.</p>
          </div>
        </GlassCard>

        <div className="chat-shell" style={{ padding: 0 }}>
          <div className="chat-pills" style={{ marginBottom: 10 }}>
            {SAMPLE_QUESTIONS.map(q => (
              <button key={q} className="chat-pill" onClick={() => ask(q)} disabled={loading} style={{ padding: '10px 14px', fontWeight: 600 }}>
                {q}
              </button>
            ))}
            {messages.length > 1 && (
              <button className="chat-pill" style={{ color: '#999', borderColor: '#ccc' }} onClick={clearChat}>
                Clear chat
              </button>
            )}
          </div>

          <div className="chat-thread">
            <AnimatePresence initial={false}>
              {messages.map(msg => (
                <motion.div
                  key={msg.id}
                  className={`chat-bubble-row ${msg.role}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  {msg.role === 'ai' && (
                    <div className="chat-avatar"><Bot size={16} /></div>
                  )}
                  <div>
                    <div className={`chat-bubble ${msg.role}`}>
                      {msg.text.split('\n').map((line, i) => (
                        <span key={i}>{line}{i < msg.text.split('\n').length - 1 && <br />}</span>
                      ))}
                    </div>
                    <div className="chat-time">{formatTime(msg.at)}</div>
                  </div>
                  {msg.role === 'user' && (
                    <div className="chat-avatar user-avatar">👤</div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {loading && (
              <div className="chat-bubble-row ai">
                <div className="chat-avatar"><Bot size={16} /></div>
                <div>
                  <div className="chat-bubble ai chat-typing"><span></span><span></span><span></span></div>
                  <div className="chat-time">typing...</div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="chat-input-pill" style={{ marginTop: 10 }}>
            <textarea
              rows="1"
              placeholder="Ask about diet plans, calories, macros, cooking tips, meal prep, Indian foods, or your health goals..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(); }
              }}
              disabled={loading}
            />
            <motion.button whileTap={{ scale: 0.97 }} className="send-round" onClick={() => ask()} disabled={loading || !input.trim()}>
              <Send size={18} />
            </motion.button>
          </div>
        </div>
      </section>
    </motion.main>
  );
}
