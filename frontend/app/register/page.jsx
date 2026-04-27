"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { createClient } from '../lib/supabase';
import { motion } from 'motion/react';

export default function RegisterPage() {
  const router = useRouter();
  const supabase = createClient();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords don't match");
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      setLoading(false);
      return;
    }

    try {
      // Strategy 1: Try via FastAPI backend (creates auth + identity in one call)
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      let backendOk = false;

      try {
        const res = await fetch(`${API_URL}/api/auth/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: formData.name,
            email: formData.email,
            password: formData.password,
          })
        });
        const data = await res.json();

        if (res.ok && data.success) {
          backendOk = true;
          // Now sign in on the client side so the session is set
          const { error: signInError } = await supabase.auth.signInWithPassword({
            email: formData.email,
            password: formData.password,
          });
          if (!signInError) {
            router.push('/dashboard');
            return;
          }
          // If sign-in fails (e.g. email confirmation required), show success message
          setSuccess(true);
          return;
        } else if (res.status === 409) {
          setError("This email is already registered. Try logging in instead.");
          return;
        } else {
          // Backend returned an error, fall through to client-side signup
          console.warn("Backend register failed, trying client-side:", data.detail);
        }
      } catch (fetchErr) {
        console.warn("Backend unreachable, trying client-side signup:", fetchErr);
      }

      // Strategy 2: Direct Supabase client-side signup (fallback)
      if (!backendOk) {
        const { data: authData, error: authError } = await supabase.auth.signUp({
          email: formData.email,
          password: formData.password,
          options: {
            data: { full_name: formData.name }
          }
        });

        if (authError) throw authError;

        // Check if email confirmation is needed
        if (authData?.user?.identities?.length === 0) {
          setError("This email is already registered. Try logging in instead.");
          return;
        }

        if (authData?.user && !authData?.session) {
          // Email confirmation required
          setSuccess(true);
          return;
        }

        if (authData?.session) {
          router.push('/dashboard');
          return;
        }
      }
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-transparent flex items-center justify-center p-4 text-[var(--color-text-primary)] font-[family-name:var(--font-sans)]">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md text-center"
        >
          <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-2xl p-8 shadow-xl">
            <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-5">
              <span className="text-emerald-400 text-3xl">✓</span>
            </div>
            <h2 className="font-[family-name:var(--font-heading)] text-2xl font-bold mb-3">Account Created!</h2>
            <p className="text-[var(--color-text-secondary)] text-sm mb-6">
              We've sent a confirmation link to <span className="text-[var(--color-text-primary)] font-medium">{formData.email}</span>.
              Please check your inbox and click the link to activate your account.
            </p>
            <Link href="/login" className="inline-block bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] hover:bg-[var(--color-accent-hover)] text-[var(--color-text-primary)] font-medium px-6 py-3 rounded-xl transition-colors">
              Go to Login
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

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
            Join Persona<span className="text-[var(--color-accent-primary)]">AI</span>
          </div>
          <p className="text-[var(--color-text-secondary)] text-sm">Create your identity-first content engine</p>
        </div>

        <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-2xl p-8 shadow-xl">
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">Full Name</label>
              <input 
                type="text" 
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl px-4 py-3 text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors"
                placeholder="Manan Shah"
              />
            </div>
            
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
              <label className="block text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">Password</label>
              <input 
                type="password" 
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={6}
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl px-4 py-3 text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors"
                placeholder="••••••••"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-[var(--color-text-secondary)] uppercase tracking-wider mb-2">Confirm Password</label>
              <input 
                type="password" 
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                minLength={6}
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
                <><span className="w-4 h-4 border-2 border-t-transparent border-white rounded-full animate-spin"></span> Creating account...</>
              ) : (
                'Complete Registration'
              )}
            </button>
          </form>

          <div className="mt-8 text-center text-sm text-[var(--color-text-muted)]">
            Already have an account?{' '}
            <Link href="/login" className="text-[var(--color-accent-primary)] hover:text-indigo-300 transition-colors font-medium">
              Sign in
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
