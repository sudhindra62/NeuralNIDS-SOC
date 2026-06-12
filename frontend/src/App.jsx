import React, { useEffect } from 'react';
import Dashboard from './components/Dashboard';
import { wsManager } from './services/websocket';

function App() {
  return (
    <div className="min-h-screen">
      <Dashboard />
    </div>
  );
}

export default App;
