'use client';

import { useState, useEffect } from 'react';
import { AlertTriangle } from 'lucide-react';
import { ManatIcon } from './ManatIcon';

const DISCLAIMER_KEY = 'magna-disclaimer-accepted';

interface DisclaimerModalProps {
  onAccept: () => void;
}

export function DisclaimerModal({ onAccept }: DisclaimerModalProps) {
  const [checked, setChecked] = useState(false);
  const [show, setShow] = useState(false);

  useEffect(() => {
    const accepted = localStorage.getItem(DISCLAIMER_KEY);
    if (!accepted) {
      setShow(true);
    } else {
      onAccept();
    }
  }, [onAccept]);

  const handleAccept = () => {
    localStorage.setItem(DISCLAIMER_KEY, 'true');
    setShow(false);
    onAccept();
  };

  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl p-8 max-w-lg w-full shadow-2xl">
        <div className="w-14 h-14 bg-gradient-to-br from-navy to-navy-light rounded-xl flex items-center justify-center mb-6">
          <ManatIcon className="w-7 h-7 text-white" />
        </div>

        <h2 className="text-2xl text-navy mb-4">
          Welcome to <span className="magna-brand">Magna</span>
        </h2>

        <p className="text-slate-600 mb-4 leading-relaxed">
          <span className="magna-brand text-navy">Magna</span> is an AI-powered legal information tool that searches New Zealand legislation to answer your questions.
        </p>

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <div className="flex gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-amber-900 font-medium mb-1">Important Disclaimer</p>
              <p className="text-amber-800 text-sm leading-relaxed">
                This is <strong>NOT legal advice</strong>. Information may be incomplete or outdated. Always verify with official sources and consult a qualified NZ lawyer for legal decisions.
              </p>
            </div>
          </div>
        </div>

        <label className="flex items-start gap-3 mb-6 cursor-pointer">
          <input
            type="checkbox"
            checked={checked}
            onChange={(e) => setChecked(e.target.checked)}
            className="mt-1 w-4 h-4 rounded border-slate-300 text-navy focus:ring-navy"
          />
          <span className="text-sm text-slate-600">
            I understand <span className="magna-brand">Magna</span> is an AI Chat bot, not legal advice, and I will verify important information with official sources.
          </span>
        </label>

        <button
          onClick={handleAccept}
          disabled={!checked}
          className={`w-full py-3.5 rounded-lg font-medium transition-all ${
            checked
              ? 'bg-gradient-to-r from-navy to-navy-light text-white hover:shadow-lg hover:-translate-y-0.5'
              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
          }`}
        >
          Continue
        </button>
      </div>
    </div>
  );
}
