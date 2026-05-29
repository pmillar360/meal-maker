import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { resolveApiUrl } from '../services/apiService';

const API_URL = resolveApiUrl();

const POLL_INTERVAL_MS = 5000;
const READY_DISPLAY_MS = 1500;

type ServerStatus = 'awake' | 'asleep' | 'ready';

interface ServerStatusContextType {
  serverStatus: ServerStatus;
}

const ServerStatusContext = createContext<ServerStatusContextType>({ serverStatus: 'awake' });

export function ServerStatusProvider({ children }: { children: React.ReactNode }) {
  const [serverStatus, setServerStatus] = useState<ServerStatus>('awake');
  const pollingRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isPollingRef = useRef(false);
  const wentAsleepRef = useRef(false);

  const checkHealth = async (): Promise<boolean> => {
    try {
      await axios.get(`${API_URL}`, { timeout: 8000, withCredentials: false });
      return true;
    } catch (error) {
      if (axios.isAxiosError(error) && !error.response) {
        return false;
      }
      // Got any HTTP response — server is alive
      return true;
    }
  };

  const startPolling = useCallback(() => {
    if (isPollingRef.current) return;
    isPollingRef.current = true;

    const poll = async () => {
      const awake = await checkHealth();
      if (awake) {
        isPollingRef.current = false;
        setServerStatus('ready');
        setTimeout(() => {
          if (typeof window !== 'undefined') window.location.reload();
        }, READY_DISPLAY_MS);
      } else {
        pollingRef.current = setTimeout(poll, POLL_INTERVAL_MS);
      }
    };

    poll();
  }, []);

  useEffect(() => {
    const handleServerDown = () => {
      if (wentAsleepRef.current) return;
      wentAsleepRef.current = true;
      setServerStatus('asleep');
      startPolling();
    };

    window.addEventListener('server:down', handleServerDown);
    return () => {
      window.removeEventListener('server:down', handleServerDown);
      if (pollingRef.current) clearTimeout(pollingRef.current);
    };
  }, [startPolling]);

  return (
    <ServerStatusContext.Provider value={{ serverStatus }}>
      {children}
    </ServerStatusContext.Provider>
  );
}

export function useServerStatus() {
  return useContext(ServerStatusContext);
}
