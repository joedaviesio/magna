'use client';

export function RummageKiwi({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 640 640"
      fill="currentColor"
      className={className}
    >
      <style>{`
        @keyframes pecking {
          0%, 100% { transform: rotate(0deg) translateY(0); }
          20% { transform: rotate(12deg) translateY(4px); }
          40% { transform: rotate(-5deg) translateY(-2px); }
          60% { transform: rotate(15deg) translateY(6px); }
          80% { transform: rotate(-3deg) translateY(0); }
        }
        @keyframes shuffleFeet {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(3px); }
          50% { transform: translateX(-3px); }
          75% { transform: translateX(2px); }
        }
        .kiwi-body {
          animation: pecking 1.2s ease-in-out infinite;
          transform-origin: 320px 400px;
        }
        .kiwi-feet {
          animation: shuffleFeet 0.8s ease-in-out infinite;
        }
      `}</style>
      <g className="kiwi-body">
        <path d="M323.2 452.4C354.4 433.6 387.9 416 424.3 416L480 416C484.6 416 489.1 415.8 493.6 415.3L578.9 537.2C582.9 542.9 590.2 545.4 596.8 543.3C603.4 541.2 608 535 608 528L608 288C608 217.3 550.7 160 480 160L424.3 160C387.9 160 354.4 142.4 323.2 123.6C294.3 106.1 260.3 96 224 96C118 96 32 182 32 288C32 359.1 70.6 421.1 128 454.3L128 520C128 533.3 138.7 544 152 544C165.3 544 176 533.3 176 520L176 474C191.3 477.9 207.4 480 224 480C229.4 480 234.7 479.8 240 479.3L240 520C240 533.3 250.7 544 264 544C277.3 544 288 533.3 288 520L288 469.1C300.4 464.7 312.2 459.1 323.2 452.4z" />
        <circle cx="480" cy="288" r="16" fill="white" />
      </g>
    </svg>
  );
}
