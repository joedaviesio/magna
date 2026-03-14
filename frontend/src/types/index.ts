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

export interface FileAttachment {
  filename: string;
  content_type: string;
  data: string; // base64
  preview_url?: string; // object URL for local preview
  size: number; // bytes
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  attachments?: Pick<FileAttachment, 'filename' | 'content_type' | 'size'>[];
}

export interface Act {
  short_name: string;
  title: string;
  year: number;
  topics: string[];
  url: string;
}

export interface ActsResponse {
  acts: Act[];
}
