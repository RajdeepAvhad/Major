import { useState } from 'react';

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = e => {
    e.preventDefault();
    alert('Thank you for contacting us. We will get back to you as soon as possible.');
    setSubmitted(true);
    e.target.reset();
  };

  return (
    <>
      <div className="page-banner">
        <h1>Contact Us</h1>
        <p>Get in touch with the EatRight team.</p>
      </div>

      <div className="container py-5">
        <div className="row g-5 justify-content-center">
          {/* Contact Info */}
          <div className="col-md-5">
            <h4 style={{ color: '#2ECC71', marginBottom: 24 }}>Get in touch with us</h4>
            <div className="d-flex align-items-center mb-3 gap-3">
              <img src="/static/images/Gemini_Generated_Image_f0bd5kf0bd5kf0bd.png" height="40" alt="Logo" />
              <span style={{ color: '#e8e8e8' }}>EatRight</span>
            </div>
            <div className="d-flex align-items-center mb-3 gap-3">
              <i className="fas fa-envelope fa-lg" style={{ color: '#2ECC71', width: 32 }}></i>
              <a href="mailto:rajdeepavhad12345@gmail.com" style={{ color: '#aaa', textDecoration: 'none' }}>
                rajdeepavhad12345@gmail.com
              </a>
            </div>
            <div className="d-flex align-items-center mb-3 gap-3">
              <i className="fas fa-phone fa-lg" style={{ color: '#2ECC71', width: 32 }}></i>
              <span style={{ color: '#e8e8e8' }}>(+91) 988-XXXX</span>
            </div>
            <div className="d-flex align-items-center gap-3">
              <i className="fas fa-map-marker-alt fa-lg" style={{ color: '#2ECC71', width: 32 }}></i>
              <span style={{ color: '#e8e8e8' }}>Pune, Maharashtra, India – 412105</span>
            </div>
          </div>

          {/* Contact Form */}
          <div className="col-md-5">
            {submitted && <div className="alert alert-success" style={{ background: '#2c2c2c', color: '#4caf50', border: '1px solid #4caf50' }}>Message sent! We'll be in touch soon.</div>}
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label" style={{ color: '#e8e8e8' }}>Name</label>
                <input className="form-control" name="Name" required placeholder="Rajdeep Avhad"
                  style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
              </div>
              <div className="mb-3">
                <label className="form-label" style={{ color: '#e8e8e8' }}>Phone</label>
                <input className="form-control" type="tel" name="PhoneNumber" required placeholder="+91 9999988888"
                  style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
              </div>
              <div className="mb-3">
                <label className="form-label" style={{ color: '#e8e8e8' }}>Email</label>
                <input className="form-control" type="email" name="FromEmailAddress" required placeholder="you@email.com"
                  style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
              </div>
              <div className="mb-3">
                <label className="form-label" style={{ color: '#e8e8e8' }}>Message</label>
                <textarea className="form-control" name="Comments" rows="5" required placeholder="Your message..."
                  style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
              </div>
              <button className="btn-brand w-100" type="submit">Send Message</button>
            </form>
          </div>
        </div>
      </div>
    </>
  );
}
