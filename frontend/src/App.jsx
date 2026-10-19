import React, { useEffect, useState } from 'react';
import { NavLink, Route, Routes, useNavigate, useLocation } from 'react-router-dom';
import { Activity, CalendarDays, Heart, MessageCircle, BookOpen, ShieldCheck, Plus, Send, CheckCircle2, Clock3, Sparkles, Trash2, Menu, Settings, Phone, Info, Code, Wind, Flower, X } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { api } from './services/api.js';
import HerwellVoiceAssistant from './components/HerwellVoiceAssistant';
import ProfessionalCalendar from './components/ProfessionalCalendar';
import LoginPage from './components/LoginPage';

const navItems = [
  { path: '/', name: 'Dashboard' },
  { path: '/mood', name: 'Mood' },
  { path: '/assistant', name: 'AI Assistant' },
  { path: '/technical', name: 'Technical' },
  { path: '/planner', name: 'Tasks' },
  { path: '/calendar', name: 'Calendar' },
  { path: '/resources', name: 'Resources' },
  { path: '/breathing', name: 'Breathing' },
  { path: '/settings', name: 'Settings' },
  { path: '/support', name: 'Support' },
  { path: '/privacy', name: 'Privacy' }
];

// Force re-render on route change
function Layout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    api.logout();
    navigate('/login');
  };

  useEffect(() => {
    // Trigger scroll reveal animations
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.rv').forEach(el => observer.observe(el));

    return () => observer.disconnect();
  }, [location]); // Re-run on location change

  return <div key={location.pathname}>
    <div className="bg-decor">
      <div className="blob b1"></div>
      <div className="blob b2"></div>
      <div className="blob b3"></div>
    </div>
    <nav className="nav">
      <NavLink to="/" className="brand">
        Balance <strong>AI</strong>
      </NavLink>
      <div className={`nav-links ${menuOpen ? 'open' : ''}`}>
        {navItems.map(({ path, name }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) => isActive ? 'active' : ''}
            onClick={() => setMenuOpen(false)}
          >
            {name}
          </NavLink>
        ))}
      </div>
      <div className="nav-tools">
        <button 
          onClick={handleLogout}
          style={{
            padding: '0.5rem 1rem',
            background: 'var(--peach)',
            color: 'var(--purple-dark)',
            border: 'none',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            fontSize: '0.9rem',
            marginRight: '0.5rem'
          }}
        >
          Logout
        </button>
        <button className="menu-btn" onClick={() => setMenuOpen(!menuOpen)}>☰</button>
      </div>
    </nav>
    <main className="view">{children}</main>
  </div>;
}

