"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { createClient } from '../lib/supabase';
import { motion } from 'motion/react';

export default function LoginPage() {
  const router = useRouter();
  const supabase = createClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { data, error: authError } = await supabase.auth.signInWithPassword({
        email: formData.email,
        password: formData.password,
      });

      if (authError) {
        // Handle specific error messages
        if (authError.message.includes("Email not confirmed")) {
          setError("Please confirm your email first. Check your inbox for the confirmation link.");
        } else if (authError.message.includes("Invalid login")) {
          setError("Invalid email or password. Please try again.");
        } else {
          setError(authError.message);
        }
        return;
      }

      if (data.user) {
        router.push('/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Failed to sign in');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-transparent flex items-center justify-center p-4 text-[var(--color-text-primary)] font-[family-name:var(--font-sans)]">
      
      <Link href="/" className="absolute top-8 left-8 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] flex items-center gap-2 transition-colors">
        <span>←</span> Back to Home
      </Link>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <div className="font-[family-name:var(--font-heading)] font-bold text-3xl tracking-tight mb-2">
            Welcome Back
          </div>
          <p className="text-[var(--color-text-secondary)] text-sm">Sign in to your PersonaAI account</p>
        </div>

        <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-2xl p-8 shadow-xl">
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">Email Address</label>
              <input 
                type="email" 
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl px-4 py-3 text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors"
                placeholder="you@example.com"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider">Password</label>
              </div>
              <input 
                type="password" 
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl px-4 py-3 text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors"
                placeholder="••••••••"
              />
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] hover:bg-[var(--color-accent-hover)] disabled:opacity-50 text-[var(--color-text-primary)] font-medium py-3 rounded-xl transition-colors mt-2 flex items-center justify-center gap-2"
            >
              {loading ? (
                <><span className="w-4 h-4 border-2 border-t-transparent border-white rounded-full animate-spin"></span> Signing in...</>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="mt-8 text-center text-sm text-[var(--color-text-muted)]">
            Don&apos;t have an account?{' '}
            <Link href="/register" className="text-[var(--color-accent-primary)] hover:text-indigo-300 transition-colors font-medium">
              Register now
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
