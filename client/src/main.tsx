import React, { useState, type FormEvent } from 'react';
import ReactDOM from 'react-dom/client';
import { ShieldCheck, KeyRound, UserRound, LogOut } from 'lucide-react';
import './style.css';

type User = { id: number; email: string; is_active: boolean };
type Token = { access_token: string; expires_in: number; token_type: string };
const apiUrl = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000';

function App() {
  const [mode, setMode] = useState<'login' | 'register'>('register');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [token, setToken] = useState(''); // Memory only. Do not store credentials or JWT in localStorage.
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError(''); setNotice('');
    try {
      const response = await fetch(`${apiUrl}/auth/${mode === 'login' ? 'login' : 'register'}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!response.ok) { throw new Error(response.status === 409 ? 'That email is already registered.' : response.status === 401 ? 'Invalid email or password.' : `Request failed (${response.status}). Check the email and password.`); }
      if (mode === 'register') { setMode('login'); setPassword(''); setNotice('Account created. You can now sign in.'); }
      else {
        const data = (await response.json()) as Token;
        const me = await fetch(`${apiUrl}/auth/me`, { headers: { Authorization: `Bearer ${data.access_token}` } });
        if (!me.ok) throw new Error('Token was issued but profile fetch failed.');
        setUser((await me.json()) as User); setToken(data.access_token); setPassword('');
      }
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Connection failed.'); }
    finally { setBusy(false); }
  }

  const logout = () => { setToken(''); setUser(null); setPassword(''); setNotice('Signed out locally.'); };
  return <main className="shell"><header><div className="brand"><span className="logo"><KeyRound size={23}/></span><div><strong>AuthKit</strong><small>Full-stack portfolio project</small></div></div><span className="pill">React + FastAPI + PostgreSQL</span></header>
    <div className="layout"><section className="intro"><div className="eyebrow">END-TO-END ENGINEERING</div><h1>Authentication,<br/><em>built with intent.</em></h1><p>Register, sign in and fetch a protected user profile with typed React, validated FastAPI endpoints and PostgreSQL persistence.</p><div className="feature"><ShieldCheck size={20}/> Argon2 password hashing and JWT verification</div><div className="feature"><UserRound size={20}/> Strict validation and database uniqueness</div><p className="note">Local portfolio demonstration. Do not use real passwords.</p></section>
    <section className="panel">{user && token ? <><div className="round"><ShieldCheck size={27}/></div><h2>You're signed in</h2><p>Protected profile loaded from <code>GET /auth/me</code>.</p><div className="profile"><span>User #{user.id}</span><strong>{user.email}</strong><span>Status: {user.is_active ? 'Active' : 'Inactive'}</span></div><button onClick={logout}><LogOut size={17}/> Sign out</button></> : <><div className="round"><KeyRound size={27}/></div><h2>{mode === 'register' ? 'Create an account' : 'Welcome back'}</h2><p>{mode === 'register' ? 'Use a sample email and a password of at least 12 characters.' : 'Enter the credentials you created in this demo.'}</p><div className="tabs" role="group" aria-label="Authentication mode"><button type="button" aria-pressed={mode==='register'} onClick={() => {setMode('register');setNotice('');setError('');}}>Register</button><button type="button" aria-pressed={mode==='login'} onClick={() => {setMode('login');setNotice('');setError('');}}>Sign in</button></div><form onSubmit={submit}><label htmlFor="email">Email address</label><input id="email" type="email" autoComplete="email" required value={email} onChange={e=>setEmail(e.target.value)} placeholder="demo@example.com" /><label htmlFor="password">Password</label><input id="password" type="password" autoComplete={mode==='register'?'new-password':'current-password'} minLength={mode==='register'?12:1} required value={password} onChange={e=>setPassword(e.target.value)} placeholder="At least 12 characters" /><button type="submit" disabled={busy}>{busy?'Sending…':mode==='register'?'Create account':'Sign in'}</button></form>{error && <p role="alert" className="error">{error}</p>}{notice && <p role="status" className="notice">{notice}</p>}</> }</section></div><footer>Local developer demo · The access token is held in memory, not browser storage.</footer>
  </main>;
}

ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