function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [checkins, setCheckins] = useState([]);
  const [health, setHealth] = useState('checking');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    Promise.all([
      api.tasks().then(setTasks).catch(() => setTasks([])),
      api.checkins().then(setCheckins).catch(() => setCheckins([])),
      api.health().then(() => setHealth('connected')).catch(() => setHealth('offline'))
    ]).finally(() => setLoaded(true));
  }, []);

  const done = tasks.filter(t => t.completed).length;

  if (!loaded) {
    return <div className="view" style={{ textAlign: 'center', padding: '60px 0' }}>
      <p>Loading your space...</p>
    </div>;
  }

  return <div className="view">
    <h1>Your wellbeing space</h1>
    <p style={{ color: 'var(--muted)' }}>Small, kind steps can make a busy day feel more manageable.</p>

    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginTop: '1.5rem' }}>
      <div className="card">
        <h3>Mood check-in</h3>
        <p>{checkins[0]?.mood?.replace('_', ' ') || 'Not yet'}</p>
        <p style={{ color: 'var(--muted)', fontSize: '0.9rem' }}>There is no right or wrong mood.</p>
        <NavLink to="/mood" className="btn btn-primary">Check in</NavLink>
      </div>

      <div className="card">
        <h3>Study tasks</h3>
        <p style={{ fontSize: '2rem', fontWeight: '700', fontFamily: 'var(--font-head)' }}>{done}/{tasks.length}</p>
        <p style={{ color: 'var(--muted)' }}>Tasks completed</p>
        <NavLink to="/planner" className="btn btn-ghost">View planner</NavLink>
      </div>

      <div className="card">
        <h3>Gentle reminder</h3>
        <p>Take a pause</p>
        <p style={{ color: 'var(--muted)' }}>Rest is part of progress.</p>
        <NavLink to="/resources" className="btn btn-soft">Explore tips</NavLink>
      </div>
    </div>

    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '2rem' }}>
      <div className="card">
        <h3>Your week, gently</h3>
        <p style={{ color: 'var(--muted)' }}>Check-ins are shown when you add them.</p>
        {checkins.length ? (
          <div style={{ marginTop: '1.5rem' }}>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={checkins.slice(0, 7).map((x, i) => ({ day: `#${i + 1}`, stress: x.stress, energy: x.energy }))}>
                <XAxis dataKey="day" />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Bar dataKey="stress" fill="var(--purple)" radius={[5, 5, 0, 0]} />
                <Bar dataKey="energy" fill="var(--lavender)" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p style={{ color: 'var(--muted)', marginTop: '1.5rem' }}>Your check-in history will appear here</p>
        )}
      </div>

      <div className="card">
        <h3>Next small steps</h3>
        <p style={{ color: 'var(--muted)' }}>Keep it realistic.</p>
        <ul style={{ listStyle: 'none', padding: 0, marginTop: '1rem' }}>
          {tasks.filter(t => !t.completed).slice(0, 4).map(t => (
            <li key={t.id} style={{ padding: '0.5rem', background: 'var(--cream)', borderRadius: '12px', marginBottom: '0.5rem' }}>{t.title}</li>
          ))}
        </ul>
        {!tasks.some(t => !t.completed) && <p style={{ color: 'var(--muted)' }}>No tasks yet. Add one when you are ready.</p>}
        <NavLink to="/planner" className="btn btn-primary" style={{ marginTop: '1.5rem' }}>Plan my time</NavLink>
      </div>
    </div>
  </div>;
}

