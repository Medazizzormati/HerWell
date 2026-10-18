import React, { useEffect, useState } from 'react';
import { NavLink, Route, Routes, useNavigate } from 'react-router-dom';
import { Activity, CalendarDays, Heart, MessageCircle, BookOpen, ShieldCheck, Plus, Send, CheckCircle2, Clock3, Sparkles, Trash2, Menu, Settings, Phone, Info, Code, Wind, Flower, X } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { api } from './services/api.js';
import HerwellVoiceAssistant from './components/HerwellVoiceAssistant';
import ProfessionalCalendar from './components/ProfessionalCalendar';

const nav = [
  { to: '/', label: 'Dashboard' },
  { to: '/mood', label: 'Mood check-in' },
  { to: '/assistant', label: 'AI assistant' },
  { to: '/technical', label: 'Technical PFE' },
  { to: '/menstrual', label: 'Women\'s Wellbeing' },
  { to: '/planner', label: 'Study planner' },
  { to: '/calendar', label: 'Calendar' },
  { to: '/resources', label: 'Resources' },
  { to: '/breathing', label: 'Breathing' },
  { to: '/settings', label: 'Settings' },
  { to: '/support', label: 'Support' }
];

function Layout({ children }) {
  const [menuOpen, setMenuOpen] = useState(false);

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
  }, []);

  return <div className="app-shell">
    <header className="hdr">
      <a href="/" className="logo">
        <div className="logo-name">HERwell</div>
        <div className="logo-tag">AI wellbeing companion</div>
      </a>
      <nav className={menuOpen ? 'open' : ''}>
        {nav.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => isActive ? 'active' : ''}
            onClick={() => setMenuOpen(false)}
          >
            {label}
          </NavLink>
        ))}
      </nav>
      <button
        className="burger"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen(!menuOpen)}
        aria-label="Toggle menu"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>
    </header>
    <main className="wrap pg sec">{children}</main>
    <footer className="ftr">
      <div className="wrap fgrid">
        <div>
          <a href="/" className="logo">
            <div className="logo-name">HERwell</div>
            <div className="logo-tag">AI wellbeing companion</div>
          </a>
          <p className="fine" style={{ marginTop: '12px' }}>
            A supportive AI companion for women students and graduates in Tunisia.
          </p>
        </div>
        <nav>
          {nav.map(({ to, label }) => (
            <NavLink key={to} to={to}>{label}</NavLink>
          ))}
        </nav>
        <div>
          <p className="fine">
            <ShieldCheck size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
            <br />
            This is educational support, not a medical service.
          </p>
        </div>
      </div>
      <div className="wrap copy-line">
        HERwell AI · A supportive companion, not a diagnosis. ·{' '}
        <a href="/privacy">Privacy & safety</a>
      </div>
    </footer>
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
    return <div className="rv" style={{ textAlign: 'center', padding: '60px 0' }}>
      <p className="lead">Loading your space...</p>
    </div>;
  }

  return <div className="rv">
    <h2>Your wellbeing space</h2>
    <p className="lead">Small, kind steps can make a busy day feel more manageable.</p>

    <div className="grid">
      <div className="card">
        <div className="card-body">
          <h3>Mood check-in</h3>
          <p>{checkins[0]?.mood?.replace('_', ' ') || 'Not yet'}</p>
          <p className="fine">There is no right or wrong mood.</p>
          <a href="/mood" className="btn">Check in</a>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <h3>Study tasks</h3>
          <p className="price">{done}/{tasks.length}</p>
          <p className="fine">Tasks completed</p>
          <a href="/planner" className="btn">View planner</a>
        </div>
      </div>

      <div className="card">
        <div className="card-body">
          <h3>Gentle reminder</h3>
          <p>Take a pause</p>
          <p className="fine">Rest is part of progress.</p>
          <a href="/resources" className="btn">Explore tips</a>
        </div>
      </div>
    </div>

    <div className="split" style={{ marginTop: '64px' }}>
      <div className="panel">
        <h3>Your week, gently</h3>
        <p className="fine">Check-ins are shown when you add them.</p>
        {checkins.length ? (
          <div style={{ marginTop: '24px' }}>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={checkins.slice(0, 7).map((x, i) => ({ day: `#${i + 1}`, stress: x.stress, energy: x.energy }))}>
                <XAxis dataKey="day" />
                <YAxis domain={[0, 5]} />
                <Tooltip />
                <Bar dataKey="stress" fill="#652D90" radius={[5, 5, 0, 0]} />
                <Bar dataKey="energy" fill="#8B4DB8" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="fine" style={{ marginTop: '24px' }}>Your check-in history will appear here</p>
        )}
      </div>

      <div className="panel">
        <h3>Next small steps</h3>
        <p className="fine">Keep it realistic.</p>
        <ul className="chips" style={{ listStyle: 'none', padding: 0 }}>
          {tasks.filter(t => !t.completed).slice(0, 4).map(t => (
            <li key={t.id}>{t.title}</li>
          ))}
        </ul>
        {!tasks.some(t => !t.completed) && <p className="fine">No tasks yet. Add one when you are ready.</p>}
        <a href="/planner" className="btn solid" style={{ marginTop: '24px' }}>Plan my time</a>
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

  return <div className="rv">
    <h2>How are you feeling today?</h2>
    <p className="lead">There is no score to achieve. Share only what feels comfortable.</p>

    <div className="panel" style={{ maxWidth: '560px' }}>
      <form onSubmit={save}>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>Your mood</label>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
          {moods.map(([id, label, emoji]) => (
            <button
              type="button"
              key={id}
              onClick={() => setMood(id)}
              style={{
                flex: 1,
                padding: '16px',
                border: mood === id ? '2px solid var(--primary)' : '1px solid var(--line)',
                borderRadius: '12px',
                background: mood === id ? 'var(--ivory2)' : '#fff',
                cursor: 'pointer',
                fontSize: '13px'
              }}
            >
              <div style={{ fontSize: '24px', marginBottom: '4px' }}>{emoji}</div>
              <small>{label}</small>
            </button>
          ))}
        </div>

        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>
          Stress level <b>{stress}/5</b>
        </label>
        <input
          type="range"
          min="1"
          max="5"
          value={stress}
          onChange={e => setStress(e.target.value)}
          style={{ width: '100%', marginBottom: '8px' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--mute)', marginBottom: '24px' }}>
          <span>Calm</span>
          <span>Overwhelmed</span>
        </div>

        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>
          Energy level <b>{energy}/5</b>
        </label>
        <input
          type="range"
          min="1"
          max="5"
          value={energy}
          onChange={e => setEnergy(e.target.value)}
          style={{ width: '100%', marginBottom: '8px' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--mute)', marginBottom: '24px' }}>
          <span>Low</span>
          <span>High</span>
        </div>

        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>Optional note</label>
        <textarea
          value={note}
          maxLength="1000"
          onChange={e => setNote(e.target.value)}
          placeholder="Anything you want to remember about today? (optional)"
          style={{ width: '100%', minHeight: '80px', marginBottom: '16px' }}
        />

        <p className="fine" style={{ marginBottom: '16px' }}>
          <ShieldCheck size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
          {' '}Use demo data only. This prototype has no user authentication.
        </p>

        <button type="submit" className="btn solid">Save check-in</button>

        {message && <p style={{ marginTop: '16px', fontSize: '14px', color: 'var(--gold-d)' }}>{message}</p>}
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

  return <div className="rv">
    <h2>Make space for what matters</h2>
    <p className="lead">Add tasks, choose your available time, and generate a simple deterministic plan.</p>

    <div className="split">
      <div className="panel">
        <h3>Add a study task</h3>
        <form onSubmit={add}>
          <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>
            Task title
            <input
              required
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="e.g. Review database joins"
              style={{ marginTop: '4px' }}
            />
          </label>

          <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>
            Subject (optional)
            <input
              value={subject}
              onChange={e => setSubject(e.target.value)}
              placeholder="e.g. SQL"
              style={{ marginTop: '4px' }}
            />
          </label>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
            <label style={{ fontSize: '14px', color: 'var(--mute)' }}>
              Duration
              <select value={duration} onChange={e => setDuration(e.target.value)} style={{ marginTop: '4px' }}>
                <option value="25">25 min</option>
                <option value="45">45 min</option>
                <option value="60">60 min</option>
                <option value="90">90 min</option>
              </select>
            </label>

            <label style={{ fontSize: '14px', color: 'var(--mute)' }}>
              Priority
              <select value={priority} onChange={e => setPriority(e.target.value)} style={{ marginTop: '4px' }}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </label>
          </div>

          <button type="submit" className="btn solid">
            <Plus size={17} /> Add task
          </button>
        </form>
      </div>

      <div className="panel">
        <h3>Your tasks</h3>
        <p className="fine">{tasks.filter(t => !t.completed).length} remaining</p>

        <div style={{ marginTop: '24px' }}>
          {tasks.map(t => (
            <div
              key={t.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px',
                marginBottom: '8px',
                background: t.completed ? 'var(--ivory2)' : '#fff',
                borderRadius: '12px',
                opacity: t.completed ? 0.6 : 1
              }}
            >
              <button
                onClick={() => toggle(t)}
                style={{
                  width: '24px',
                  height: '24px',
                  border: '1px solid var(--line)',
                  borderRadius: '6px',
                  background: t.completed ? 'var(--gold-d)' : '#fff',
                  color: t.completed ? '#fff' : 'var(--ink)',
                  cursor: 'pointer'
                }}
              >
                {t.completed ? '✓' : ''}
              </button>
              <div style={{ flex: 1 }}>
                <b>{t.title}</b>
                <small style={{ display: 'block', color: 'var(--mute)' }}>
                  {t.subject || 'Study'} · {t.duration_minutes} min · {t.priority} priority
                </small>
              </div>
              <button
                onClick={() => remove(t)}
                style={{ padding: '4px', border: 'none', background: 'none', cursor: 'pointer', color: 'var(--mute)' }}
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>

        {!tasks.length && <p className="fine">Your task list is empty. Add one task to begin.</p>}
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

  return <div className="rv">
    <h2>A library for your everyday wellbeing</h2>
    <p className="lead">These original educational notes are not medical advice. Check sources before using external health claims.</p>

    <div style={{ marginBottom: '38px' }}>
      <input
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search study, sleep, stress…"
        style={{ width: '100%', maxWidth: '400px', padding: '14px' }}
      />
    </div>

    <div className="grid">
      {filtered.map((r, i) => (
        <article className="card" key={i}>
          <div className="card-body">
            <small style={{ color: 'var(--gold-d)', textTransform: 'uppercase', fontSize: '12px', letterSpacing: '0.05em' }}>
              {r.category.replace('_', ' ')}
            </small>
            <h3>{r.title}</h3>
            <p>{r.content}</p>
            <p className="fine">
              <ShieldCheck size={14} style={{ display: 'inline', verticalAlign: 'middle' }} />
              {' '}{r.source}
            </p>
          </div>
        </article>
      ))}
    </div>

    {!filtered.length && <p className="fine">No resources match your search.</p>}
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

  return <div className="rv" style={{ textAlign: 'center' }}>
    <h2>Box breathing exercise</h2>
    <p className="lead">A simple technique to calm your mind and reduce stress.</p>

    <div
      style={{
        width: '200px',
        height: '200px',
        borderRadius: '50%',
        background: 'var(--blush)',
        margin: '40px auto',
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
          background: 'var(--primary)',
          opacity: 0.3,
          transform: phase === 'inhale' ? 'scale(1)' : phase === 'exhale' ? 'scale(0.5)' : 'scale(0.75)',
          transition: 'transform 4s ease-in-out'
        }}
      />
      <div style={{ zIndex: 1, fontFamily: 'var(--serif)', fontSize: '18px', color: 'var(--ink)' }}>
        {phase === 'idle' ? 'Start' : phase === 'inhale' ? 'Inhale' : phase === 'hold' ? 'Hold' : 'Exhale'}
      </div>
    </div>

    <p style={{ fontSize: '14px', color: 'var(--mute)', maxWidth: '400px', margin: '0 auto' }}>
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
      className="btn solid"
      style={{ marginTop: '24px' }}
    >
      {phase === 'idle' ? 'Start breathing' : 'In progress...'}
    </button>
  </div>;
}

function SettingsPage() {
  return <div className="rv">
    <h2>Settings</h2>
    <p className="lead">This demo does not have real authentication or per-user settings.</p>

    <div className="panel" style={{ maxWidth: '560px' }}>
      <h3>Prototype settings</h3>
      <p className="fine">The following features are placeholders for future development.</p>

      <div style={{ marginTop: '24px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>
          Language
          <select disabled style={{ marginTop: '4px', width: '100%' }}>
            <option>Français</option>
            <option>English</option>
            <option>العربية</option>
          </select>
        </label>

        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>
          Theme
          <select disabled style={{ marginTop: '4px', width: '100%' }}>
            <option>Light</option>
            <option>Dark (not implemented)</option>
          </select>
        </label>
      </div>
    </div>
  </div>;
}

function SupportPage() {
  return <div className="rv">
    <h2>Support resources</h2>
    <p className="lead">If you are in immediate danger, contact local emergency services right away.</p>

    <div className="panel">
      <h3>Verified local contacts</h3>
      <p className="warning" style={{ color: 'var(--gold-d)' }}>
        <Phone size={16} style={{ display: 'inline', verticalAlign: 'middle' }} />
        {' '}No verified contacts are configured in this demo. For production, add only verified local emergency and support contacts before deployment.
      </p>
    </div>

    <div className="panel" style={{ marginTop: '26px' }}>
      <h3>When to seek help</h3>
      <p>If you are feeling overwhelmed, consider reaching out to a trusted friend, family member, or campus counseling service.</p>
    </div>
  </div>;
}

function LoginPage() {
  return <div className="rv" style={{ maxWidth: '560px', margin: '0 auto' }}>
    <h2>Sign in to HERwell</h2>
    <p className="lead">Authentication is not implemented in this hackathon prototype.</p>

    <div className="panel">
      <p className="fine">
        <Info size={16} style={{ display: 'inline', verticalAlign: 'middle' }} />
        {' '}This is a placeholder for future development.
      </p>

      <form style={{ marginTop: '24px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>
          Email
          <input type="email" placeholder="your.email@example.com" disabled style={{ marginTop: '4px', width: '100%' }} />
        </label>

        <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: 'var(--mute)' }}>
          Password
          <input type="password" placeholder="••••••••" disabled style={{ marginTop: '4px', width: '100%' }} />
        </label>

        <button type="submit" className="btn solid" disabled>Sign in</button>
      </form>

      <p className="fine" style={{ marginTop: '16px' }}>Demo mode active — no account required to explore the interface.</p>
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

  return <div className="rv">
    <h2>Technical PFE Assistant</h2>
    <p className="lead">Your AI-powered engineering copilot for debugging, architecture, and project development.</p>

    <div className="panel">
      <div style={{ marginBottom: '16px' }}>
        <label style={{ fontSize: '14px', color: 'var(--mute)' }}>Select project</label>
        <select
          value={selectedProject || ''}
          onChange={e => setSelectedProject(Number(e.target.value) || null)}
          style={{ marginTop: '4px', width: '100%' }}
        >
          <option value="">No project selected</option>
          {projects.map(p => (
            <option key={p.id} value={p.id}>{p.title}</option>
          ))}
        </select>
      </div>

      <div style={{ maxHeight: '400px', overflowY: 'auto', marginBottom: '16px' }}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              padding: '12px',
              marginBottom: '8px',
              borderRadius: '12px',
              background: m.role === 'user' ? 'var(--ivory2)' : '#fff',
              marginLeft: m.role === 'user' ? 'auto' : '0',
              marginRight: m.role === 'user' ? '0' : 'auto',
              maxWidth: '80%'
            }}
          >
            <small style={{ color: 'var(--mute)', fontSize: '12px' }}>{m.role === 'user' ? 'You' : 'HERwell'}</small>
            <p style={{ marginTop: '4px' }}>{m.text}</p>
            {m.sources?.length > 0 && (
              <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--mute)' }}>
                Sources: {m.sources.map((s, j) => s.title).join(', ')}
              </div>
            )}
          </div>
        ))}
        {busy && <p className="fine">Thinking carefully…</p>}
      </div>

      <form onSubmit={send} style={{ display: 'flex', gap: '8px' }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a technical question…"
          style={{ flex: 1 }}
        />
        <button type="submit" className="btn solid" disabled={busy || !input.trim()}>
          <Send size={18} />
        </button>
      </form>
    </div>
  </div>;
}

