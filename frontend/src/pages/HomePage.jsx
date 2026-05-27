import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Activity, ArrowRight, Bot, Globe, Link2, Salad } from 'lucide-react';
import GlassCard from '../components/GlassCard';
import { StarsBackground } from '@/components/animate-ui/components/backgrounds/stars';

const offerItems = [
  {
    title: 'Diet Planner',
    desc: 'Get personalised breakfast, lunch and dinner recommendations powered by ML.',
    icon: Salad,
    tone: 'rgba(34,197,94,0.2)',
    badge: 'ML Powered',
    cta: 'Get Started',
    to: '/dietplanner',
  },
  {
    title: 'Body Fat Calculator',
    desc: 'Calculate your body fat in seconds using your weight, height, age and gender.',
    icon: Activity,
    tone: 'rgba(56,189,248,0.22)',
    badge: 'Instant',
    cta: 'Calculate',
    to: '/bodymass',
  },
  {
    title: 'AI Chatbot',
    desc: 'Ask diet and nutrition questions and get immediate answers from your AI coach.',
    icon: Bot,
    tone: 'rgba(167,139,250,0.22)',
    badge: 'GPT-4',
    cta: 'Ask Now',
    to: '/chatbot',
  },
];

const developers = [
  { name: 'Rajdeep Avhad', initials: 'RA', tint: '#22c55e' },
  { name: 'Prajwal Jadhav', initials: 'PJ', tint: '#60a5fa' },
  { name: 'Hrishikesh Patil', initials: 'HP', tint: '#f59e0b' },
  { name: 'Bhumika Sinha', initials: 'BS', tint: '#a78bfa' },
];

export default function HomePage() {
  const words = ['Welcome', 'to', 'EatRight'];

  return (
    <motion.main className="page-motion" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Stars fill the entire hero */}
        <StarsBackground
          starColor="#ffffff"
          className="absolute inset-0"
          style={{ background: 'radial-gradient(ellipse at 60% 80%, #0d2010 0%, #060d06 50%, #000 100%)' }}
        />

        {/* Optional: green glow at bottom */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_100%,rgba(34,197,94,0.08)_0%,transparent_70%)] pointer-events-none" />

        {/* Hero content */}
        <div className="relative z-10 text-center">
          <motion.div className="home-hero__badge" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            🌱 AI-Powered Nutrition Platform
          </motion.div>

          <h1 className="home-hero__title">
            {words.map((word, idx) => (
              <motion.span
                key={word}
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.12 }}
                style={{ display: 'inline-block', marginRight: 10 }}
              >
                {word}
              </motion.span>
            ))}
          </h1>

          <p className="home-hero__description">
            Your personalised AI-powered food recommendation system. Get a custom diet plan based on your body metrics and goals.
            <span className="typing-caret" />
          </p>

          <motion.div whileTap={{ scale: 0.97 }} style={{ display: 'inline-block' }}>
            <Link to="/dietplanner" className="btn-green pulse-glow" style={{ display: 'inline-flex', alignItems: 'center', textDecoration: 'none' }}>
              Plan My Diet
            </Link>
          </motion.div>

          <div className="hero-trust-badges">
            <span>🔒 Secure</span>
            <span>⚡ Instant Results</span>
            <span>🤖 AI Powered</span>
          </div>
        </div>
      </section>

      <section className="container py-5" style={{ padding: '48px 20px' }}>
        <h2 className="text-center mb-4" style={{ color: '#86efac', fontSize: '2.5rem', fontWeight: 700 }}>What We Offer</h2>
        <p style={{ textAlign: 'center', color: '#aaa', marginBottom: 40, fontSize: '1.1rem' }}>Everything you need for a healthier lifestyle</p>
        <div className="offer-grid">
          {offerItems.map((item, idx) => {
            const Icon = item.icon;
            return (
              <GlassCard key={item.title} className="offer-card p-4" delay={idx * 0.1}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 16 }}>
                  <div className="offer-icon-wrap" style={{ background: item.tone }}>
                    <Icon size={24} color="#dcfce7" />
                  </div>
                  <span style={{ borderRadius: 999, border: '1px solid rgba(255,255,255,0.14)', padding: '5px 10px', fontSize: 12 }}>
                    {item.badge}
                  </span>
                </div>
                <h5 style={{ color: '#f8fafc', fontSize: '1.35rem', marginBottom: 10 }}>{item.title}</h5>
                <p style={{ fontSize: 14, color: '#9ca3af', marginBottom: 14 }}>{item.desc}</p>
                <Link to={item.to} className="offer-link">
                  {item.cta} <ArrowRight size={16} />
                </Link>
              </GlassCard>
            );
          })}
        </div>
      </section>

      <section style={{ background: 'rgba(42,42,42,0.6)', padding: '48px 0', borderTop: '1px solid #444' }}>
        <div className="container">
          <h2 style={{ color: '#86efac', marginBottom: 12, textAlign: 'center' }}>Developers</h2>
          <div className="dev-grid">
            {developers.map((dev, idx) => (
              <GlassCard key={dev.name} className="p-3" delay={idx * 0.1}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div className="dev-avatar" style={{ background: dev.tint }}>{dev.initials}</div>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <a href="#" className="footer-icon" aria-label="Profile link"><Link2 size={16} /></a>
                    <a href="#" className="footer-icon" aria-label="Portfolio"><Globe size={16} /></a>
                  </div>
                </div>
                <h6 style={{ margin: 0 }}>{dev.name}</h6>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>
    </motion.main>
  );
}
