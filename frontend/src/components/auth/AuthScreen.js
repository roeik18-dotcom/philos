import { useState } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function AuthScreen({ onAuthSuccess, onSkip }) {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Pre-fill invite code from URL or pending invite
  useState(() => {
    const path = window.location.pathname;
    const match = path.match(/^\/invite\/([a-zA-Z0-9-]+)$/);
    if (match) {
      setInviteCode(match[1]);
      setMode('register');
    } else if (path === '/join') {
      const params = new URLSearchParams(window.location.search);
      const code = params.get('invite');
      if (code) { setInviteCode(code); setMode('register'); }
    }
    // Also check pending invite from InvitePage
    const pending = localStorage.getItem('philos_pending_invite');
    if (pending && !inviteCode) {
      setInviteCode(pending);
      setMode('register');
    }
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (!email || !password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    if (mode === 'register' && password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      setLoading(false);
      return;
    }

    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const body = mode === 'login'
        ? { email, password }
        : { email, password, ...(inviteCode ? { invite_code: inviteCode } : {}) };

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      const data = await response.json();

      if (data.success) {
        // Store token
        localStorage.setItem('philos_auth_token', data.token);
        localStorage.setItem('philos_user', JSON.stringify(data.user));
        
        // Migrate anonymous data if exists
        const anonymousUserId = localStorage.getItem('philos_user_id');
        if (anonymousUserId) {
          try {
            await fetch(`${API_URL}/api/auth/migrate-data?anonymous_user_id=${anonymousUserId}`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${data.token}`,
              },
            });
            // Update local user_id to authenticated user_id
            localStorage.setItem('philos_user_id', data.user.id);
          } catch (migrationError) {
            console.error('Migration error:', migrationError);
          }
        } else {
          localStorage.setItem('philos_user_id', data.user.id);
        }
        
        onAuthSuccess(data.user);
        // Clear pending invite
        localStorage.removeItem('philos_pending_invite');
      } else {
        setError(data.message || 'An error occurred');
      }
    } catch (err) {
      console.error('Auth error:', err);
      setError('Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-yellow-50 flex items-center justify-center p-4"
    >
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Philos Orientation</h1>
          <p className="text-gray-600">Mental navigation system</p>
        </div>

        {/* Auth Card */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-xl p-8 border border-white/50">
          {/* Tabs */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => { setMode('login'); setError(''); }}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                mode === 'login'
                  ? 'bg-amber-500 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              data-testid="auth-login-tab"
            >
              Sign In
            </button>
            <button
              onClick={() => { setMode('register'); setError(''); }}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all ${
                mode === 'register'
                  ? 'bg-amber-500 text-white shadow-md'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              data-testid="auth-register-tab"
            >
              Sign Up
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-200 outline-none transition-all text-right"
                placeholder="your@email.com"
                data-testid="auth-email-input"
                dir="ltr"
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-200 outline-none transition-all"
                placeholder="••••••••"
                data-testid="auth-password-input"
              />
            </div>

            {/* Confirm Password (Register only) */}
            {mode === 'register' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-200 outline-none transition-all"
                  placeholder="••••••••"
                  data-testid="auth-confirm-password-input"
                />
              </div>
            )}

            {/* Invite Code (Register only, optional) */}
            {mode === 'register' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Invite Code <span className="text-gray-400 font-normal">(optional)</span>
                </label>
                <input
                  type="text"
                  value={inviteCode}
                  onChange={(e) => setInviteCode(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-violet-400 focus:ring-2 focus:ring-violet-200 outline-none transition-all"
                  placeholder="PH-XXXX"
                  data-testid="auth-invite-code-input"
                  dir="ltr"
                />
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl text-sm">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 px-4 rounded-xl font-medium transition-all ${
                loading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-amber-500 hover:bg-amber-600 text-white shadow-md hover:shadow-lg'
              }`}
              data-testid="auth-submit-btn"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Processing...
                </span>
              ) : mode === 'login' ? 'Sign In' : 'Sign Up'}
            </button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-4 my-6">
            <div className="flex-1 h-px bg-gray-200"></div>
            <span className="text-sm text-gray-400">or</span>
            <div className="flex-1 h-px bg-gray-200"></div>
          </div>

          {/* Skip Button */}
          <button
            onClick={onSkip}
            className="w-full py-3 px-4 rounded-xl font-medium bg-gray-100 hover:bg-gray-200 text-gray-600 transition-all"
            data-testid="auth-skip-btn"
          >
            Continue without account
          </button>

          {/* Info Text */}
          <p className="text-xs text-gray-400 text-center mt-4">
            {mode === 'register' 
              ? 'By signing up you agree to the Terms of Service' 
              : 'Your data will be saved in the cloud and synced across devices'}
          </p>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-500 text-sm mt-6">
          © 2026 Philos Orientation
        </p>
      </div>
    </div>
  );
}