function MoodPage() {
  const [mood, setMood] = useState('okay');
  const [stress, setStress] = useState(3);
  const [energy, setEnergy] = useState(3);
  const [note, setNote] = useState('');
  const [message, setMessage] = useState('');

  const moods = [
    ['very_low', 'Very low', '😞'],
    ['low', 'Low', '🙁'],
    ['okay', 'Okay', '😐'],
    ['good', 'Good', '🙂'],
    ['great', 'Great', '😊']
  ];

  async function save(e) {
    e.preventDefault();
    try {
      await api.saveCheckin({ mood, stress: Number(stress), energy: Number(energy), note });
      setMessage('Your check-in was saved. Thank you for checking in with yourself.');
      setNote('');
    } catch {
      setMessage('Could not reach the backend. Start FastAPI and try again.');
    }
  }

  return <div className="view">
    <h1>How are you feeling today?</h1>
    <p style={{ color: 'var(--muted)' }}>There is no score to achieve. Share only what feels comfortable.</p>

    <div className="card" style={{ maxWidth: '560px', margin: '2rem auto' }}>
      <form onSubmit={save}>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '700', color: 'var(--muted)' }}>Your mood</label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.5rem', marginBottom: '1.5rem' }}>
          {moods.map(([id, label, emoji]) => (
            <button
              type="button"
              key={id}
              onClick={() => setMood(id)}
              style={{
                padding: '1rem 0.5rem',
                border: mood === id ? '2px solid var(--purple)' : '2px solid var(--line)',
                borderRadius: '16px',
                background: mood === id ? 'var(--cream)' : '#fff',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: '700',
                color: 'var(--text)',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ fontSize: '1.8rem', marginBottom: '0.25rem' }}>{emoji}</div>
              <small>{label}</small>
            </button>
          ))}
        </div>

        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '700', color: 'var(--muted)' }}>
          Stress level <b>{stress}/5</b>
        </label>
        <input
          type="range"
          min="1"
          max="5"
          value={stress}
          onChange={e => setStress(e.target.value)}
          style={{ width: '100%', marginBottom: '0.5rem', accentColor: 'var(--purple)' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--muted)', marginBottom: '1.5rem' }}>
          <span>Calm</span>
          <span>Overwhelmed</span>
        </div>

        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '700', color: 'var(--muted)' }}>
          Energy level <b>{energy}/5</b>
        </label>
        <input
          type="range"
          min="1"
          max="5"
          value={energy}
          onChange={e => setEnergy(e.target.value)}
          style={{ width: '100%', marginBottom: '0.5rem', accentColor: 'var(--purple)' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--muted)', marginBottom: '1.5rem' }}>
          <span>Low</span>
          <span>High</span>
        </div>

        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '700', color: 'var(--muted)' }}>Optional note</label>
        <textarea
          value={note}
          maxLength="1000"
          onChange={e => setNote(e.target.value)}
          placeholder="Anything you want to remember about today? (optional)"
          style={{ width: '100%', minHeight: '80px', marginBottom: '1rem', padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)', fontFamily: 'inherit' }}
        />

        <p style={{ color: 'var(--muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>
          <ShieldCheck size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
          {' '}Use demo data only. This prototype has no user authentication.
        </p>

        <button type="submit" className="btn btn-primary">Save check-in</button>

        {message && <p style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--muted)' }}>{message}</p>}
      </form>
    </div>
  </div>;
}

function AssistantPage() {
  return <HerwellVoiceAssistant />;
}

function PlannerPage() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState('');
  const [subject, setSubject] = useState('');
  const [duration, setDuration] = useState(45);
  const [priority, setPriority] = useState('medium');
  const [plan, setPlan] = useState(null);

  async function load() {
    try {
      setTasks(await api.tasks());
    } catch {
      console.error('Backend unavailable');
    }
  }

  useEffect(() => { load(); }, []);

  async function add(e) {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await api.addTask({ title, subject, duration_minutes: Number(duration), priority });
      setTitle('');
      setSubject('');
      await load();
    } catch {
      console.error('Task was not saved');
    }
  }

  async function toggle(task) {
    try {
      await api.updateTask(task.id, { completed: !task.completed });
      await load();
    } catch {
      console.error('Could not update task');
    }
  }

  async function remove(task) {
    try {
      await api.deleteTask(task.id);
      await load();
    } catch {
      console.error('Could not delete task');
    }
  }

  return <div className="view">
    <h1>Make space for what matters</h1>
    <p style={{ color: 'var(--muted)' }}>Add tasks, choose your available time, and generate a simple deterministic plan.</p>

    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
      <div className="card">
        <h3>Add a study task</h3>
        <form onSubmit={add}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '700', color: 'var(--muted)' }}>
            Task title
            <input
              required
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="e.g. Review database joins"
              style={{ marginTop: '0.25rem', padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)', width: '100%' }}
            />
          </label>

          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '700', color: 'var(--muted)' }}>
            Subject (optional)
            <input
              value={subject}
              onChange={e => setSubject(e.target.value)}
              placeholder="e.g. SQL"
              style={{ marginTop: '0.25rem', padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)', width: '100%' }}
            />
          </label>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
            <label style={{ fontWeight: '700', color: 'var(--muted)' }}>
              Duration
              <select value={duration} onChange={e => setDuration(e.target.value)} style={{ marginTop: '0.25rem', padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)', width: '100%' }}>
                <option value="25">25 min</option>
                <option value="45">45 min</option>
                <option value="60">60 min</option>
                <option value="90">90 min</option>
              </select>
            </label>

            <label style={{ fontWeight: '700', color: 'var(--muted)' }}>
              Priority
              <select value={priority} onChange={e => setPriority(e.target.value)} style={{ marginTop: '0.25rem', padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)', width: '100%' }}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>
          </div>

          <button type="submit" className="btn btn-primary">
            <Plus size={17} /> Add task
          </button>
        </form>
      </div>

      <div className="card">
        <h3>Your tasks</h3>
        <p style={{ color: 'var(--muted)' }}>{tasks.filter(t => !t.completed).length} remaining</p>

        <div style={{ marginTop: '1.5rem' }}>
          {tasks.map(t => (
            <div
              key={t.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem',
                marginBottom: '0.5rem',
                background: t.completed ? 'var(--cream)' : '#fff',
                borderRadius: '16px',
                opacity: t.completed ? 0.6 : 1,
                border: '1px solid var(--line)',
                border: '1px solid var(--line)'
              }}
            >
              <button
                onClick={() => toggle(t)}
                style={{
                  width: '24px',
                  height: '24px',
                  border: '1px solid var(--line)',
                  borderRadius: '6px',
                  background: t.completed ? 'var(--sage)' : '#fff',
                  color: t.completed ? '#fff' : 'var(--text)',
                  cursor: 'pointer'
                }}
              >
                {t.completed ? '✓' : ''}
              </button>
              <div style={{ flex: 1 }}>
                <b>{t.title}</b>
                <small style={{ display: 'block', color: 'var(--muted)' }}>
                  {t.subject || 'Study'} · {t.duration_minutes} min · {t.priority} priority
                </small>
              </div>
              <button
                onClick={() => remove(t)}
                style={{ padding: '4px', border: 'none', background: 'none', cursor: 'pointer', color: 'var(--muted)' }}
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>

        {!tasks.length && <p style={{ color: 'var(--muted)' }}>Your task list is empty. Add one task to begin.</p>}
      </div>
    </div>
  </div>;
}

function ResourcesPage() {
  const [items, setItems] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    api.resources().then(setItems).catch(() => setItems([]));
  }, []);

  const filtered = items.filter(x =>
    `${x.title} ${x.content} ${x.category}`.toLowerCase().includes(query.toLowerCase())
  );

  return <div className="view">
    <h1>A library for your everyday wellbeing</h1>
    <p style={{ color: 'var(--muted)' }}>These original educational notes are not medical advice. Check sources before using external health claims.</p>

    <div style={{ marginBottom: '1.5rem' }}>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search study, sleep, stress…"
        style={{ width: '100%', maxWidth: '400px', padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)' }}
      />
    </div>

    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
      {filtered.map((r, i) => (
        <article className="card" key={i}>
          <div className="card-body">
            <small style={{ color: 'var(--purple-dark)', textTransform: 'uppercase', fontSize: '12px', letterSpacing: '0.05em' }}>
              {r.category.replace('_', ' ')}
            </small>
            <h3>{r.title}</h3>
            <p>{r.content}</p>
            <p style={{ color: 'var(--muted)' }}>
              <ShieldCheck size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
              {' '}{r.source}
            </p>
          </div>
        </article>
      ))}
    </div>

    {!filtered.length && <p style={{ color: 'var(--muted)' }}>No resources match your search.</p>}
  </div>;
}

function BreathingPage() {
  const [phase, setPhase] = useState('idle');
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    if (phase === 'idle') return;

    const interval = setInterval(() => {
      setSeconds(s => {
        if (s >= 3) {
          setPhase(p => {
            if (p === 'inhale') return 'hold';
            if (p === 'hold') return 'exhale';
            if (p === 'exhale') return 'idle';
            return 'idle';
          });
          return 0;
        }
        return s + 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [phase]);

  const start = () => {
    setPhase('inhale');
    setSeconds(0);
  };

  return <div className="view" style={{ textAlign: 'center' }}>
    <h1>Box breathing exercise</h1>
    <p style={{ color: 'var(--muted)' }}>A simple technique to calm your mind and reduce stress.</p>

    <div
      style={{
        width: '200px',
        height: '200px',
        borderRadius: '50%',
        background: 'var(--peach)',
        margin: '2rem auto',
        display: 'grid',
        placeItems: 'center',
        position: 'relative',
        transition: 'transform 4s ease-in-out'
      }}
    >
      <div
        style={{
          position: 'absolute',
          inset: 0,
          borderRadius: '50%',
          background: 'var(--purple)',
          opacity: 0.3,
          transform: phase === 'inhale' ? 'scale(1)' : phase === 'exhale' ? 'scale(0.5)' : 'scale(0.75)',
          transition: 'transform 4s ease-in-out'
        }}
      />
      <div style={{ zIndex: 1, fontFamily: 'var(--font-head)', fontSize: '18px', color: 'var(--text)' }}>
        {phase === 'idle' ? 'Start' : phase === 'inhale' ? 'Inhale' : phase === 'hold' ? 'Hold' : 'Exhale'}
      </div>
    </div>

    <p style={{ fontSize: '14px', color: 'var(--muted)', maxWidth: '400px', margin: '0 auto' }}>
      {phase === 'idle'
        ? 'Press start to begin a 4-4-4-4 breathing cycle'
        : phase === 'inhale'
        ? 'Breathe in slowly through your nose'
        : phase === 'hold'
        ? 'Hold your breath gently'
        : 'Exhale slowly through your mouth'}
    </p>

    <button
      onClick={start}
      disabled={phase !== 'idle'}
      className="btn btn-primary"
      style={{ marginTop: '1.5rem' }}
    >
      {phase === 'idle' ? 'Start breathing' : 'In progress...'}
    </button>
  </div>;
}

function SettingsPage() {
  return <div className="view">
    <h1>Settings</h1>
    <p style={{ color: 'var(--muted)' }}>This demo does not have real authentication or per-user settings.</p>

    <div className="card" style={{ maxWidth: '560px' }}>
      <h3>Prototype settings</h3>
      <p style={{ color: 'var(--muted)' }}>The following features are placeholders for future development.</p>

      <div style={{ marginTop: '1.5rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '700', color: 'var(--muted)' }}>
          Language
          <select disabled style={{ marginTop: '0.25rem', padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)', width: '100%' }}>
            <option>Français</option>
            <option>English</option>
            <option>العربية</option>
          </select>
        </label>

        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '700', color: 'var(--muted)' }}>
          Theme
          <select disabled style={{ marginTop: '0.25rem', padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)', width: '100%' }}>
            <option>Light</option>
            <option>Dark (not implemented)</option>
          </select>
        </label>
      </div>
    </div>
  </div>;
}

function SupportPage() {
  return <div className="view">
    <h1>Support resources</h1>
    <p style={{ color: 'var(--muted)' }}>If you are in immediate danger, contact local emergency services right away.</p>

    <div className="card">
      <h3>Verified local contacts</h3>
      <p style={{ color: 'var(--purple-dark)', background: 'var(--peach)', padding: '0.75rem', borderRadius: '12px' }}>
        <Phone size={16} style={{ display: 'inline', verticalAlign: 'middle' }} />
        {' '}No verified contacts are configured in this demo. For production, add only verified local emergency and support contacts before deployment.
      </p>
    </div>

    <div className="card" style={{ marginTop: '1.5rem' }}>
      <h3>When to seek help</h3>
      <p>If you are feeling overwhelmed, consider reaching out to a trusted friend, family member, or campus counseling service.</p>
    </div>
  </div>;
}

function TechnicalPage() {
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hello! I\'m your Technical PFE Assistant. I can help you with debugging, architecture, code review, database design, API development, and more.' }
  ]);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);

  useEffect(() => {
    api.projects().then(setProjects).catch(() => setProjects([]));
  }, []);

  async function send(e) {
    e.preventDefault();
    if (!input.trim() || busy) return;
    const value = input.trim();
    setMessages(m => [...m, { role: 'user', text: value }]);
    setInput('');
    setBusy(true);
    try {
      const result = await api.technicalChat({ message: value, project_id: selectedProject });
      setMessages(m => [...m, { role: 'assistant', text: result.response, sources: result.sources }]);
    } catch {
      setMessages(m => [...m, { role: 'assistant', text: 'The backend is unavailable. Please start the FastAPI server.' }]);
    } finally {
      setBusy(false);
    }
  }

  return <div className="view">
    <h1>Technical PFE Assistant</h1>
    <p style={{ color: 'var(--muted)' }}>Your AI-powered engineering copilot for debugging, architecture, and project development.</p>

    <div className="card" style={{ marginTop: '1.5rem' }}>
      <div style={{ marginBottom: '1rem' }}>
        <label style={{ fontWeight: '700', color: 'var(--muted)' }}>Select project</label>
        <select
          value={selectedProject || ''}
          onChange={e => setSelectedProject(Number(e.target.value) || null)}
          style={{ marginTop: '0.25rem', padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)', width: '100%' }}
        >
          <option value="">No project selected</option>
          {projects.map(p => (
            <option key={p.id} value={p.id}>{p.title}</option>
          ))}
        </select>
      </div>

      <div style={{ maxHeight: '400px', overflowY: 'auto', marginBottom: '1rem' }}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              padding: '0.75rem',
              marginBottom: '0.5rem',
              borderRadius: '16px',
              background: m.role === 'user' ? 'var(--cream)' : '#fff',
              marginLeft: m.role === 'user' ? 'auto' : '0',
              marginRight: m.role === 'user' ? '0' : 'auto',
              maxWidth: '80%',
              border: '1px solid var(--line)'
            }}
          >
            <small style={{ color: 'var(--muted)', fontSize: '12px' }}>{m.role === 'user' ? 'You' : 'Balance AI'}</small>
            <p style={{ marginTop: '0.25rem' }}>{m.text}</p>
            {m.sources?.length > 0 && (
              <div style={{ marginTop: '0.5rem', fontSize: '12px', color: 'var(--muted)' }}>
                Sources: {m.sources.map((s, j) => s.title).join(', ')}
              </div>
            )}
          </div>
        ))}
        {busy && <p style={{ color: 'var(--muted)' }}>Thinking carefully…</p>}
      </div>

      <form onSubmit={send} style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a technical question…"
          style={{ flex: 1, padding: '0.7rem 0.9rem', border: '2px solid var(--line)', borderRadius: 'var(--radius-sm)', background: 'var(--cream)' }}
        />
        <button type="submit" className="btn btn-primary" disabled={busy || !input.trim()}>
          <Send size={18} />
        </button>
      </form>
    </div>
  </div>;
}

