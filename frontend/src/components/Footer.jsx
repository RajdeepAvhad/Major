import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container">
        <div className="row">
          {/* Logo */}
          <div className="col-lg-3 col-md-6 mb-4">
            <img src="/static/images/Gemini_Generated_Image_f0bd5kf0bd5kf0bd.png" alt="EatRight" height="100" />
          </div>

          {/* Links */}
          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="text-uppercase mb-3">Links</h5>
            <ul className="list-unstyled">
              <li><Link to="/home">Home</Link></li>
              <li><Link to="/dietplanner">Diet Planner</Link></li>
              <li><Link to="/bodymass">Body Fat Calc</Link></li>
              <li><Link to="/contact">Contact Us</Link></li>
            </ul>
          </div>

          {/* Developers */}
          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="text-uppercase mb-3">Developers</h5>
            <ul className="list-unstyled">
              <li>Rajdeep Avhad</li>
              <li>Prajwal Jadhav</li>
              <li>Hrishikesh Patil</li>
              <li>Bhumika Sinha</li>
            </ul>
          </div>

          {/* Social */}
          <div className="col-lg-3 col-md-6 mb-4">
            <h5 className="text-uppercase mb-3">Social</h5>
            <div>
              <a href="#" className="footer-icon"><i className="fab fa-linkedin"></i></a>
              <a href="#" className="footer-icon"><i className="fab fa-github"></i></a>
              <a href="https://www.instagram.com/" className="footer-icon"><i className="fab fa-instagram"></i></a>
              <a href="#" className="footer-icon"><i className="fab fa-facebook"></i></a>
            </div>
          </div>
        </div>

        <hr style={{ borderColor: '#444' }} />
        <p className="text-center" style={{ color: '#999', fontSize: 13 }}>
          © 2024 EatRight – WeCare Food Recommendation System
        </p>
      </div>
    </footer>
  );
}
