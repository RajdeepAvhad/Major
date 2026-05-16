import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function BodyFatPage() {
  const [height, setHeight] = useState('');
  const [weight, setWeight] = useState('');
  const [age, setAge]       = useState('');
  const [gender, setGender] = useState('m');
  const [result, setResult] = useState('');

  const calculate = () => {
    const h = parseFloat(height);
    const w = parseFloat(weight);
    const a = parseInt(age);
    if (!h || !w || !a) { setResult('Please fill all fields.'); return; }
    const bmi = w / (h * h);
    let bfp;
    if (gender === 'f') bfp = (1.20 * bmi) + (0.23 * a) - 5.4;
    else                bfp = (1.20 * bmi) + (0.23 * a) - 16.2;
    setResult(`Your Body Fat Percentage is ${bfp.toFixed(2)}%`);
  };

  return (
    <div className="bodyfat-section">
      <div className="bodyfat-card">
        <h2 style={{ color: '#2ECC71', marginBottom: 20 }}>Body Fat % Calculator</h2>

        <div className="mb-3">
          <label style={{ color: '#2ECC71', fontWeight: 500 }}>Height (m)</label>
          <input className="form-control mt-1" type="number" step="0.01" placeholder="e.g. 1.70"
            value={height} onChange={e => setHeight(e.target.value)}
            style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
        </div>

        <div className="mb-3">
          <label style={{ color: '#2ECC71', fontWeight: 500 }}>Weight (kg)</label>
          <input className="form-control mt-1" type="number" placeholder="e.g. 70"
            value={weight} onChange={e => setWeight(e.target.value)}
            style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
        </div>

        <div className="mb-3">
          <label style={{ color: '#2ECC71', fontWeight: 500 }}>Age</label>
          <input className="form-control mt-1" type="number" placeholder="e.g. 22"
            value={age} onChange={e => setAge(e.target.value)}
            style={{ background: '#3d3d3d', color: '#e8e8e8', border: '1px solid #555' }} />
        </div>

        <div className="mb-3">
          <label style={{ color: '#2ECC71', fontWeight: 500 }}>Gender</label>
          <div className="d-flex gap-4 mt-1">
            <label style={{ color: '#e8e8e8' }}><input type="radio" value="m" checked={gender === 'm'} onChange={() => setGender('m')} /> Male</label>
            <label style={{ color: '#e8e8e8' }}><input type="radio" value="f" checked={gender === 'f'} onChange={() => setGender('f')} /> Female</label>
          </div>
        </div>

        {result && <p style={{ color: '#2ECC71', fontWeight: 700, marginBottom: 16 }}>{result}</p>}

        <div className="d-flex gap-2 flex-wrap">
          <button className="btn-brand" onClick={calculate}>Calculate</button>
          <button className="btn-brand" style={{ background: '#666' }} onClick={() => {
            setHeight(''); setWeight(''); setAge(''); setGender('m'); setResult('');
          }}>Reset</button>
          <Link to="/dietplanner" className="btn-brand" style={{ background: '#27AE60' }}>
            Plan My Diet
          </Link>
        </div>
      </div>
    </div>
  );
}
