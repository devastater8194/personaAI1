"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "../lib/supabase";
import Sidebar from "./Sidebar";
import Header from "./Header";

export default function DashboardLayout({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const supabase = useMemo(() => createClient(), []);

  useEffect(() => {
    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        router.push("/login");
      } else {
        setUser(session.user);
      }
      setLoading(false);
    };

    checkUser();

    const { data: authListener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (event === "SIGNED_OUT") {
          router.push("/login");
        } else if (session) {
          setUser(session.user);
        }
      }
    );

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, [router, supabase]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[var(--color-bg-primary)] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[var(--color-accent-primary)]"></div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="flex h-screen bg-transparent text-[var(--color-text-primary)] font-[family-name:var(--font-sans)] overflow-hidden relative dashboard-bg">

      {/* Sidebar */}
      <div className="z-10 h-full flex flex-col md:flex">
         <Sidebar user={user} />
      </div>

      {/* Main Content Pane */}
      <div className="flex flex-col flex-1 overflow-hidden z-10 w-full">
        <Header user={user} />
        <main className="flex-1 overflow-y-auto p-4 md:p-8 bg-transparent">
           <div className="relative z-10">
               {children}
           </div>
        </main>
      </div>
    </div>
  );
}
