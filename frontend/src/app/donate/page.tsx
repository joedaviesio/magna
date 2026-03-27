'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, BookOpen, CheckCircle } from 'lucide-react';

export default function DonatePage() {
  const searchParams = useSearchParams();
  const success = searchParams.get('success') === 'true';
  const [amount, setAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const donationAmount = amount ? parseInt(amount) : null;

  const handleDonate = async () => {
    if (!donationAmount || donationAmount < 1) return;
    setIsLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8105'}/api/donate/checkout`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ amount: donationAmount }),
        }
      );

      const data = await response.json();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (err) {
      console.error('Failed to create checkout session:', err);
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-slate-50">
        <div className="max-w-2xl mx-auto px-6 py-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-50 rounded-full mb-6 mt-12">
            <CheckCircle className="w-8 h-8 text-green-500" />
          </div>
          <h1 className="text-3xl font-semibold text-slate-900 mb-3">Thank you!</h1>
          <p className="text-slate-500 max-w-md mx-auto mb-8">
            Your donation helps keep Bowen Public free for all New Zealanders.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-lg transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Bowen
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-2xl mx-auto px-6 py-12">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Bowen
        </Link>

        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-pink-50 rounded-full mb-4">
            <BookOpen className="w-7 h-7 text-pink-500" />
          </div>
          <h1 className="text-3xl font-semibold text-slate-900 mb-2">
            Support{' '}
            <span className="bowen-brand">
              <span style={{ color: '#5d78c5' }}>B</span>
              <span style={{ color: '#ffce31' }}>o</span>
              <span style={{ color: '#e25063' }}>w</span>
              <span style={{ color: '#ffce31' }}>e</span>
              <span style={{ color: '#e25063' }}>n</span>
            </span>{' '}
            Public
          </h1>
          <p className="text-slate-500 max-w-md mx-auto">
            Bowen is free for all New Zealanders. Donations help us cover server costs,
            expand our legislation bank and keep this service running. We also use donations for community outreach and education.
          </p>
        </div>

        {/* Amount input */}
        <div className="flex items-center justify-center gap-2 mb-6">
          <span className="text-4xl font-semibold text-slate-300">$</span>
          <input
            type="number"
            min="1"
            placeholder="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            autoFocus
            className="w-32 text-5xl font-semibold text-slate-800 bg-transparent text-center outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none placeholder:text-slate-200"
          />
          <span className="text-lg text-slate-400 self-end mb-2">NZD</span>
        </div>

        {/* Donate button */}
        <button
          onClick={handleDonate}
          disabled={!donationAmount || donationAmount < 1 || isLoading}
          className="w-full py-3 px-6 rounded-xl text-white font-medium text-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed animate-gradient-shift"
          style={{
            backgroundImage: 'linear-gradient(270deg, #3b82f6, #ec4899, #8b5cf6, #3b82f6)',
            backgroundSize: '300% 100%',
          }}
        >
          {isLoading ? 'Redirecting...' : donationAmount ? `Donate $${donationAmount}` : 'Enter an amount'}
        </button>

        <p className="text-center text-xs text-slate-400 mt-4">
          Payments processed securely by Stripe. Bowen Public is a New Zealand project.
        </p>

      </div>
    </div>
  );
}
