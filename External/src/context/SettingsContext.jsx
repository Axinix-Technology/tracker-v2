import React, { createContext, useContext, useState } from 'react';

const defaultSettings = {
  phone: '+91 98765 43210',
  email: 'contact@axinix.tech',
  address: 'Level 4, Cyber Towers, Tech Corridor, Bangalore, India',
  wa: 'https://wa.me/919876543210',
  fb: 'https://facebook.com/axinixtech',
  ig: 'https://instagram.com/axinixtech',
  li: 'https://linkedin.com/company/axinix-technologies',
  yt: 'https://youtube.com/@axinixtechnologies',
  map: 'https://maps.google.com',
};

const SettingsContext = createContext();

export function SettingsProvider({ children }) {
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('axinix_settings');
    return saved ? JSON.parse(saved) : defaultSettings;
  });

  const updateSettings = (newSettings) => {
    setSettings(prev => {
      const updated = { ...prev, ...newSettings };
      localStorage.setItem('axinix_settings', JSON.stringify(updated));
      return updated;
    });
  };

  return (
    <SettingsContext.Provider value={{ settings, updateSettings }}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
}

