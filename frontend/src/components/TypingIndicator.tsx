'use client';

import { useState, useEffect } from 'react';
import { ManatIcon } from './ManatIcon';

const LOADING_PHRASES = [
  'Searching legislation...',
  'Rummaging through statutes...',
  'Consulting the archives...',
  'Cross-referencing sections...',
  'Parsing provisions...',
  'Sifting through schedules...',
  'Deciphering legalese...',
  'Checking the fine print...',
  'Flipping through Acts...',
  'Untangling subsections...',
  'Perusing parliamentary intent...',
  'Reviewing the record...',
];

export function TypingIndicator() {
  const [phraseIndex, setPhraseIndex] = useState(() =>
    Math.floor(Math.random() * LOADING_PHRASES.length)
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setPhraseIndex((prev) => {
        let next;
        do {
          next = Math.floor(Math.random() * LOADING_PHRASES.length);
        } while (next === prev);
        return next;
      });
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex justify-start">
      <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-sm p-4">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-6 h-6 bg-gradient-to-br from-primary to-primary-light rounded-md flex items-center justify-center">
            <ManatIcon className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="bowen-brand text-xs text-slate-500">Bowen</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]" />
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]" />
          <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
          <span className="ml-2 text-sm text-slate-500 transition-opacity duration-300">
            {LOADING_PHRASES[phraseIndex]}
          </span>
        </div>
      </div>
    </div>
  );
}