function PrivacyPage() {
  return <div className="view" style={{ maxWidth: '720px' }}>
    <h1>Privacy & Safety</h1>
    <p style={{ color: 'var(--muted)' }}>Understanding how Balance AI handles your data and protects your wellbeing.</p>

    <div className="card" style={{ marginTop: '1.5rem' }}>
      <h3>Data collection</h3>
      <p>This hackathon prototype uses demo data only and has no authentication. Do not enter sensitive personal information.</p>
    </div>

    <div className="card" style={{ marginTop: '1.5rem' }}>
      <h3>Not a medical service</h3>
      <p>Balance AI is educational support only. It does not diagnose conditions, prescribe treatments, or replace professional care. If you may be in immediate danger, contact verified local emergency support.</p>
    </div>

    <div className="card" style={{ marginTop: '1.5rem' }}>
      <h3>Data deletion</h3>
      <p>In this demo, data is stored locally. Clear your browser data to remove all information.</p>
    </div>
  </div>;
}

function NotFound() {
  return <div className="view" style={{ textAlign: 'center', padding: '4rem 0' }}>
    <h1>Page not found</h1>
    <p style={{ color: 'var(--muted)' }}>The page you're looking for doesn't exist.</p>
    <NavLink to="/" className="btn btn-primary" style={{ marginTop: '1.5rem' }}>Go to Dashboard</NavLink>
  </div>;
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
    setLoading(false);
  }, []);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '4rem' }}>Loading...</div>;
  }

  // Redirect to login if not authenticated and not on login page
  if (!isAuthenticated && location.pathname !== '/login') {
    navigate('/login');
    return null;
  }

  return <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/" element={<Layout><Dashboard /></Layout>} />
    <Route path="/mood" element={<Layout><MoodPage /></Layout>} />
    <Route path="/assistant" element={<Layout><AssistantPage /></Layout>} />
    <Route path="/technical" element={<Layout><TechnicalPage /></Layout>} />
    <Route path="/planner" element={<Layout><PlannerPage /></Layout>} />
    <Route path="/calendar" element={<Layout><ProfessionalCalendar /></Layout>} />
    <Route path="/resources" element={<Layout><ResourcesPage /></Layout>} />
    <Route path="/breathing" element={<Layout><BreathingPage /></Layout>} />
    <Route path="/settings" element={<Layout><SettingsPage /></Layout>} />
    <Route path="/support" element={<Layout><SupportPage /></Layout>} />
    <Route path="/privacy" element={<Layout><PrivacyPage /></Layout>} />
    <Route path="*" element={<Layout><NotFound /></Layout>} />
  </Routes>;
}
