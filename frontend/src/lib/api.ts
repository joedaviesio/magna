import { ChatResponse } from '@/types';

const API_BASE = 'http://localhost:8000';

export async function sendMessage(message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

export async function getActs(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/acts`);
  if (!response.ok) {
    throw new Error('Failed to fetch acts');
  }
  return response.json();
}
