import { useState, useEffect } from 'react';
import { Clock, CheckCircle2, UserCheck, AlertCircle, Loader2, RefreshCw } from 'lucide-react';
import { fetchMyRequests, getDeviceId } from '../lib/supabase';

export default function MyRequestsPage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadMyRequests();
    
    // Auto-refresh every 10 seconds
    const interval = setInterval(() => {
      loadMyRequests(true);
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const loadMyRequests = async (isAutoRefresh = false) => {
    if (!isAutoRefresh) {
      setLoading(true);
    } else {
      setRefreshing(true);
    }
    
    try {
      const deviceId = getDeviceId();
      console.log('Loading requests for device:', deviceId);
      
      const data = await fetchMyRequests();
      
      // Transform to match our UI format
      const transformed = data.map(req => ({
        ...req,
        need: req.description,
      }));
      
      setRequests(transformed);
    } catch (error) {
      console.error('Error loading requests:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-5 h-5 text-[#A7C4BC]" />;
      case 'in_progress':
        return <Clock className="w-5 h-5 text-[#E6CBA5]" />;
      case 'accepted':
        return <UserCheck className="w-5 h-5 text-[#A0C1D1]" />;
      default:
        return <AlertCircle className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'in_progress':
        return 'In Progress';
      case 'accepted':
        return 'Accepted';
      default:
        return 'Waiting';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-[#A7C4BC]/10 border-[#A7C4BC]/20';
      case 'in_progress':
        return 'bg-[#E6CBA5]/10 border-[#E6CBA5]/20';
      case 'accepted':
        return 'bg-[#A0C1D1]/10 border-[#A0C1D1]/20';
      default:
        return 'bg-muted/30 border-border/30';
    }
  };

  const getCategoryLabel = (category) => {
    const labels = {
      body: 'Body',
      emotion: 'Emotion',
      mind: 'Mind'
    };
    return labels[category] || category;
  };

  if (loading) {
    return (
      <div className="flex-1 px-6 py-8 pb-24 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  // Sort: waiting first, then accepted, in_progress, completed
  const sortedRequests = [...requests].sort((a, b) => {
    const statusOrder = { waiting: 0, accepted: 1, in_progress: 2, completed: 3 };
    return statusOrder[a.status || 'waiting'] - statusOrder[b.status || 'waiting'];
  });

  if (requests.length === 0) {
    return (
      <div className="flex-1 px-6 py-8 pb-24 flex flex-col items-center justify-center gap-4">
        <AlertCircle className="w-16 h-16 text-muted-foreground" />
        <p className="text-lg text-muted-foreground text-center">You haven't created any requests yet</p>
        <p className="text-base text-muted-foreground/70 text-center">Click "Need help?" to create a request</p>
      </div>
    );
  }

  return (
    <div data-testid="my-requests-page" className="flex-1 px-6 py-8 pb-24 flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl md:text-4xl font-semibold tracking-tight text-foreground">
          My Requests
        </h1>
        <button
          onClick={() => loadMyRequests()}
          disabled={refreshing}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="flex flex-col gap-3">
        {sortedRequests.map((request) => (
          <div
            key={request.id}
            className={`rounded-3xl p-5 border transition-all ${getStatusColor(request.status || 'waiting')}`}
            data-testid="request-item"
          >
            <div className="flex items-start justify-between gap-3 mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm font-medium text-muted-foreground">
                    {getCategoryLabel(request.category)}
                  </span>
                </div>
                <h3 className="text-lg font-medium text-foreground leading-snug">
                  {request.need}
                </h3>
              </div>
              <div className="flex flex-col items-end gap-1">
                {getStatusIcon(request.status || 'waiting')}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>{request.minutes} min</span>
                <span>{request.distance}</span>
              </div>
              <span 
                className="text-sm font-medium"
                data-testid="request-status"
                style={{ 
                  color: request.status === 'completed' ? '#2C4A40' : 
                         request.status === 'in_progress' ? '#8B6F47' :
                         request.status === 'accepted' ? '#2A4550' : '#8C867D'
                }}
              >
                {getStatusLabel(request.status || 'waiting')}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
