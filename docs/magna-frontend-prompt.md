# Magna Frontend Build Prompt for Claude Code

## Project Overview

Build a Next.js frontend for "Magna" - a free, public NZ legal information assistant. The backend API is already running at `http://localhost:8000`.

## Tech Stack

- Next.js 14+ with App Router
- TypeScript
- Tailwind CSS
- Lucide React icons

## Design Requirements

### Brand Identity
- **Name**: Magna (evokes Magna Carta, legal authority)
- **Theme**: Clean, professional, trustworthy
- **Primary color**: Dark navy (#1a1a2e) for authority/trust
- **Background**: Pure white (#ffffff)
- **Accent**: Subtle blue for links
- **Typography**: Elegant serif for headings (Georgia or similar), clean sans-serif for body (Inter or system fonts)

### UI Components Needed

#### 1. Landing/Disclaimer Modal
- Appears on first visit
- Title: "Welcome to Magna"
- Explains this is AI-powered legal INFORMATION, not advice
- Checkbox: "I understand this is not legal advice"
- "Continue" button (disabled until checkbox checked)
- Store acceptance in localStorage

#### 2. Main Chat Interface
- Clean white background
- Centered chat container (max-width ~800px)
- Header with "Magna" logo/name and tagline "NZ Legal Information Assistant"
- Message history area (scrollable)
- Input area at bottom with send button

#### 3. Message Components
- **User messages**: Right-aligned, subtle background
- **Assistant messages**: Left-aligned, white background with subtle border
- Show "Sources" expandable section below assistant messages
- Each source shows: Act name, Section number, link to legislation.govt.nz

#### 4. Sources Panel
- Collapsible/expandable
- Shows cited legislation sections
- Each source is clickable (opens legislation.govt.nz in new tab)
- Format: "Section X - Act Name" with excerpt preview

#### 5. Disclaimer Footer
- Always visible at bottom of chat
- Text: "⚠️ This is AI-generated information, NOT legal advice. Consult a qualified NZ lawyer for legal decisions."
- Subtle styling, not intrusive

#### 6. Example Questions
- Show 4-6 example questions when chat is empty
- Clickable to auto-fill input
- Examples:
  - "What is the maximum bond for a rental property?"
  - "How much notice is required to end employment?"
  - "What are my rights if a product is faulty?"
  - "When do I need a building consent?"
  - "What are the privacy principles under NZ law?"

## API Integration

### Backend Endpoints (already running on localhost:8000)

#### POST /chat
```typescript
// Request
interface ChatRequest {
  message: string;
}

// Response
interface ChatResponse {
  response: string;
  sources: Source[];
  disclaimer: string;
}

interface Source {
  act_title: string;
  section_number: string;
  section_heading: string;
  url: string;
  excerpt: string;
  score: float;
}
```

#### GET /health
Returns health status of the backend.

#### GET /acts
Returns list of available acts.

### API Client Example

```typescript
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
```

## File Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx      # Root layout with fonts
│   │   ├── page.tsx        # Main chat page
│   │   └── globals.css     # Global styles
│   ├── components/
│   │   ├── Chat.tsx        # Main chat container
│   │   ├── ChatMessage.tsx # Individual message component
│   │   ├── ChatInput.tsx   # Input field + send button
│   │   ├── Sources.tsx     # Expandable sources panel
│   │   ├── Disclaimer.tsx  # Disclaimer modal + footer
│   │   └── ExampleQuestions.tsx
│   ├── hooks/
│   │   └── useChat.ts      # Chat state management
│   └── lib/
│       └── api.ts          # API client functions
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

## Key Functionality

### Chat Flow
1. User types question in input
2. Show loading state (typing indicator)
3. POST to /chat endpoint
4. Display response with sources
5. Sources are collapsible
6. Scroll to new message

### State Management
- Use React useState/useReducer for chat messages
- Store messages as array: `{ role: 'user' | 'assistant', content: string, sources?: Source[] }`
- Handle loading state
- Handle errors gracefully

### Responsive Design
- Mobile-first approach
- Chat input stays fixed at bottom on mobile
- Sources panel adapts to screen size
- Readable on all devices

## Sample Component: ChatMessage

```tsx
interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

export function ChatMessage({ role, content, sources }: ChatMessageProps) {
  const [showSources, setShowSources] = useState(false);
  
  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-lg p-4 ${
        role === 'user' 
          ? 'bg-slate-100' 
          : 'bg-white border border-slate-200'
      }`}>
        <div className="prose prose-slate">
          {/* Render markdown content */}
          {content}
        </div>
        
        {sources && sources.length > 0 && (
          <div className="mt-3 pt-3 border-t">
            <button 
              onClick={() => setShowSources(!showSources)}
              className="text-sm text-blue-600 hover:underline"
            >
              {showSources ? 'Hide' : 'Show'} {sources.length} sources
            </button>
            
            {showSources && (
              <div className="mt-2 space-y-2">
                {sources.map((source, i) => (
                  <a 
                    key={i}
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-sm p-2 bg-slate-50 rounded hover:bg-slate-100"
                  >
                    <div className="font-medium">{source.act_title}</div>
                    {source.section_number && (
                      <div className="text-slate-600">Section {source.section_number}</div>
                    )}
                  </a>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

## Important Notes

1. **CORS**: Backend already allows localhost:3000, so no issues expected

2. **Markdown Rendering**: Assistant responses may include markdown (bold, lists). Consider using `react-markdown` or similar.

3. **Loading States**: Show a typing indicator while waiting for response

4. **Error Handling**: Display friendly error messages if API fails

5. **Accessibility**: Ensure proper ARIA labels, keyboard navigation

6. **No Authentication**: This is a public tool, no login required

## Commands to Set Up

```bash
cd ~/Desktop/magna/frontend

# If starting fresh:
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Install additional dependencies
npm install lucide-react react-markdown

# Start development server
npm run dev
```

## Success Criteria

- [ ] Disclaimer modal appears on first visit
- [ ] Can type and send questions
- [ ] Responses display with proper formatting
- [ ] Sources are shown and clickable
- [ ] Links open legislation.govt.nz
- [ ] Mobile responsive
- [ ] Loading states work
- [ ] Error handling works
- [ ] Clean, professional appearance
- [ ] Disclaimer always visible

## Reference Design

The UI should feel like a premium legal tool - clean, trustworthy, authoritative. Think of it as the "ChatGPT for NZ law" but with appropriate guardrails and citations. The design should instill confidence while being clear about limitations.