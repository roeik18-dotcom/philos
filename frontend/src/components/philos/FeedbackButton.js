import { useState } from 'react';
import { MessageSquareWarning, X, Send, Loader2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function FeedbackButton({ userId, currentTab }) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState('');
  const [type, setType] = useState('confusion');
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const effectiveUserId = userId || localStorage.getItem('philos_user_id');

  const handleSubmit = async () => {
    if (!text.trim()) return;
    setSending(true);
    try {
      await fetch(`${API_URL}/api/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: effectiveUserId,
          text: text.trim(),
          page: currentTab || 'unknown',
          type
        })
      });
      setSent(true);
      setTimeout(() => { setOpen(false); setSent(false); setText(''); }, 1500);
    } catch (e) {}
    finally { setSending(false); }
  };

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-20 left-4 z-40 w-10 h-10 bg-white border border-gray-200 rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 hover:shadow-xl transition-all active:scale-95"
        data-testid="feedback-floating-btn"
        title="Send feedback"
      >
        <MessageSquareWarning className="w-4 h-4 text-gray-500" />
      </button>

      {/* Modal */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/30 backdrop-blur-sm p-4" onClick={() => setOpen(false)}>
          <div
            className="bg-white rounded-2xl shadow-2xl p-5 w-full max-w-sm"
            dir="rtl"
            onClick={e => e.stopPropagation()}
            data-testid="feedback-modal"
          >
            {sent ? (
              <div className="text-center py-6" data-testid="feedback-success">
                <p className="text-lg font-bold text-green-600 mb-1">תודה!</p>
                <p className="text-xs text-gray-400">המשוב שלך התקבל</p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-gray-800">שלח משוב</h3>
                  <button onClick={() => setOpen(false)} className="text-gray-300 hover:text-gray-500" data-testid="feedback-close">
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Type selector */}
                <div className="flex gap-2 mb-3" data-testid="feedback-type-selector">
                  {[
                    { id: 'confusion', label: 'בלבול', color: 'orange' },
                    { id: 'improvement', label: 'הצעת שיפור', color: 'blue' },
                    { id: 'bug', label: 'באג', color: 'red' }
                  ].map(t => (
                    <button
                      key={t.id}
                      onClick={() => setType(t.id)}
                      className={`flex-1 py-1.5 text-[10px] font-medium rounded-lg border transition-all ${
                        type === t.id
                          ? `bg-${t.color}-50 border-${t.color}-200 text-${t.color}-600`
                          : 'bg-white border-gray-100 text-gray-400'
                      }`}
                      style={type === t.id ? {
                        backgroundColor: t.color === 'orange' ? '#fff7ed' : t.color === 'blue' ? '#eff6ff' : '#fef2f2',
                        borderColor: t.color === 'orange' ? '#fed7aa' : t.color === 'blue' ? '#bfdbfe' : '#fecaca',
                        color: t.color === 'orange' ? '#ea580c' : t.color === 'blue' ? '#2563eb' : '#dc2626'
                      } : {}}
                      data-testid={`feedback-type-${t.id}`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>

                {/* Text input */}
                <textarea
                  value={text}
                  onChange={e => setText(e.target.value)}
                  placeholder="ספר לנו מה קרה..."
                  className="w-full h-24 p-3 text-sm border border-gray-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-indigo-200 focus:border-indigo-300"
                  data-testid="feedback-text-input"
                />

                {/* Submit */}
                <button
                  onClick={handleSubmit}
                  disabled={!text.trim() || sending}
                  className="w-full mt-3 py-2.5 bg-gray-900 text-white text-xs font-medium rounded-xl flex items-center justify-center gap-1.5 hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                  data-testid="feedback-submit-btn"
                >
                  {sending ? <Loader2 className="w-3 h-3 animate-spin" /> : <><Send className="w-3 h-3" />שלח משוב</>}
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
