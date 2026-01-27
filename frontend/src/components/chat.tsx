'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import Link from 'next/link';
import { AlertCircle, BookOpen, Heart } from 'lucide-react';
import { ManatIcon } from './ManatIcon';
import { KiwiIcon } from './KiwiIcon';
import { useChat } from '@/hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { DisclaimerModal } from './DisclaimerModal';
import { DisclaimerFooter } from './DisclaimerFooter';
import { TypingIndicator } from './TypingIndicator';
import { getActs } from '@/lib/api';
import { Act } from '@/types';

// Fallback legislation coverage (used if API fails)
const FALLBACK_LEGISLATION = [
  { title: 'Residential Tenancies Act 1986', short_name: 'RTA', topics: ['tenancy', 'bonds', 'housing'] },
  { title: 'Employment Relations Act 2000', short_name: 'ERA', topics: ['employment', 'dismissal', 'leave'] },
  { title: 'Companies Act 1993', short_name: 'CA', topics: ['directors', 'shareholders', 'incorporation'] },
  { title: 'Consumer Guarantees Act 1993', short_name: 'CGA', topics: ['refunds', 'repairs', 'guarantees'] },
  { title: 'Property Law Act 2007', short_name: 'PLA', topics: ['property', 'mortgages', 'leases'] },
  { title: 'Fair Trading Act 1986', short_name: 'FTA', topics: ['consumer protection', 'misleading conduct'] },
  { title: 'Privacy Act 2020', short_name: 'PA', topics: ['personal information', 'data breaches'] },
  { title: 'Building Act 2004', short_name: 'BA', topics: ['consents', 'code compliance'] },
  { title: 'Contract and Commercial Law Act 2017', short_name: 'CCLA', topics: ['contracts', 'sale of goods'] },
  { title: 'Resource Management Act 1991', short_name: 'RMA', topics: ['environment', 'resource consents'] },
  { title: 'Crimes Act 1961', short_name: 'CA1961', topics: ['criminal offences', 'sentencing'] },
  { title: 'Health and Safety at Work Act 2015', short_name: 'HSWA', topics: ['workplace safety', 'PCBU duties'] },
  { title: 'Human Rights Act 1993', short_name: 'HRA', topics: ['discrimination', 'equality'] },
  { title: 'Income Tax Act 2007', short_name: 'ITA', topics: ['tax', 'deductions', 'income'] },
  { title: 'Land Transport Act 1998', short_name: 'LTA', topics: ['driving', 'licences', 'traffic'] },
  { title: 'Immigration Act 2009', short_name: 'IA', topics: ['visas', 'residence', 'deportation'] },
  { title: 'Trusts Act 2019', short_name: 'TA', topics: ['trusts', 'trustees', 'beneficiaries'] },
  { title: 'Insolvency Act 2006', short_name: 'INSA', topics: ['bankruptcy', 'liquidation'] },
  { title: 'Copyright Act 1994', short_name: 'CRA', topics: ['copyright', 'intellectual property'] },
  { title: 'Credit Contracts and Consumer Finance Act 2003', short_name: 'CCCFA', topics: ['loans', 'credit', 'interest'] },
  { title: 'Official Information Act 1982', short_name: 'OIA', topics: ['government', 'requests', 'disclosure'] },
  { title: 'Family Violence Act 2018', short_name: 'FVA', topics: ['protection orders', 'domestic violence'] },
  { title: 'Accident Compensation Act 2001', short_name: 'ACA', topics: ['ACC', 'injury', 'compensation'] },
  { title: 'Financial Markets Conduct Act 2013', short_name: 'FMCA', topics: ['securities', 'investment', 'disclosure'] },
  { title: 'Harmful Digital Communications Act 2015', short_name: 'HDCA', topics: ['cyberbullying', 'online harassment'] },
  { title: 'Unit Titles Act 2010', short_name: 'UTA', topics: ['body corporate', 'apartments'] },
  { title: 'Local Government Act 2002', short_name: 'LGA', topics: ['councils', 'rates', 'bylaws'] },
  { title: 'Family Court Act 1980', short_name: 'FCA', topics: ['family court', 'jurisdiction'] },
  { title: 'Coroners Act 2006', short_name: 'CORA', topics: ['inquests', 'death inquiries'] },
  { title: 'Sale of Goods Act 1908', short_name: 'SOGA', topics: ['sale', 'goods', 'contracts'] },
  { title: 'Education Act 1989', short_name: 'EA', topics: ['schools', 'students', 'curriculum'] },
  { title: 'Constitution Act 1986', short_name: 'CONST', topics: ['parliament', 'sovereignty', 'executive'] },
  { title: 'Electoral Act 1993', short_name: 'ELEC', topics: ['voting', 'elections', 'parliament'] },
  { title: 'Citizenship Act 1977', short_name: 'CITZ', topics: ['citizenship', 'naturalisation'] },
  { title: 'Anti-Money Laundering and Countering Financing of Terrorism Act 2009', short_name: 'AML', topics: ['money laundering', 'terrorism financing', 'reporting'] },
  { title: 'Trade Marks Act 2002', short_name: 'TMA', topics: ['trade marks', 'registration', 'infringement'] },
  { title: 'Patents Act 2013', short_name: 'PATA', topics: ['patents', 'inventions', 'intellectual property'] },
  { title: 'Climate Change Response Act 2002', short_name: 'CCRA', topics: ['emissions', 'carbon', 'climate'] },
  { title: 'Conservation Act 1987', short_name: 'CONS', topics: ['conservation', 'DOC', 'protected areas'] },
  { title: 'Public Service Act 2020', short_name: 'PSA', topics: ['public service', 'government agencies'] },
  { title: 'Fire and Emergency New Zealand Act 2017', short_name: 'FENZ', topics: ['fire', 'emergency', 'rescue'] },
  { title: 'Public Finance Act 1989', short_name: 'PFA', topics: ['budget', 'appropriation', 'crown'] },
  { title: 'District Courts Act 1947', short_name: 'DCA', topics: ['district court', 'jurisdiction'] },
  { title: 'Biosecurity Act 1993', short_name: 'BSA', topics: ['biosecurity', 'pest', 'quarantine'] },
  { title: 'Fisheries Act 1996', short_name: 'FA', topics: ['fishing', 'quota', 'marine'] },
  { title: 'Hazardous Substances and New Organisms Act 1996', short_name: 'HSNO', topics: ['hazardous', 'chemicals', 'GMO'] },
  { title: 'Freedom Camping Act 2011', short_name: 'FCAM', topics: ['camping', 'vehicles', 'local authority'] },
  { title: 'Health Act 1956', short_name: 'HA', topics: ['public health', 'sanitation', 'disease'] },
  { title: 'Medicines Act 1981', short_name: 'MA', topics: ['medicine', 'pharmacy', 'prescription'] },
  { title: 'Smokefree Environments Act 1990', short_name: 'SEA', topics: ['smoking', 'tobacco', 'vaping'] },
];

