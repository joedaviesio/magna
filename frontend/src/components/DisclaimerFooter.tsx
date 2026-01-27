import { AlertTriangle } from 'lucide-react';

export function DisclaimerFooter() {
  return (
    <div className="flex items-center justify-center gap-2 text-xs text-slate-500 py-2">
      <AlertTriangle className="w-3.5 h-3.5" />
      <span>
        <span className="bowen-brand">Bowen</span> is a Chat bot, NOT legal advice. Consult a qualified NZ lawyer for legal decisions.
      </span>
    </div>
  );
}