function MenstrualPage() {
  const [trackingEnabled, setTrackingEnabled] = useState(false);
  const [cycles, setCycles] = useState([]);
  const [symptoms, setSymptoms] = useState([]);
  const [estimate, setEstimate] = useState(null);

  useEffect(() => {
    api.listCycles().then(setCycles).catch(() => setCycles([]));
    api.listSymptoms().then(setSymptoms).catch(() => setSymptoms([]));
    api.estimateNextPeriod().then(setEstimate).catch(() => setEstimate(null));
  }, []);

  async function enableTracking() {
    setTrackingEnabled(true);
  }

  async function addCycle() {
    try {
      await api.createCycle({
        period_start_date: new Date().toISOString(),
        cycle_length_days: 28,
        notes: '',
        tracking_enabled: true
      });
      api.listCycles().then(setCycles);
    } catch {
      console.error('Could not add cycle');
    }
  }

  async function deleteAll() {
    if (confirm('Delete all menstrual health data? This cannot be undone.')) {
      try {
        await api.deleteAllMenstrualData();
        setCycles([]);
        setSymptoms([]);
        setEstimate(null);
      } catch {
        console.error('Could not delete data');
      }
    }
  }

  return <div className="rv">
    <h2>Women's Wellbeing</h2>
    <p className="lead">Optional, privacy-first menstrual health tracking and educational resources.</p>

    {!trackingEnabled ? (
      <div className="panel" style={{ background: 'var(--blush)', maxWidth: '560px' }}>
        <h3>Enable tracking</h3>
        <p className="fine">
          Cycle tracking is optional. If you enable it, your data will be stored locally. You can delete it at any time.
        </p>
        <button onClick={enableTracking} className="btn solid">Enable tracking</button>
      </div>
    ) : (
      <>
        <div className="grid">
          <div className="card">
            <div className="card-body">
              <h3>Next period estimate</h3>
              {estimate ? (
                <>
                  <p className="price">{new Date(estimate.estimate).toLocaleDateString()}</p>
                  <p className="fine">{estimate.disclaimer}</p>
                </>
              ) : (
                <p className="fine">Insufficient data to estimate</p>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-body">
              <h3>Cycles recorded</h3>
              <p className="price">{cycles.length}</p>
              <p className="fine">Add more cycles for better estimates</p>
              <button onClick={addCycle} className="btn" style={{ marginTop: '8px' }}>Add cycle</button>
            </div>
          </div>
        </div>

        <div className="panel" style={{ marginTop: '26px', background: 'var(--blush)' }}>
          <h3>Privacy controls</h3>
          <p className="fine">Your menstrual health data is stored separately from other features.</p>
          <button onClick={deleteAll} className="btn" style={{ borderColor: '#e07a7a', color: '#e07a7a' }}>
            Delete all menstrual data
          </button>
        </div>
      </>
    )}
  </div>;
}

function PrivacyPage() {
  return <div className="rv" style={{ maxWidth: '720px' }}>
    <h2>Privacy & Safety</h2>
    <p className="lead">Understanding how HERwell AI handles your data and protects your wellbeing.</p>

    <div className="panel">
      <h3>Data collection</h3>
      <p>This hackathon prototype uses demo data only and has no authentication. Do not enter sensitive personal information.</p>
    </div>

    <div className="panel" style={{ marginTop: '26px' }}>
      <h3>Not a medical service</h3>
      <p>HERwell AI is educational support only. It does not diagnose conditions, prescribe treatments, or replace professional care. If you may be in immediate danger, contact verified local emergency support.</p>
    </div>

    <div className="panel" style={{ marginTop: '26px' }}>
      <h3>Data deletion</h3>
      <p>In this demo, data is stored locally. Clear your browser data to remove all information.</p>
    </div>
  </div>;
}

function NotFound() {
  return <div className="rv" style={{ textAlign: 'center' }}>
    <h2>Page not found</h2>
    <p className="lead">The page you're looking for doesn't exist.</p>
    <a href="/" className="btn solid">Go home</a>
  </div>;
}

export default function App() {
  return <Routes>
    <Route path="/" element={<Layout><Dashboard /></Layout>} />
    <Route path="/mood" element={<Layout><MoodPage /></Layout>} />
    <Route path="/assistant" element={<Layout><AssistantPage /></Layout>} />
    <Route path="/technical" element={<Layout><TechnicalPage /></Layout>} />
    <Route path="/menstrual" element={<Layout><MenstrualPage /></Layout>} />
    <Route path="/planner" element={<Layout><PlannerPage /></Layout>} />
    <Route path="/calendar" element={<Layout><ProfessionalCalendar /></Layout>} />
    <Route path="/resources" element={<Layout><ResourcesPage /></Layout>} />
    <Route path="/breathing" element={<Layout><BreathingPage /></Layout>} />
    <Route path="/settings" element={<Layout><SettingsPage /></Layout>} />
    <Route path="/support" element={<Layout><SupportPage /></Layout>} />
    <Route path="/login" element={<Layout><LoginPage /></Layout>} />
    <Route path="/privacy" element={<Layout><PrivacyPage /></Layout>} />
    <Route path="*" element={<Layout><NotFound /></Layout>} />
  </Routes>;
}
