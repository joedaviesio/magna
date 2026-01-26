interface ManatIconProps {
  className?: string;
}

export function ManatIcon({ className }: ManatIconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
      <path d="M12 4c-4.41 0-8 3.59-8 8h2c0-3.31 2.69-6 6-6V4z"/>
      <path d="M12 4v2c3.31 0 6 2.69 6 6h2c0-4.41-3.59-8-8-8z"/>
      <path d="M12 20c4.41 0 8-3.59 8-8h-2c0 3.31-2.69 6-6 6v2z"/>
      <path d="M12 20v-2c-3.31 0-6-2.69-6-6H4c0 4.41 3.59 8 8 8z"/>
      <path d="M12 4v16M4 12h16" stroke="currentColor" strokeWidth="1.5" fill="none"/>
    </svg>
  );
}
