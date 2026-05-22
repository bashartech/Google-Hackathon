"use client";

import React, { useState } from 'react';
import Hero from '@/components/Hero';
import ArchitectureGraph from '@/components/ArchitectureGraph';
import ServiceExplorer from '@/components/ServiceExplorer';
import Footer from '@/components/Footer';

export default function HomePage() {
  const [currentTab, setCurrentTab] = useState<'home' | 'chat' | 'dashboard'>('home');

  // Triggered when clicking "Book Instant" on a service card
  const handleImmediateBooking = (serviceType: string) => {
    // Navigate to chat
    window.location.pathname = '/chat';
  };

  return (
    <div className="min-h-screen bg-bg-deep flex flex-col justify-between" id="app-root-container">
      <div>
        <main className="w-full">
          <div id="core-space-view">
            <Hero 
              onAccessSandbox={() => { window.location.pathname = '/chat'; }} 
              onAccessDashboard={() => { window.location.pathname = '/dashboard'; }} 
            />
            
            {/* Interactive bento grid services */}
            <ServiceExplorer onSelectedService={handleImmediateBooking} />
            
            {/* Specialized workflow visualization nodes */}
            <ArchitectureGraph />
          </div>
        </main>
      </div>

      {/* Branded elements and Hackathon list indicators */}
      <Footer />
    </div>
  );
}
