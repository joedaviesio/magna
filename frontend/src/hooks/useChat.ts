'use client';

import { useState, useCallback, useMemo, useEffect } from 'react';
import { Message } from '@/types';
import { sendMessage, BowenApiError } from '@/lib/api';

const SESSION_STORAGE_KEY = 'bowen-session-id';
const MESSAGES_STORAGE_KEY = 'bowen-chat-messages';

function generateSessionId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function getOrCreateSessionId(): string {
  if (typeof window === 'undefined') return generateSessionId();

  const stored = localStorage.getItem(SESSION_STORAGE_KEY);
  if (stored) return stored;

  const newId = generateSessionId();
  localStorage.setItem(SESSION_STORAGE_KEY, newId);
  return newId;
}

function loadStoredMessages(): Message[] {
  if (typeof window === 'undefined') return [];

  try {
    const stored = localStorage.getItem(MESSAGES_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.warn('Failed to load stored messages:', e);
  }
  return [];
}

function saveMessages(messages: Message[]): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(MESSAGES_STORAGE_KEY, JSON.stringify(messages));
  } catch (e) {
    console.warn('Failed to save messages:', e);
  }
}

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  // Get or create session ID (persisted in localStorage)
  const sessionId = useMemo(() => getOrCreateSessionId(), []);

  // Load stored messages on mount
  useEffect(() => {
    const stored = loadStoredMessages();
    if (stored.length > 0) {
      setMessages(stored);
    }
    setIsInitialized(true);
  }, []);

  // Save messages whenever they change (after initialization)
  useEffect(() => {
    if (isInitialized) {
      saveMessages(messages);
    }
  }, [messages, isInitialized]);

  const send = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    setError(null);
    const userMessage: Message = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(content, sessionId);
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        sources: response.sources,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      // Handle structured API errors
      if (err instanceof BowenApiError) {
        setError(err.userMessage);
      } else {
        setError('Failed to get a response. Please check if the backend is running and try again.');
      }
      // Remove the user message if the request failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, sessionId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    // Clear stored messages but keep session ID
    if (typeof window !== 'undefined') {
      localStorage.removeItem(MESSAGES_STORAGE_KEY);
    }
  }, []);

  const clearSession = useCallback(() => {
    setMessages([]);
    setError(null);
    // Clear everything including session ID
    if (typeof window !== 'undefined') {
      localStorage.removeItem(MESSAGES_STORAGE_KEY);
      localStorage.removeItem(SESSION_STORAGE_KEY);
    }
  }, []);

  return {
    messages,
    isLoading,
    error,
    send,
    clearMessages,
    clearSession,
    sessionId,
  };
}
