export interface Source {
  act_title: string;
  section_number: string;
  section_heading: string;
  url: string;
  excerpt: string;
  score: number;
}

export interface ChatResponse {
  response: string;
  sources: Source[];
  disclaimer: string;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}
