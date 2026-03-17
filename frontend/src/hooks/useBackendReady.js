/**
 * BackendReady — silent backend wake + action queue.
 *
 * On app load, pings /api/health every 2.5s until the backend responds.
 * While waking: isReady=false. After first successful ping: isReady=true.
 * Queued actions (via enqueue) are flushed automatically when ready.
 * User never sees backend state — no technical messages.
 */
import { useState, useEffect, useRef, useCallback, createContext, useContext } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const PING_INTERVAL = 2500;
const PING_TIMEOUT = 4000;

const BackendContext = createContext({ isReady: false, enqueue: () => {} });

export function useBackendReady() {
  return useContext(BackendContext);
}

export function BackendReadyProvider({ children }) {
  const [isReady, setIsReady] = useState(false);
  const queue = useRef([]);
  const intervalRef = useRef(null);
  const mountedRef = useRef(true);

  const ping = useCallback(async () => {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), PING_TIMEOUT);
      const res = await fetch(`${API_URL}/api/health`, { signal: controller.signal });
      clearTimeout(timeout);
      if (res.ok && mountedRef.current) {
        setIsReady(true);
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
        // Flush queued actions
        const pending = [...queue.current];
        queue.current = [];
        for (const fn of pending) {
          try { await fn(); } catch {}
        }
      }
    } catch {
      // Silent — retry on next interval
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    ping(); // immediate first attempt
    intervalRef.current = setInterval(ping, PING_INTERVAL);
    return () => {
      mountedRef.current = false;
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [ping]);

  const enqueue = useCallback((fn) => {
    if (isReady) {
      // Already ready — execute immediately
      try { fn(); } catch {}
    } else {
      queue.current.push(fn);
    }
  }, [isReady]);

  return (
    <BackendContext.Provider value={{ isReady, enqueue }}>
      {children}
    </BackendContext.Provider>
  );
}
