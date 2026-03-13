import { useEffect } from 'react';
import PhilosDashboard from './PhilosDashboard';

export default function TrustTestPage({ user, onLogout, onShowAuth }) {
  useEffect(() => {
    document.title = 'What is your trust score?';
    const setMeta = (name, content) => {
      let el = document.querySelector(`meta[name="${name}"]`) || document.querySelector(`meta[property="${name}"]`);
      if (!el) { el = document.createElement('meta'); el.setAttribute(name.startsWith('og:') ? 'property' : 'name', name); document.head.appendChild(el); }
      el.setAttribute('content', content);
    };
    setMeta('description', 'A simple experiment to measure trust with one question.');
    setMeta('og:title', 'What is your trust score?');
    setMeta('og:description', 'A simple experiment to measure trust with one question.');
    setMeta('og:type', 'website');
    setMeta('og:url', window.location.href);
    return () => { document.title = 'Philos'; };
  }, []);

  return (
    <div className="min-h-screen bg-background" data-testid="trust-test-page">
      <PhilosDashboard user={user} onLogout={onLogout} onShowAuth={onShowAuth} />
    </div>
  );
}
