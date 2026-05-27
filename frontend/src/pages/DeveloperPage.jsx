// Unified Developer Portfolio Page — shows the relevant developer's info based on `name` prop

const DEVS = {
  rajdeep: {
    name: 'Rajdeep Avhad',
    role: 'Backend & ML Developer',
    email: 'rajdeepavhad@gmail.com',
    github: '#',
    linkedin: '#',
    img: '/static/images/sagar.jpg',
    about: 'Final year Computer Engineering student with a passion for machine learning and backend development. Built the core ML recommendation engine (K-Means + Random Forest) and Django REST API for EatRight.',
    skills: ['Python', 'Django', 'Machine Learning', 'scikit-learn', 'pandas', 'SQL', 'REST APIs'],
    education: 'B.E. Computer Engineering – Pune University',
  },
  prajwal: {
    name: 'Prajwal Jadhav',
    role: 'Frontend Developer',
    email: 'prajwal@gmail.com',
    github: '#',
    linkedin: '#',
    img: '/static/images/satish.jpg',
    about: 'Frontend enthusiast who transformed the EatRight UI from Django templates to a modern React.js SPA with clean, responsive design.',
    skills: ['React.js', 'JavaScript', 'HTML5', 'CSS3', 'Bootstrap', 'Figma'],
    education: 'B.E. Computer Engineering – Pune University',
  },
  hrishikesh: {
    name: 'Hrishikesh Patil',
    role: 'Database & API',
    email: 'hrishikesh@gmail.com',
    github: '#',
    linkedin: '#',
    img: '/static/images/saurabh.jpg',
    about: 'Database and API specialist who designed and optimised the SQLite schema, Django models, and the AJAX/REST layer for seamless data flow.',
    skills: ['SQLite', 'Django ORM', 'REST APIs', 'JSON', 'Python', 'Git'],
    education: 'B.E. Computer Engineering – Pune University',
  },
  bhumika: {
    name: 'Bhumika Sinha',
    role: 'UI/UX Designer',
    email: 'bhumika@gmail.com',
    github: '#',
    linkedin: '#',
    img: '/static/images/kousubh.jpg',
    about: 'UI/UX designer responsible for the EatRight visual identity, wireframes and colour palette. Ensured a delightful, accessible user experience across all pages.',
    skills: ['Figma', 'Adobe XD', 'UI Design', 'Canva', 'Bootstrap', 'CSS'],
    education: 'B.E. Computer Engineering – Pune University',
  },
};

export default function DeveloperPage({ name }) {
  const dev = DEVS[name] || DEVS.rajdeep;

  return (
    <>
      <div className="page-banner">
        <h1>{dev.name}</h1>
        <p>{dev.role}</p>
      </div>

      <div className="container py-5" style={{ maxWidth: 800 }}>
        <div className="card shadow-sm p-4">
          <div className="d-flex align-items-center gap-4 mb-4 flex-wrap">
            <img
              src={dev.img}
              alt={dev.name}
              className="rounded-circle"
              style={{ width: 120, height: 120, objectFit: 'cover', border: '4px solid #2ECC71' }}
              onError={e => { e.target.src = '/static/images/logo.png'; }}
            />
            <div>
              <h3 style={{ color: '#2ECC71', marginBottom: 4 }}>{dev.name}</h3>
              <p className="text-muted mb-2">{dev.role}</p>
              <div className="d-flex gap-3">
                <a href={`mailto:${dev.email}`} style={{ color: '#2ECC71' }}>
                  <i className="fas fa-envelope"></i> {dev.email}
                </a>
              </div>
              <div className="d-flex gap-3 mt-2">
                <a href={dev.github} className="btn-brand" style={{ fontSize: 13, padding: '4px 14px' }}>
                  <i className="fab fa-github"></i> GitHub
                </a>
                <a href={dev.linkedin} className="btn-brand" style={{ fontSize: 13, padding: '4px 14px', background: '#0077b5' }}>
                  <i className="fab fa-linkedin"></i> LinkedIn
                </a>
              </div>
            </div>
          </div>

          <hr />

          <h5 style={{ color: '#2ECC71' }}>About</h5>
          <p className="text-muted mb-4">{dev.about}</p>

          <h5 style={{ color: '#2ECC71' }}>Education</h5>
          <p className="text-muted mb-4">{dev.education}</p>

          <h5 style={{ color: '#2ECC71' }}>Skills</h5>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {dev.skills.map(skill => (
              <span key={skill} style={{
                background: '#3d3d3d', border: '1px solid #2ECC71',
                color: '#2ECC71', borderRadius: 20, padding: '4px 14px', fontSize: 13,
              }}>
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
