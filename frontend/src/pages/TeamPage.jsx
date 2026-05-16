import { Link } from 'react-router-dom';

const TEAM = [
  { name: 'Rajdeep Avhad',    role: 'Backend & ML Developer', path: 'rajdeep',    img: '/static/images/sagar.jpg' },
  { name: 'Prajwal Jadhav',   role: 'Frontend Developer',     path: 'prajwal',    img: '/static/images/satish.jpg' },
  { name: 'Hrishikesh Patil', role: 'Database & API',         path: 'hrishikesh', img: '/static/images/saurabh.jpg' },
  { name: 'Bhumika Sinha',    role: 'UI/UX Designer',         path: 'bhumika',    img: '/static/images/kousubh.jpg' },
];

export default function TeamPage() {
  return (
    <>
      <div className="page-banner">
        <h1>Our Team</h1>
        <p>The people behind EatRight – final year engineering students.</p>
      </div>

      <div className="container py-5">
        <div className="row g-4 justify-content-center">
          {TEAM.map(member => (
            <div key={member.path} className="col-md-3 col-sm-6">
              <div className="card text-center shadow-sm h-100 p-3">
                <img
                  src={member.img}
                  alt={member.name}
                  className="rounded-circle mx-auto mb-3"
                  style={{ width: 100, height: 100, objectFit: 'cover' }}
                  onError={e => { e.target.src = '/static/images/Gemini_Generated_Image_f0bd5kf0bd5kf0bd.png'; }}
                />
                <h5 style={{ color: '#2ECC71' }}>{member.name}</h5>
                <p className="text-muted" style={{ fontSize: 14 }}>{member.role}</p>
                <Link to={`/${member.path}`} className="btn-brand mt-auto" style={{ fontSize: 13 }}>
                  View Profile
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
