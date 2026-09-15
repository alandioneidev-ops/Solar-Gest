import { StrictMode, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:3333/api';

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`${apiUrl}/dashboard`)
      .then((response) => {
        if (!response.ok) throw new Error('Não foi possível carregar o dashboard.');
        return response.json();
      })
      .then(setDashboard)
      .catch((reason) => setError(reason.message));
  }, []);

  const metric = (label, value) => (
    <article className="metric" key={label}>
      <span>{label}</span>
      <strong>{dashboard?.[value] ?? '...'}</strong>
    </article>
  );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark"><i className="sun" /><i className="panel" /></span> Solar<span>Gest</span></div>
        <p className="nav-label">Operação</p>
        <nav><a className="active" href="#dashboard">Dashboard</a><a href="#comercial">Comercial</a><a href="#engenharia">Engenharia</a><a href="#financeiro">Financeiro</a><a href="#gestao">Gestão</a></nav>
      </aside>
      <main className="content">
        <header className="topbar"><div><p className="eyebrow">Visão geral</p><h1>Dashboard</h1><p className="subtitle">Acompanhe a operação do Solar Gest.</p></div><div className="account"><span className="avatar">D</span><span><b>Demonstração</b><small>Administrador</small></span></div></header>
        {error && <p className="error">{error} Inicie a API Node em localhost:3333.</p>}
        <section className="metrics">{metric('Clientes', 'clientes')}{metric('Leads', 'leads')}{metric('Projetos', 'projetos')}{metric('Atendimentos abertos', 'atendimentosAbertos')}</section>
        <section className="panel"><h2>Próxima etapa da migração</h2><p className="subtitle">Esta interface React já consome a API Node. Os módulos Django serão transferidos gradualmente para endpoints reais.</p></section>
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<StrictMode><App /></StrictMode>);
