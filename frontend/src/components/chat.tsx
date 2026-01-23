'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import Link from 'next/link';
import { AlertCircle, BookOpen, Heart } from 'lucide-react';
import { ManatIcon } from './ManatIcon';
import { useChat } from '@/hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { DisclaimerModal } from './DisclaimerModal';
import { DisclaimerFooter } from './DisclaimerFooter';
import { TypingIndicator } from './TypingIndicator';

const LEGISLATION_COVERAGE = [
  { name: 'Residential Tenancies Act 1986', abbrev: 'RTA', description: 'tenancy, bonds, landlord/tenant rights' },
  { name: 'Employment Relations Act 2000', abbrev: 'ERA', description: 'employment, dismissal, leave, unions' },
  { name: 'Companies Act 1993', abbrev: 'CA', description: 'company formation, directors, shareholders' },
  { name: 'Fair Trading Act 1986', abbrev: 'FTA', description: 'consumer protection, misleading conduct' },
  { name: 'Property Law Act 2007', abbrev: 'PLA', description: 'property transactions, mortgages, leases' },
  { name: 'Privacy Act 2020', abbrev: 'PA', description: 'personal information, privacy principles' },
  { name: 'Building Act 2004', abbrev: 'BA', description: 'building consents, code compliance' },
  { name: 'Contract and Commercial Law Act 2017', abbrev: 'CCLA', description: 'contracts, sale of goods' },
  { name: 'Resource Management Act 1991', abbrev: 'RMA', description: 'environmental management, resource consents' },
];

// Placeholder supporters - replace with actual donors
const SUPPORTERS = [
  { name: 'Russell McVeagh', tier: 'gold' },
  { name: 'Chapman Tripp', tier: 'gold' },
  { name: 'Bell Gully', tier: 'silver' },
  { name: 'Simpson Grierson', tier: 'silver' },
  { name: 'MinterEllisonRuddWatts', tier: 'silver' },
  { name: 'Buddle Findlay', tier: 'bronze' },
  { name: 'Duncan Cotterill', tier: 'bronze' },
  { name: 'Lane Neave', tier: 'bronze' },
];

export function Chat() {
  const { messages, isLoading, error, send, clearMessages } = useChat();
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Clear cache on mount for fresh chat each visit
  useEffect(() => {
    localStorage.removeItem('magna-disclaimer-accepted');
    clearMessages();
  }, [clearMessages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleDisclaimerAccept = useCallback(() => {
    setDisclaimerAccepted(true);
  }, []);

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <DisclaimerModal onAccept={handleDisclaimerAccept} />

      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-sm border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 bg-gradient-to-br from-navy to-navy-light rounded-lg flex items-center justify-center shadow-md">
              <ManatIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="magna-brand text-xl text-navy tracking-wide">
                Magna
              </h1>
              <p className="text-[10px] text-slate-400 uppercase tracking-wider">
                Prototype
              </p>
            </div>
          </Link>
          <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-xs text-green-700 font-medium">Online</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-6">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mb-6">
              <ManatIcon className="w-8 h-8 text-navy" />
            </div>
            <h2 className="text-3xl text-navy mb-3">
              Ask <span className="magna-brand">Magna</span> about New Zealand Law
            </h2>
            <p className="text-slate-500 max-w-md mb-8">
              Get instant answers grounded in legislation, with direct citations to official sources.
            </p>

            {/* Legislation Coverage */}
            <div className="w-full max-w-2xl">
              <div className="flex items-center justify-center gap-2 text-sm text-slate-500 mb-4">
                <BookOpen className="w-4 h-4" />
                <span>Legislation Coverage</span>
              </div>
              <div className="bg-slate-50 rounded-xl border border-slate-200 p-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {LEGISLATION_COVERAGE.map((act) => (
                    <div key={act.abbrev} className="text-left">
                      <p className="text-sm font-medium text-slate-700">{act.name}</p>
                      <p className="text-xs text-slate-500">{act.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Supporters Section */}
            <div className="w-full max-w-2xl mt-12">
              <div className="flex items-center justify-center gap-2 text-sm text-slate-500 mb-4">
                <Heart className="w-4 h-4" />
                <span>Proudly Supported By</span>
              </div>
              <div className="bg-gradient-to-br from-slate-50 to-white rounded-xl border border-slate-200 p-6">
                {/* Gold Tier */}
                <div className="mb-6">
                  <p className="text-[10px] uppercase tracking-widest text-amber-600 font-medium text-center mb-3">Gold Partners</p>
                  <div className="flex flex-wrap justify-center gap-4">
                    {SUPPORTERS.filter(s => s.tier === 'gold').map((supporter) => (
                      <div
                        key={supporter.name}
                        className="px-5 py-3 bg-gradient-to-br from-amber-50 to-amber-100/50 border border-amber-200 rounded-lg"
                      >
                        <span className="font-semibold text-slate-800">{supporter.name}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Silver Tier */}
                <div className="mb-6">
                  <p className="text-[10px] uppercase tracking-widest text-slate-400 font-medium text-center mb-3">Silver Partners</p>
                  <div className="flex flex-wrap justify-center gap-3">
                    {SUPPORTERS.filter(s => s.tier === 'silver').map((supporter) => (
                      <div
                        key={supporter.name}
                        className="px-4 py-2 bg-slate-100 border border-slate-200 rounded-lg"
                      >
                        <span className="font-medium text-sm text-slate-700">{supporter.name}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Bronze Tier */}
                <div>
                  <p className="text-[10px] uppercase tracking-widest text-orange-400 font-medium text-center mb-3">Bronze Partners</p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {SUPPORTERS.filter(s => s.tier === 'bronze').map((supporter) => (
                      <div
                        key={supporter.name}
                        className="px-3 py-1.5 bg-orange-50 border border-orange-100 rounded-md"
                      >
                        <span className="text-sm text-slate-600">{supporter.name}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Call to Action */}
                <div className="mt-8 pt-6 border-t border-slate-200 text-center">
                  <p className="text-xs text-slate-500 mb-2">
                    Help us expand free legal information access for all New Zealanders
                  </p>
                  <p className="text-xs text-slate-400">
                    Contact <span className="text-navy font-medium">donate@magna.law</span> to become a supporter
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6 pb-32">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && <TypingIndicator />}
            {error && (
              <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <p>{error}</p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {/* Input Area */}
      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-white via-white to-transparent pt-8 pb-4 px-4">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSend={send} isLoading={isLoading} />
          <DisclaimerFooter />
        </div>
      </div>
    </div>
  );
}
