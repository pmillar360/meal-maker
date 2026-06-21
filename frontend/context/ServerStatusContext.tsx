import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { checkServerHealth } from '../services/apiService';

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

  useEffect(() => {
    const handleServerDown = () => {
      setServerStatus((currentStatus) => {
        if (currentStatus === 'asleep' || currentStatus === 'ready') {
          return currentStatus;
        }
        return 'asleep';
      });
    };

    window.addEventListener('server:down', handleServerDown);
    return () => {
      window.removeEventListener('server:down', handleServerDown);
    };
  }, []);

  useEffect(() => {
    if (serverStatus !== 'asleep') {
      return;
    }

    let cancelled = false;

    const poll = async () => {
      const awake = await checkServerHealth();
      if (cancelled) {
        return;
      }

      if (awake) {
        setServerStatus('ready');
      } else {
        pollingRef.current = setTimeout(poll, POLL_INTERVAL_MS);
      }
    };

    poll();

    return () => {
      cancelled = true;
      if (pollingRef.current) {
        clearTimeout(pollingRef.current);
      }
    };
  }, [serverStatus]);

  useEffect(() => {
    if (serverStatus !== 'ready') {
      return;
    }

    const readyTimeout = setTimeout(() => {
      setServerStatus('awake');
    }, READY_DISPLAY_MS);

    return () => clearTimeout(readyTimeout);
  }, [serverStatus]);

  return (
    <ServerStatusContext.Provider value={{ serverStatus }}>
      {children}
    </ServerStatusContext.Provider>
  );
}

export function useServerStatus() {
  return useContext(ServerStatusContext);
}
