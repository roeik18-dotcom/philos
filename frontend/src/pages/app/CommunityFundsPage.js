import { useState, useEffect } from 'react';
import { Loader2, DollarSign, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

function formatCurrency(n) {
  return '$' + n.toLocaleString();
}

export default function CommunityFundsPage() {
  const [funds, setFunds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);
  const [txns, setTxns] = useState({});

  useEffect(() => {
    const fetchFunds = async () => {
      try {
        const res = await fetch(`${API_URL}/api/community-funds`);
        const d = await res.json();
        if (d.success) setFunds(d.funds);
      } catch (err) {
        console.error('Funds fetch error:', err);
      }
      setLoading(false);
    };
    fetchFunds();
  }, []);

  const toggleExpand = async (community) => {
    if (expanded === community) { setExpanded(null); return; }
    setExpanded(community);
    if (!txns[community]) {
      try {
        const res = await fetch(`${API_URL}/api/community-funds/${encodeURIComponent(community)}`);
        const d = await res.json();
        if (d.success) setTxns(prev => ({ ...prev, [community]: d.transactions }));
      } catch (err) {
        console.error('Txns fetch error:', err);
      }
    }
  };

  if (loading) {
    return (
      <div className="funds-page" data-testid="community-funds-page">
        <div className="feed-loading"><Loader2 className="w-5 h-5 animate-spin" /><span>Loading funds...</span></div>
      </div>
    );
  }

  const totalRaised = funds.reduce((s, f) => s + (f.total_raised || 0), 0);
  const totalDistributed = funds.reduce((s, f) => s + (f.total_distributed || 0), 0);

  return (
    <div className="funds-page" data-testid="community-funds-page">
      <div className="feed-header">
        <h1 className="feed-title" data-testid="funds-title">Community Funds</h1>
        <p className="feed-subtitle">Transparent financial visibility for every community.</p>
      </div>

      {/* Summary stats */}
      <div className="funds-summary" data-testid="funds-summary">
        <div className="funds-stat">
          <TrendingUp className="w-5 h-5" style={{ color: '#10b981' }} />
          <div>
            <div className="funds-stat-value" data-testid="total-raised">{formatCurrency(totalRaised)}</div>
            <div className="funds-stat-label">Total Raised</div>
          </div>
        </div>
        <div className="funds-stat">
          <TrendingDown className="w-5 h-5" style={{ color: '#00d4ff' }} />
          <div>
            <div className="funds-stat-value" data-testid="total-distributed">{formatCurrency(totalDistributed)}</div>
            <div className="funds-stat-label">Distributed</div>
          </div>
        </div>
        <div className="funds-stat">
          <DollarSign className="w-5 h-5" style={{ color: '#f59e0b' }} />
          <div>
            <div className="funds-stat-value" data-testid="total-balance">{formatCurrency(totalRaised - totalDistributed)}</div>
            <div className="funds-stat-label">Total Balance</div>
          </div>
        </div>
      </div>

      {/* Fund cards */}
      <div className="funds-list" data-testid="funds-list">
        {funds.map((f, i) => (
          <div key={f.community} className="fund-card" data-testid={`fund-card-${i}`}>
            <div className="fund-card-header" onClick={() => toggleExpand(f.community)} style={{ cursor: 'pointer' }}>
              <div className="fund-card-rank">#{i + 1}</div>
              <div className="fund-card-info">
                <h3 className="fund-card-name" data-testid={`fund-name-${i}`}>{f.community}</h3>
                <div className="fund-card-bars">
                  <div className="fund-bar-group">
                    <span className="fund-bar-label">Raised</span>
                    <div className="fund-bar"><div className="fund-bar-fill raised" style={{ width: `${(f.total_raised / totalRaised) * 100}%` }} /></div>
                    <span className="fund-bar-value">{formatCurrency(f.total_raised)}</span>
                  </div>
                  <div className="fund-bar-group">
                    <span className="fund-bar-label">Distributed</span>
                    <div className="fund-bar"><div className="fund-bar-fill distributed" style={{ width: `${(f.total_distributed / totalRaised) * 100}%` }} /></div>
                    <span className="fund-bar-value">{formatCurrency(f.total_distributed)}</span>
                  </div>
                </div>
              </div>
              <div className="fund-card-balance" data-testid={`fund-balance-${i}`}>
                <div className="fund-balance-value">{formatCurrency(f.current_balance)}</div>
                <div className="fund-balance-label">Balance</div>
              </div>
            </div>

            {/* Transactions (expandable) */}
            {expanded === f.community && txns[f.community] && (
              <div className="fund-txns" data-testid={`fund-txns-${i}`}>
                {txns[f.community].map((t, j) => (
                  <div key={j} className="fund-txn-row">
                    {t.amount > 0 ? (
                      <ArrowUpRight className="w-3.5 h-3.5" style={{ color: '#10b981' }} />
                    ) : (
                      <ArrowDownRight className="w-3.5 h-3.5" style={{ color: '#f43f5e' }} />
                    )}
                    <span className="fund-txn-desc">{t.description}</span>
                    <span className="fund-txn-type">{t.type}</span>
                    <span className={`fund-txn-amount ${t.amount > 0 ? 'positive' : 'negative'}`}>
                      {t.amount > 0 ? '+' : ''}{formatCurrency(Math.abs(t.amount))}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
