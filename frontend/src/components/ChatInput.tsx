'use client';

import { useState, useMemo, FormEvent, KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';

// Bowen brand colors from the logo
const BRAND_COLORS = ['#5d78c5', '#ffce31', '#e25063'];

function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, isLoading, placeholder = 'Ask about New Zealand legislation...' }: ChatInputProps) {
  const [input, setInput] = useState('');

  // Randomly assign brand colors to each border side
  const borderColors = useMemo(() => {
    const shuffled = shuffleArray(BRAND_COLORS);
    return {
      top: shuffled[0],
      right: shuffled[1],
      bottom: shuffled[2],
      left: shuffled[3],
    };
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSend(input);
    setInput('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div
        className="flex gap-3 bg-white rounded-xl p-2 shadow-lg shadow-slate-200/50"
        style={{
          borderWidth: '2px',
          borderStyle: 'solid',
          borderTopColor: borderColors.top,
          borderRightColor: borderColors.right,
          borderBottomColor: borderColors.bottom,
          borderLeftColor: borderColors.left,
        }}
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          rows={1}
          className="flex-1 resize-none bg-transparent border-none outline-none focus:outline-none focus:ring-0 px-3 py-2.5 text-slate-900 placeholder:text-slate-400 text-[15px]"
          style={{ minHeight: '44px', maxHeight: '120px' }}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className={`px-5 rounded-lg font-medium transition-all flex items-center gap-2 ${
            input.trim() && !isLoading
              ? 'bg-slate-600 text-white hover:bg-slate-500 hover:shadow-md rounded-xl'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          }`}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Send className="w-4 h-4" />
          )}
          <span className="hidden sm:inline">Send</span>
        </button>
      </div>
    </form>
  );
}
