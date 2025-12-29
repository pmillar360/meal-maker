import React, { createContext, useContext, useEffect, useState } from 'react';
import { getCurrentUser, loginUser, logoutUser, registerUser } from '../services/UserService';
import { User } from '../services/TypeService';

interface AuthContextValue {
  user: User | null;
  isLoggedIn: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  register: (username: string, password: string) => Promise<boolean>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadUser = async () => {
      try {
        const current = await getCurrentUser();
        if (isMounted) {
          setUser(current);
        }
      } catch {
        if (isMounted) {
          setUser(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadUser();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (username: string, password: string) => {
    const success = await loginUser(username, password);
    if (success) {
      try {
        const current = await getCurrentUser();
        setUser(current);
      } catch {
        setUser(null);
      }
    }
    return success;
  };

  const register = async (username: string, password: string) => {
    const result = await registerUser(username, password);
    if (result) {
      try {
        const current = await getCurrentUser();
        setUser(current);
      } catch {
        setUser(null);
      }
      return true;
    }
    return false;
  };

  const logout = async () => {
    await logoutUser();
    setUser(null);
  };

  const value: AuthContextValue = {
    user,
    isLoggedIn: Boolean(user),
    isLoading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
};
