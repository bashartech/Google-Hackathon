"use client";
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ChatWindow, { Message } from '@/components/ChatWindow';
import WorkflowTimeline from '@/components/WorkflowTimeline';
import AgentReasoning from '@/components/AgentReasoning';
import { cn } from '@/lib/utils';
import { Search, Plus, Hash, Settings, Users, Ghost } from 'lucide-react';
import Sidebar from '@/components/Sidebar';

interface WorkflowStep {
  agent: string;
  stage: string;
  status: 'in_progress' | 'completed' | 'failed' | 'pending';
  timestamp: string;
  action: string;
  error?: string;
}

export default function ChatPage({ sidebarOpen, setSidebarOpen }: { sidebarOpen?: boolean, setSidebarOpen?: (open: boolean) => void }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [workflow, setWorkflow] = useState<WorkflowStep[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const handleSendMessage = async (message: string) => {
    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Note: In AI Studio runtime, we should point to the correct internal API or the mock behavior if the backend isn't ready.
      // Based on the user's provided code, they are using http://localhost:8001
      // I'll keep the structure but add error handling for the preview environment.
      
      const response = await fetch('http://localhost:8001/api/service-request', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId }),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      if (data.session_id) setSessionId(data.session_id);
      if (data.workflow_steps) setWorkflow(data.workflow_steps);

      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: data.message,
        timestamp: new Date(),
      }]);
    } catch (err: any) {
      console.error('Error:', err);
      // Fallback response for preview if backend is disconnected
      setTimeout(() => {
        setMessages((prev) => [...prev, {
          role: 'assistant',
          content: "I'm currently in a demo environment without backend access, but my UI is fully operational. Typically, I would coordinate with my agents to fulfill your request.",
          timestamp: new Date(),
        }]);
        setIsLoading(false);
      }, 1500);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="pt-20 h-screen flex overflow-hidden bg-bg-deep"
    >
      {/* Sidebar for desktop and mobile */}
      <aside className="hidden lg:flex relative z-20 border-r border-white/10 bg-white/[0.03] backdrop-blur-2xl">
        <Sidebar />
      </aside>
      {/* Mobile sidebar toggle (optional, can be improved with a drawer) */}
      <div className="lg:hidden fixed top-20 left-0 z-30">
        <Sidebar />
      </div>

      {/* Main Chat Area */}
      {/* <div > */}
      <main className="flex-1 p-2 sm:p-4 md:p-6 flex flex-col min-w-0 w-full max-w-full">
        <ChatWindow
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
      </main>

      {/* Right Sidebar - Workflow & Reasoning */}
      <aside className=" hidden xl:flex w-96 flex-col border-l border-white/5 bg-white/[0.01] overflow-y-auto custom-scrollbar">
        <div className="p-6 space-y-8">
          <WorkflowTimeline workflow={workflow} />
          <AgentReasoning workflow={workflow} />

          {workflow.length === 0 && (
            <div className="p-8 rounded-3xl border border-white/5 bg-white/[0.02] text-center">
              <Users className="w-10 h-10 text-white/10 mx-auto mb-4" />
              <h4 className="text-sm font-bold mb-2">Team Intelligence</h4>
              <p className="text-xs text-white/30 leading-relaxed">
                Connect with our agent network to optimize your home service lifecycle.
              </p>
            </div>
          )}
        </div>
      </aside>
      {/* </div> */}
    </motion.div>
  );
    }