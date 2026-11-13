import React, { Suspense } from 'react';
import { useRoutes, Navigate } from 'react-router-dom';
import routes from '~react-pages';
import { MainLayout } from './layouts/MainLayout';

export function App() {
  // Wrap auto-generated filesystem routes with MainLayout
  const element = useRoutes([
    {
      element: <MainLayout />,
      children: [
        ...routes,
        // Common convenience & legacy redirects
        { path: 'home', element: <Navigate to="/" replace /> },
        { path: 'contact/create', element: <Navigate to="/contact" replace /> },
        { path: 'demo/*', element: <Navigate to="/contact" replace /> },
        { path: 'cart', element: <Navigate to="/products" replace /> },
        { path: 'checkout', element: <Navigate to="/products" replace /> },
        { path: 'portfolio/*', element: <Navigate to="/solutions" replace /> },
        { path: 'insights/*', element: <Navigate to="/about" replace /> },
        { path: 'customer-account', element: <Navigate to="/contact" replace /> },
        { path: 'delivery', element: <Navigate to="/contact" replace /> },
        { path: 'search', element: <Navigate to="/solutions" replace /> },
        { path: 'login', element: <Navigate to="/" replace /> },
      ],
    },
  ]);

  return (
    <Suspense fallback={<div className="min-h-screen bg-[#061126]" />}>
      {element}
    </Suspense>
  );
}

export default App;
