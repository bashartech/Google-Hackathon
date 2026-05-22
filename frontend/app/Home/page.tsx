/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import Header from '@/components/Navbar';
import Hero from '@/components/Hero';
import ArchitectureGraph from '@/components/ArchitectureGraph';
import ServiceExplorer from '@/components/ServiceExplorer';
// import ChatSandbox from './components/ChatSandbox';
// import MetricsDashboard from './components/MetricsDashboard';
import Footer from '@/components/Footer';

export default function App() {
  const [currentTab, setCurrentTab] = useState<'home' | 'chat' | 'dashboard'>('home');

  // Triggered when clicking "Book Instant" on a service card
  const handleImmediateBooking = (serviceType: string) => {
    setCurrentTab('chat');
    // We can simulate preselected inputs or have the user click a matching preset!
  };

  return (
    <div className="min-h-screen bg-bg-deep flex flex-col justify-between" id="app-root-container">
      <div>
        {/* Global Nav Header */}
        {/* <Header currentTab={currentTab} setCurrentTab={setCurrentTab} /> */}

        {/* Dynamic Nav View rendering */}
        <main className="w-full">
          {currentTab === 'home' && (
            <div id="core-space-view">
              <Hero 
                onAccessSandbox={() => setCurrentTab('chat')} 
                onAccessDashboard={() => setCurrentTab('dashboard')} 
              />
              
              {/* Interactive bento grid services */}
              <ServiceExplorer onSelectedService={handleImmediateBooking} />
              
              {/* Specialized workflow visualization nodes */}
              <ArchitectureGraph />
            </div>
          )}

         
        </main>
      </div>

      {/* Branded elements and Hackathon list indicators */}
      <Footer />
    </div>
  );
}