// Database stats (updated when legislation is processed)
const DATABASE_STATS = {
  acts: 50,
  sections: 104039,
  chunks: 110866,
};

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
  const [acts, setActs] = useState<Array<{ title: string; short_name: string; topics: string[] }>>(FALLBACK_LEGISLATION);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const lastAssistantRef = useRef<HTMLDivElement>(null);
  const wasLoadingRef = useRef(false);

  // Fetch acts from API on mount
  useEffect(() => {
    getActs()
      .then((fetchedActs) => {
        if (fetchedActs && fetchedActs.length > 0) {
          setActs(fetchedActs.map(act => ({
            title: act.title,
            short_name: act.short_name,
            topics: act.topics
          })));
        }
      })
      .catch((err) => {
        console.warn('Failed to fetch acts from API, using fallback:', err);
      });
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Scroll to top of assistant answer when response completes
  useEffect(() => {
    if (wasLoadingRef.current && !isLoading && messages.length > 0) {
      // Loading just finished - scroll to top of the last assistant message
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === 'assistant' && lastAssistantRef.current) {
        const headerHeight = 80; // Account for sticky header
        const elementTop = lastAssistantRef.current.getBoundingClientRect().top + window.scrollY;
        window.scrollTo({ top: elementTop - headerHeight, behavior: 'smooth' });
      }
    } else if (isLoading) {
      // While loading, scroll to bottom to show typing indicator
      scrollToBottom();
    }
    wasLoadingRef.current = isLoading;
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
            <div className="w-10 h-10 bg-white border border-slate-200 rounded-lg flex items-center justify-center shadow-md">
              <ManatIcon className="w-5 h-5 text-black" />
            </div>
            <div>
              <h1 className="bowen-brand text-xl tracking-wide">
                <span style={{color: '#00ac3f'}}>B</span>
                <span style={{color: '#1c66d1'}}>o</span>
                <span style={{color: '#e23d30'}}>w</span>
                <span style={{color: '#ffce31'}}>e</span>
                <span style={{color: '#1c66d1'}}>n</span>
              </h1>
              <p className="text-[10px] uppercase tracking-wider text-black">
                PUBLIC
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
            <div className="flex items-center gap-3 mb-6">
            <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center">
                <ManatIcon className="w-8 h-8 text-primary" />
              </div>
              <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center">
                <KiwiIcon className="w-8 h-8 text-primary" />
              </div>

            </div>
            <h2 className="text-3xl text-primary mb-3">
              Ask <span className="bowen-brand"><span style={{color: '#00ac3f'}}>B</span><span style={{color: '#1c66d1'}}>o</span><span style={{color: '#e23d30'}}>w</span><span style={{color: '#ffce31'}}>e</span><span style={{color: '#1c66d1'}}>n</span></span> about New Zealand Law
            </h2>
            <p className="text-slate-500 max-w-md mb-8">
              A public and free service for all New Zealanders.
            </p>

            {/* Database Stats */}
            <div className="w-full max-w-2xl mb-6">
              <div className="grid grid-cols-3 gap-3">
                <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 text-center">
                  <p className="text-2xl font-semibold text-slate-800">{acts.length}</p>
                  <p className="text-[10px] text-slate-500 uppercase tracking-wide">Acts</p>
                </div>
                <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 text-center">
                  <p className="text-2xl font-semibold text-slate-800">{DATABASE_STATS.sections.toLocaleString()}</p>
                  <p className="text-[10px] text-slate-500 uppercase tracking-wide">Sections</p>
                </div>
                <div className="bg-slate-50 rounded-lg border border-slate-200 p-3 text-center">
                  <p className="text-2xl font-semibold text-slate-800">{DATABASE_STATS.chunks.toLocaleString()}</p>
                  <p className="text-[10px] text-slate-500 uppercase tracking-wide">Searchable Chunks</p>
                </div>
              </div>
            </div>

            {/* Legislation Coverage */}
            <div className="w-full max-w-2xl">
              <div className="flex items-center justify-center gap-2 text-sm text-slate-500 mb-3">
                <BookOpen className="w-4 h-4" />
                <span>Legislation Coverage</span>
              </div>
              <div className="bg-slate-50 rounded-xl border border-slate-200 p-3">
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
                  {acts.map((act) => (
                    <div key={act.short_name} className="text-left p-2 bg-white rounded-lg border border-slate-100">
                      <p className="text-xs font-medium text-slate-700 leading-tight">{act.title}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5 truncate">{act.topics.join(', ')}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Supporters Section */}
            <div className="w-full max-w-2xl mt-12 mb-24">
              <div className="flex items-center justify-center gap-2 text-sm text-slate-500 mb-4">
                <Heart className="w-4 h-4" />
                <span>Proudly Supported By</span>
              </div>
              <div className="bg-gradient-to-br from-slate-50 to-white rounded-xl border border-slate-200 p-6">
                {/* Gold Tier */}
                {/* <div className="mb-6">
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
                </div> */}

                {/* Silver Tier */}
                {/* <div className="mb-6">
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
                </div> */}

                {/* Bronze Tier */}
                {/* <div>
                  <p className="text-[10px] uppercase tracking-widest text-primary-400 font-medium text-center mb-3">Bronze Partners</p>
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
                </div> */}

                {/* Call to Action */}
                <div className="mt-8 pt-6 border-t border-slate-200 text-center">
                  <p className="text-xs text-slate-500 mb-2">
                    Help us expand free legal information access for all New Zealanders
                  </p>
                  <p className="text-xs text-slate-400">
                    Contact <span className="text-primary font-medium">donate@bowenlaw.online</span> to become a supporter
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6 pb-32">
            {messages.map((message, index) => {
              const isLastAssistant = message.role === 'assistant' && index === messages.length - 1;
              return (
                <div key={index} ref={isLastAssistant ? lastAssistantRef : undefined}>
                  <ChatMessage message={message} />
                </div>
              );
            })}
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
