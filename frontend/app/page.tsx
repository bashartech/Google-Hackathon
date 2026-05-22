/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

'use client';

import { Variants } from 'framer-motion';

import { usePathname } from 'next/navigation';
import { AnimatePresence, motion } from 'framer-motion';

import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import React, { useState } from 'react';

import HomePage from '@/components/HomePage';
import ChatPage from '@/components/ChatPage';
import DashboardPage from '@/components/DashboardPage';

const pageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
    scale: 0.98,
    filter: 'blur(8px)',
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    filter: 'blur(0px)',
    transition: {
      duration: 0.5,
      ease: [0.22, 1, 0.36, 1],
    },
  },
  exit: {
    opacity: 0,
    y: -10,
    scale: 0.98,
    filter: 'blur(8px)',
    transition: {
      duration: 0.35,
      ease: [0.4, 0, 1, 1],
    },
  },
};

export default function App() {
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const renderPage = () => {
    switch (pathname) {
      case '/chat':
        return <ChatPage />;
      case '/dashboard':
        return <DashboardPage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <div className="relative flex h-screen overflow-hidden bg-[#070B14] text-slate-100 antialiased">
      {/* Background Effects */}
      <div className="absolute inset-0 -z-10 overflow-hidden">
        {/* Gradient Orbs */}
        <div className="absolute left-[-10%] top-[-10%] h-[500px] w-[500px] rounded-full bg-violet-700/20 blur-3xl" />
        <div className="absolute bottom-[-20%] right-[-10%] h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-3xl" />

        {/* Grid Overlay */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px)
            `,
            backgroundSize: '40px 40px',
          }}
        />

        {/* Noise Texture */}
        <div className="absolute inset-0 bg-[url('/noise.png')] opacity-[0.03]" />
      </div>

      {/* Sidebar for desktop */}
      {/* <aside className="relative z-20 hidden lg:flex border-r border-white/10 bg-white/[0.03] backdrop-blur-2xl">
        <Sidebar />
      </aside> */}
      {/* Sidebar for mobile */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main Layout */}
      <div className="relative flex min-w-0 flex-1 flex-col">
        {/* Top Navbar */}
        <header className="sticky top-0 z-30 border-b border-white/10 bg-[#0B1120]/70 backdrop-blur-2xl">
          <Navbar onMenuClick={() => setSidebarOpen(true)} />
        </header>

        {/* Main Content */}
        <main className="relative flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar">
          <AnimatePresence mode="wait">
            <motion.div
              key={pathname}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
              className="min-h-full"
            >
              {renderPage()}
            </motion.div>
          </AnimatePresence>
        </main>

        {/* Ambient Bottom Glow */}
        <div className="pointer-events-none absolute bottom-0 left-1/2 h-40 w-[70%] -translate-x-1/2 rounded-full bg-violet-600/10 blur-3xl" />
      </div>
    </div>
  );
}