'use client';

import { ManatIcon } from './ManatIcon';

export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm p-4">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-6 h-6 bg-gradient-to-br from-navy to-navy-light rounded-md flex items-center justify-center">
            <ManatIcon className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="bowen-brand text-xs text-slate-500">Bowen</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 bg-navy rounded-full animate-bounce [animation-delay:-0.3s]" />
          <div className="w-2 h-2 bg-navy rounded-full animate-bounce [animation-delay:-0.15s]" />
          <div className="w-2 h-2 bg-navy rounded-full animate-bounce" />
          <span className="ml-2 text-sm text-slate-500">Searching legislation...</span>
        </div>
      </div>
    </div>
  );
}
