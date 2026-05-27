import { Link } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { ArrowUp, Globe, Link2, Send } from 'lucide-react';

export default function Footer() {
  const [showTop, setShowTop] = useState(false);

  useEffect(() => {
    const onScroll = () => setShowTop(window.scrollY > 300);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <footer className="site-footer">
      <div className="site-footer__line" />
      <div className="container">
        <div className="row">
          <div className="col-lg-3 col-md-6 mb-4">
            <img className="site-logo site-logo--footer" src="/static/images/logo.png" alt="EatRight" />
          </div>

          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="text-uppercase mb-3">Links</h5>
            <ul className="list-unstyled">
              <li><Link to="/home">Home</Link></li>
              <li><Link to="/dietplanner">Diet Planner</Link></li>
              <li><Link to="/bodymass">Body Fat Calc</Link></li>
              <li><Link to="/contact">Contact Us</Link></li>
            </ul>
          </div>

          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="text-uppercase mb-3">Developers</h5>
            <ul className="list-unstyled">
              <li>Rajdeep Avhad</li>
              <li>Prajwal Jadhav</li>
              <li>Hrishikesh Patil</li>
              <li>Bhumika Sinha</li>
            </ul>
          </div>

          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="text-uppercase mb-3">Social</h5>
            <div>
              <a href="#" className="footer-icon" aria-label="LinkedIn"><Link2 size={18} /></a>
              <a href="#" className="footer-icon" aria-label="Portfolio"><Globe size={18} /></a>
              <a href="https://www.instagram.com/" className="footer-icon" aria-label="Instagram"><Send size={18} /></a>
            </div>
          </div>
        </div>

        <hr style={{ borderColor: '#444' }} />
        <p className="text-center" style={{ color: '#999', fontSize: 13 }}>
          © 2024 EatRight – WeCare Food Recommendation System
        </p>
      </div>

      {showTop && (
        <button className="back-to-top" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} aria-label="Back to top">
          <ArrowUp size={18} />
        </button>
      )}
    </footer>
  );
}
