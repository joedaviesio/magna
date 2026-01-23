'use client';

import ReactMarkdown from 'react-markdown';
import { ManatIcon } from './ManatIcon';
import { Message } from '@/types';
import { Sources } from './Sources';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[85%] md:max-w-[75%] ${
          isUser
            ? 'bg-gradient-to-br from-navy to-navy-light text-white rounded-2xl rounded-br-sm'
            : 'bg-white border border-slate-200 rounded-2xl rounded-bl-sm'
        } p-4`}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100">
            <div className="w-6 h-6 bg-gradient-to-br from-navy to-navy-light rounded-md flex items-center justify-center">
              <ManatIcon className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="magna-brand text-xs text-slate-500">Magna</span>
          </div>
        )}

        <div
          className={`prose prose-sm max-w-none ${
            isUser
              ? 'prose-invert'
              : 'prose-slate prose-headings:text-navy prose-a:text-blue-600'
          }`}
        >
          {isUser ? (
            <p className="m-0">{message.content}</p>
          ) : (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          )}
        </div>

        {!isUser && message.sources && <Sources sources={message.sources} />}
      </div>
    </div>
  );
}
