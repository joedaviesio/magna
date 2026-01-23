'use client';

import { MessageSquare } from 'lucide-react';

const EXAMPLE_QUESTIONS = [
  'What is the maximum bond for a rental property?',
  'How much notice is required to end employment?',
  'What are my rights if a product is faulty?',
  'When do I need a building consent?',
  'What are the privacy principles under NZ law?',
  'What warranties apply to consumer goods?',
];

interface ExampleQuestionsProps {
  onSelect: (question: string) => void;
}

export function ExampleQuestions({ onSelect }: ExampleQuestionsProps) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <p className="text-sm text-slate-500 mb-4 flex items-center justify-center gap-2">
        <MessageSquare className="w-4 h-4" />
        Try asking about:
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {EXAMPLE_QUESTIONS.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="text-left p-4 bg-slate-50 hover:bg-slate-100 border border-slate-200 hover:border-slate-300 rounded-xl transition-all text-sm text-slate-700 hover:text-navy"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
