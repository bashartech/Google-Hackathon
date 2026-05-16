import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, User, Bot, Sparkles, Command, MessageSquare, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import ReactMarkdown from 'react-markdown';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatWindowProps {
  onSendMessage: (message: string) => Promise<void>;
  isLoading: boolean;
  messages: Message[];
}

export default function ChatWindow({
  onSendMessage,
  isLoading,
  messages,
}: ChatWindowProps) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const messageText = input.trim();
    setInput('');
    await onSendMessage(messageText);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface-panel rounded-[2.5rem] border border-white/5 overflow-hidden shadow-2xl relative">
      {/* Header */}
      <div className="px-8 py-6 border-b border-white/5 bg-gradient-to-r from-brand-primary/10 to-transparent flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-brand-primary/20 rounded-xl text-brand-primary border border-brand-primary/30">
            <MessageSquare className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white tracking-tight">Active Collaboration</h2>
            <p className="text-[11px] text-slate-500 font-medium">Session #SL-09412 - Intelligent Nexus</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
           <div className="flex -space-x-2 mr-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="w-7 h-7 rounded-full border-2 border-surface bg-slate-800 flex items-center justify-center text-[10px] font-bold">A{i}</div>
              ))}
           </div>
           <button className="p-2 rounded-lg hover:bg-white/5 text-white/40 transition-colors">
              <Command className="w-4 h-4" />
           </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 scroll-smooth custom-scrollbar">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-4">
             <motion.div 
               initial={{ scale: 0.8, opacity: 0 }}
               animate={{ scale: 1, opacity: 1 }}
               className="w-20 h-20 rounded-[2rem] bg-brand-primary/10 border border-brand-primary/20 flex items-center justify-center shadow-2xl shadow-brand-primary/5 mb-8"
             >
                <Sparkles className="w-10 h-10 text-brand-primary" />
             </motion.div>
             <h3 className="text-2xl font-black mb-3">Orchestration Start.</h3>
             <p className="text-sm text-slate-500 max-w-xs leading-relaxed font-medium">
               Command the agent cluster to resolve your home needs. English, Urdu, or Roman Urdu protocols supported.
             </p>
             
             <div className="mt-10 grid grid-cols-1 gap-3 w-full max-w-sm">
                {["Emergency AC repair G-13", "Plumber for kitchen leak", "Electrician urgent"].map((hint, i) => (
                  <button 
                    key={i}
                    onClick={() => setInput(hint)}
                    className="px-6 py-3 rounded-2xl bg-white/[0.02] border border-white/5 text-xs text-slate-400 hover:bg-white/5 hover:text-white transition-all text-left font-bold uppercase tracking-wider"
                  >
                    "{hint}"
                  </button>
                ))}
             </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={index}
              className={cn(
                "flex gap-5",
                message.role === 'user' ? "flex-row-reverse" : "flex-row"
              )}
            >
              <div className={cn(
                "w-10 h-10 rounded-2xl flex-shrink-0 flex items-center justify-center border",
                message.role === 'user' 
                  ? "bg-white/5 border-white/10" 
                  : "bg-brand-primary/10 border-brand-primary/20"
              )}>
                {message.role === 'user' ? <User className="w-5 h-5 text-white/40" /> : <Bot className="w-5 h-5 text-brand-primary" />}
              </div>
              
              <div className={cn(
                "max-w-[80%] space-y-2",
                message.role === 'user' ? "items-end" : "items-start"
              )}>
                <div className={cn(
                  "px-6 py-4 rounded-3xl text-sm leading-relaxed font-medium",
                  message.role === 'user' 
                    ? "bg-brand-primary/20 border border-brand-primary/30 text-sky-50 rounded-tr-none" 
                    : "bg-white/5 border border-white/10 text-slate-300 rounded-tl-none"
                )}>
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                </div>
                <div className={cn(
                  "flex items-center gap-2 px-1 text-[10px] font-black uppercase tracking-widest text-slate-600",
                  message.role === 'user' && "flex-row-reverse"
                )}>
                  <span>{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  <span className="w-1 h-1 rounded-full bg-slate-800" />
                  <span>{message.role === 'user' ? 'Operator' : 'Coordinator'}</span>
                </div>
              </div>
            </motion.div>
          ))
        )}

        {isLoading && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-5"
          >
            <div className="w-10 h-10 rounded-2xl bg-brand-primary/10 border border-brand-primary/20 flex items-center justify-center">
              <Loader2 className="w-5 h-5 text-brand-primary animate-spin" />
            </div>
            <div className="bg-white/5 border border-white/10 px-6 py-4 rounded-3xl rounded-tl-none">
               <div className="flex gap-1.5">
                  {[0, 1, 2].map((i) => (
                    <motion.div 
                      key={i}
                      animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.1, 0.8] }}
                      transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                      className="w-1.5 h-1.5 rounded-full bg-brand-primary"
                    />
                  ))}
               </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-8 bg-surface border-t border-white/5">
        <form onSubmit={handleSubmit} className="relative group">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message to the agent cluster..."
            disabled={isLoading}
            className="w-full bg-[#020408] border border-white/10 rounded-2xl px-6 py-5 pr-16 text-sm focus:outline-none focus:border-brand-primary/50 transition-all resize-none min-h-[64px] max-h-32 text-slate-200 placeholder:text-slate-700 font-medium"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-3.5 bottom-3.5 p-3 bg-brand-primary text-white rounded-xl hover:bg-sky-500 transition-all disabled:opacity-30 disabled:grayscale group-focus-within:shadow-[0_0_15px_rgba(14,165,233,0.4)]"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
        <div className="mt-4 flex items-center justify-between px-2">
           <div className="flex items-center gap-5">
              <div className="flex items-center gap-1.5 grayscale opacity-30 hover:grayscale-0 hover:opacity-100 transition-all cursor-pointer">
                 <Command className="w-3.5 h-3.5 text-white" />
                 <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Library</span>
              </div>
              <div className="flex items-center gap-1.5 grayscale opacity-30 hover:grayscale-0 hover:opacity-100 transition-all cursor-pointer">
                 <Zap className="w-3.5 h-3.5 text-white" />
                 <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Flash Mode</span>
              </div>
           </div>
           <span className="text-[10px] text-slate-700 font-bold uppercase tracking-[0.2em]">Press Enter to Execute</span>
        </div>
      </div>
    </div>
  );
}
