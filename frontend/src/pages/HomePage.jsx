import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <>
      {/* Hero Banner with Fresh Vegetables Background */}
      <div style={{
        minHeight: 500,
        background: 'linear-gradient(135deg, rgba(26,26,26,0.4) 0%, rgba(44,44,44,0.3) 100%), url(/static/images/fresh-veggies-bg.jpg) center/cover',
        backgroundAttachment: 'fixed',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#fff',
        textAlign: 'center',
        padding: '80px 30px',
        borderBottom: '3px solid #2ECC71'
      }}>
        <img src="/static/images/Gemini_Generated_Image_f0bd5kf0bd5kf0bd.png" alt="EatRight" height="110" style={{ marginBottom: 24, filter: 'brightness(1.3) drop-shadow(0 6px 12px rgba(0,0,0,0.7))' }} />
        <h1 style={{ fontSize: '3.5rem', marginBottom: 16, fontWeight: 800, textShadow: '3px 3px 6px rgba(0,0,0,0.9)', animation: 'slideDown 0.6s ease-out' }}>Welcome to EatRight</h1>
        <p style={{ fontSize: '1.3rem', maxWidth: 650, marginBottom: 32, opacity: 1, textShadow: '2px 2px 4px rgba(0,0,0,0.9)', animation: 'slideUp 0.6s ease-out 0.1s backwards' }}>
          Your personalised AI-powered food recommendation system. Get a custom diet plan based on your body metrics and goals.
        </p>
        <Link to="/dietplanner" className="btn-brand" style={{ fontSize: 18, padding: '18px 48px', boxShadow: '0 6px 16px rgba(46, 204, 113, 0.5)', animation: 'slideUp 0.6s ease-out 0.2s backwards' }}>
          Plan My Diet
        </Link>
      </div>

      {/* Feature Cards */}
      <section className="container py-5" style={{ backgroundColor: '#1a1a1a', padding: '50px 20px' }}>
        <h2 className="text-center mb-4" style={{ color: '#2ECC71', fontSize: '2.5rem', fontWeight: 700 }}>What We Offer</h2>
        <p style={{ textAlign: 'center', color: '#aaa', marginBottom: 40, fontSize: '1.1rem' }}>Everything you need for a healthier lifestyle</p>
        <div className="row g-4 justify-content-center">
          <div className="col-md-4">
            <div className="card h-100 shadow-sm text-center p-4" style={{
              backgroundColor: '#2c2c2c',
              border: '1px solid #444',
              color: '#e8e8e8',
              transition: 'all 0.3s',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => e.currentTarget.style.borderColor = '#2ECC71'}
            onMouseLeave={(e) => e.currentTarget.style.borderColor = '#444'}>
              <h5 style={{ color: '#2ECC71', fontSize: '1.5rem', marginBottom: 16 }}>Diet Planner</h5>
              <p className="text-muted" style={{ fontSize: 14, color: '#aaa' }}>
                Get personalised breakfast, lunch &amp; dinner recommendations powered by Machine Learning.
              </p>
              <Link to="/dietplanner" className="btn-brand mt-auto" style={{ marginTop: 'auto' }}>Get Started</Link>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100 shadow-sm text-center p-4" style={{
              backgroundColor: '#2c2c2c',
              border: '1px solid #444',
              color: '#e8e8e8',
              transition: 'all 0.3s',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => e.currentTarget.style.borderColor = '#2ECC71'}
            onMouseLeave={(e) => e.currentTarget.style.borderColor = '#444'}>
              <h5 style={{ color: '#2ECC71', fontSize: '1.5rem', marginBottom: 16 }}>Body Fat Calculator</h5>
              <p className="text-muted" style={{ fontSize: 14, color: '#aaa' }}>
                Calculate your body fat percentage instantly using your height, weight, age and gender.
              </p>
              <Link to="/bodymass" className="btn-brand">Calculate</Link>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100 shadow-sm text-center p-4" style={{
              backgroundColor: '#2c2c2c',
              border: '1px solid #444',
              color: '#e8e8e8',
              transition: 'all 0.3s',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => e.currentTarget.style.borderColor = '#2ECC71'}
            onMouseLeave={(e) => e.currentTarget.style.borderColor = '#444'}>
              <h5 style={{ color: '#2ECC71', fontSize: '1.5rem', marginBottom: 16 }}>AI Nutrition Chatbot</h5>
              <p className="text-muted" style={{ fontSize: 14, color: '#aaa' }}>
                Ask any nutrition or diet question and get instant AI-powered answers using GPT.
              </p>
              <Link to="/dashboard" className="btn-brand">Ask Now</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Developers */}
      <section style={{ background: '#2c2c2c', padding: '48px 0', borderTop: '1px solid #444' }}>
        <div className="container text-center">
          <h2 style={{ color: '#2ECC71', marginBottom: 12 }}>Developers</h2>
          <p className="text-muted" style={{ color: '#aaa', marginBottom: 0 }}>Rajdeep, Prajwal, Hrishikesh, Bhumika</p>
        </div>
      </section>
    </>
  );
}
