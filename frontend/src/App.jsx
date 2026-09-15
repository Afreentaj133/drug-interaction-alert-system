import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import CheckerPage from './pages/CheckerPage';
import HistoryPage from './pages/HistoryPage';
import DashboardPage from './pages/DashboardPage';
import DrugsPage from './pages/DrugsPage';
import AboutPage from './pages/AboutPage';
import DisclaimerPage from './pages/DisclaimerPage';

export default function App() {
  const [activePage, setActivePage] = useState('landing');

  // Scroll to top whenever page changes
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [activePage]);

  const renderContent = () => {
    switch (activePage) {
      case 'landing':
        return <LandingPage setActivePage={setActivePage} />;
      case 'checker':
        return <CheckerPage />;
      case 'history':
        return <HistoryPage />;
      case 'dashboard':
        return <DashboardPage />;
      case 'drugs':
        return <DrugsPage />;
      case 'about':
        return <AboutPage />;
      case 'disclaimer':
        return <DisclaimerPage />;
      default:
        return <LandingPage setActivePage={setActivePage} />;
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar activePage={activePage} setActivePage={setActivePage} />
      <main style={{ flex: 1 }}>
        {renderContent()}
      </main>
      <Footer setActivePage={setActivePage} />
    </div>
  );
}
