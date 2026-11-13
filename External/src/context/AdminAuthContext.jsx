import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient, getAdminToken, getAdminUser, clearAdminSession } from '../api/client';

const AdminAuthContext = createContext(null);

export function AdminAuthProvider({ children }) {
  const [token, setToken] = useState(() => getAdminToken());
  const [user, setUser] = useState(() => getAdminUser());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const savedToken = getAdminToken();
    const savedUser = getAdminUser();
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(savedUser);
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    const res = await apiClient.login(username, password);
    setToken(res.token);
    setUser(res.user);
    return res;
  };

  const logout = async () => {
    await apiClient.logout();
    setToken(null);
    setUser(null);
  };

  const isSuperAdmin = Boolean(
    user?.isSuperAdmin ||
    user?.is_superadmin ||
    user?.role?.is_superadmin ||
    user?.userType === 'superadmin'
  );

  const isAuthenticated = Boolean(token && isSuperAdmin);

  return (
    <AdminAuthContext.Provider
      value={{
        token,
        user,
        loading,
        isAuthenticated,
        isSuperAdmin,
        login,
        logout,
      }}
    >
      {children}
    </AdminAuthContext.Provider>
  );
}

export function useAdminAuth() {
  const context = useContext(AdminAuthContext);
  if (!context) {
    throw new Error('useAdminAuth must be used within an AdminAuthProvider');
  }
  return context;
}

