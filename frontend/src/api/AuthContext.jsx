import { createContext, useContext, useState, useEffect } from 'react';
import { apiGet, apiPost } from './client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  // On mount: fetch CSRF cookie then check auth status
  useEffect(() => {
    apiGet('/api/csrf/')
      .then(() => apiGet('/api/auth/status/'))
      .then(data => {
        if (data.is_authenticated) setUser(data.user);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (username, password) => {
    const data = await apiPost('/api/login/', { username, password });
    if (data.ok) setUser(data.user);
    return data;
  };

  const signup = async (username, email, password, confirm_password) => {
    const data = await apiPost('/api/signup/', { username, email, password, confirm_password });
    if (data.ok) setUser(data.user);
    return data;
  };

  const logout = async () => {
    await apiPost('/api/logout/', {});
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
