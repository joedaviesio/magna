import { AlertTriangle } from 'lucide-react';
import Link from 'next/link';

export function DisclaimerFooter() {
  return (
    <div className="flex flex-col items-center gap-1 text-xs text-slate-500 py-2">
      <div className="flex items-center gap-2">

        <span>
          <span className="bowen-brand">Bowen</span> is an ai model, NOT legal advice. Consult a qualified NZ lawyer for legal decisions.
        </span>
      </div>
      <div className="flex gap-3">
        <Link
          href="/data-policy"
          className="text-slate-400 hover:text-slate-600 underline underline-offset-2"
        >
          Data Policy
        </Link>
        <Link
          href="/te-tiriti"
          className="text-slate-400 hover:text-slate-600 underline underline-offset-2"
        >
          Bowen's approach to The Treaty / Te Tiriti
        </Link>
        <a
          href="https://joedavies.io"
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-400 hover:text-slate-600 underline underline-offset-2"
        >
          Founder
        </a>
      </div>
    </div>
  );
}
