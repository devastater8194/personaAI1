"use client";

import { useState, useEffect } from "react";

// Helper functions for date generation
const getDaysInMonthView = (date) => {
  const year = date.getFullYear();
  const month = date.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);

  // ISO weekday (1=Mon, 7=Sun)
  let startOffset = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1;
  const days = [];

  // Pad previous month
  const prevLastDay = new Date(year, month, 0).getDate();
  for (let i = startOffset - 1; i >= 0; i--) {
    days.push({
      date: new Date(year, month - 1, prevLastDay - i),
      isCurrentMonth: false
    });
  }

  // Current month days
  for (let i = 1; i <= lastDay.getDate(); i++) {
    days.push({
      date: new Date(year, month, i),
      isCurrentMonth: true
    });
  }

  // Pad next month
  const remainder = days.length % 7;
  if (remainder !== 0) {
    for (let i = 1; i <= 7 - remainder; i++) {
      days.push({
        date: new Date(year, month + 1, i),
        isCurrentMonth: false
      });
    }
  }
  return days;
};

const getDaysInWeekView = (date) => {
  const current = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const day = current.getDay();
  const diff = current.getDate() - day + (day === 0 ? -6 : 1); // Adjust when Sunday
  
  const monday = new Date(current.setDate(diff));
  const days = [];
  for (let i = 0; i < 7; i++) {
    const d = new Date(monday);
    d.setDate(monday.getDate() + i);
    days.push({ date: d, isCurrentMonth: d.getMonth() === date.getMonth() });
  }
  return days;
};

export default function ScheduleView({ user }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [scheduledPosts, setScheduledPosts] = useState([]);
  
  const [showModal, setShowModal] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);

  useEffect(() => {
    const abortController = new AbortController();
    
    async function fetchUpcoming() {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/schedule/upcoming/${user.id}`, { signal: abortController.signal });
        const data = await res.json();
        setScheduledPosts(Array.isArray(data) ? data : []);
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error("Failed to fetch schedule:", err);
        }
      }
    }
    if (user?.id) fetchUpcoming();
    
    return () => abortController.abort();
  }, [user.id]);

  const daysToRender = isExpanded ? getDaysInMonthView(currentDate) : getDaysInWeekView(currentDate);
  const weekDaysLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  const getPostsForDay = (dateObj) => {
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, '0');
    const day = String(dateObj.getDate()).padStart(2, '0');
    const dateStr = `${year}-${month}-${day}`;

    return scheduledPosts.filter(post => {
      if (!post.scheduled_for) return false;
      const postDateStr = post.scheduled_for.split("T")[0];
      return postDateStr === dateStr;
    });
  };

  const isToday = (dateObj) => {
    const today = new Date();
    return dateObj.getDate() === today.getDate() &&
           dateObj.getMonth() === today.getMonth() &&
           dateObj.getFullYear() === today.getFullYear();
  };

  const handleDayClick = (dayObj) => {
    setSelectedDate(dayObj.date);
    setShowModal(true);
  };

  const nextPost = scheduledPosts.length > 0 ? scheduledPosts[0] : null;

  return (
    <>
      <div className="mb-8">
        <h2 className="text-2xl font-[family-name:var(--font-heading)] font-bold text-[var(--color-text-primary)] mb-2">
          Phase 4 — Auto-Schedule + Post
        </h2>
        <p className="text-[var(--color-text-secondary)]">Content calendar with APScheduler and Social Graph APIs.</p>
      </div>

      <div className="glass-card border border-[var(--color-border)] rounded-xl p-6 mb-8">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <h3 
              className="font-[family-name:var(--font-heading)] font-semibold text-[var(--color-text-primary)] cursor-pointer hover:text-[var(--color-accent-primary)] transition-colors flex items-center gap-2 select-none"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
              <span className="text-[10px] bg-[var(--color-bg-card)] px-2 py-0.5 rounded font-medium ml-1">
                {isExpanded ? 'Month View' : 'Week View'}
              </span>
            </h3>
            
            {isExpanded && (
               <div className="flex gap-1 ml-2">
                 <button 
                   onClick={() => setCurrentDate(new Date(currentDate.setMonth(currentDate.getMonth() - 1)))}
                   className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] px-2 py-1 bg-[var(--color-bg-card)] rounded text-xs"
                 >
                   &larr; Prev
                 </button>
                 <button 
                   onClick={() => setCurrentDate(new Date(currentDate.setMonth(currentDate.getMonth() + 1)))}
                   className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] px-2 py-1 bg-[var(--color-bg-card)] rounded text-xs"
                 >
                   Next &rarr;
                 </button>
               </div>
            )}
          </div>
          <button onClick={() => { setSelectedDate(new Date()); setShowModal(true); }} className="bg-[var(--color-bg-card)] hover:bg-[var(--color-bg-card)] text-[var(--color-text-primary)] text-xs font-medium px-3 py-1.5 rounded-lg transition-colors border border-[var(--color-border)]">
            + Manual Post
          </button>
        </div>
        
        <div className="grid grid-cols-7 gap-3 mb-2">
          {weekDaysLabels.map(label => (
            <div key={label} className="text-center text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest">{label}</div>
          ))}
        </div>
        
        <div className="grid grid-cols-7 gap-3 min-h-[120px] transition-all">
          {daysToRender.map((dayObj, idx) => {
            const dayPosts = getPostsForDay(dayObj.date);
            const isDayToday = isToday(dayObj.date);
            
            return (
              <div 
                key={idx} 
                onClick={() => handleDayClick(dayObj)}
                className={`rounded-xl p-3 flex flex-col gap-1.5 cursor-pointer hover:bg-white/[0.02] transition-colors overflow-hidden ${
                  !dayObj.isCurrentMonth ? 'opacity-30' : ''
                } ${
                  isDayToday ? 'bg-[var(--color-bg-card)] border border-[var(--color-accent-primary)]/50 shadow-[0_0_15px_rgba(79,70,229,0.15)] ring-1 ring-[var(--color-accent-primary)]/50' : 'bg-[var(--color-bg-card)] border border-[var(--color-border)]'
                }`}
                style={{ minHeight: isExpanded ? '100px' : '120px' }}
              >
                <div className={`text-sm font-bold mb-1 flex justify-between items-center ${isDayToday ? 'text-[var(--color-accent-primary)]' : 'text-[var(--color-text-secondary)]'}`}>
                   <span>{dayObj.date.getDate()}</span>
                   <span className="opacity-0 hover:opacity-100 text-[var(--color-accent-primary)] hover:font-bold border border-[var(--color-border)] rounded px-1 transition-all">
                     +
                   </span>
                </div>
                
                <div className="flex flex-col gap-1 overflow-y-auto custom-scrollbar pr-1">
                  {dayPosts.map((post, i) => {
                    const platform = post.platform?.toLowerCase() || "";
                    const typeColor = 
                      platform === 'linkedin' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                      platform.includes('twitter') || platform.includes('x') ? 'bg-gray-500/20 text-gray-300 border border-gray-500/30' :
                      'bg-pink-500/20 text-pink-400 border border-pink-500/30';
                      
                    return (
                      <div 
                        key={i} 
                        className={`text-[9px] font-medium py-1.5 px-2 rounded-md truncate transition-transform hover:scale-105 ${typeColor}`}
                        title={post.content_drafts?.topic || 'Scheduled Post'}
                      >
                        {post.platform}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card border border-[var(--color-border)] rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">System Connections</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center pb-3 border-b border-[var(--color-border)]">
              <div className="text-sm text-[var(--color-text-secondary)]">LinkedIn API</div>
              <div className="text-[10px] text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Connected</div>
            </div>
            <div className="flex justify-between items-center pb-3 border-b border-[var(--color-border)]">
              <div className="text-sm text-[var(--color-text-secondary)]">X (Twitter) v2</div>
              <div className="text-[10px] text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Connected</div>
            </div>
            <div className="flex justify-between items-center pb-3 border-b border-[var(--color-border)]">
              <div className="text-sm text-[var(--color-text-secondary)]">Instagram Graph API</div>
              <div className="text-[10px] text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Auth Needed</div>
            </div>
            <div className="flex justify-between items-center">
              <div className="text-sm text-[var(--color-text-secondary)]">Puppeteer Renderer (IG)</div>
              <div className="text-[10px] text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded font-bold uppercase tracking-wider">Active</div>
            </div>
          </div>
        </div>

        <div className="glass-card border border-[var(--color-border)] rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">Next Auto-Post Scheduled</h3>
          
          {nextPost ? (
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-xl p-5 mb-4 shadow-inner">
              <div className="flex justify-between items-start mb-3">
                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${
                  nextPost.platform.toLowerCase() === 'linkedin' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                  nextPost.platform.toLowerCase() === 'twitter' ? 'bg-gray-500/20 text-gray-300 border border-gray-500/30' :
                  'bg-pink-500/20 text-pink-400 border border-pink-500/30'
                }`}>
                  {nextPost.platform}
                </span>
                <span className="text-xs font-semibold text-indigo-300">
                  {new Date(nextPost.scheduled_for).toLocaleString([], { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <div className="text-sm text-[var(--color-text-secondary)] line-clamp-3">
                {nextPost.content_drafts?.content || "No content preview available."}
              </div>
            </div>
          ) : (
            <div className="bg-[var(--color-bg-card)] border border-[var(--color-border)] border-dashed rounded-xl p-6 mb-4 text-center">
               <span className="text-[var(--color-text-muted)] text-sm">No upcoming posts scheduled.</span>
            </div>
          )}
          
          <button className="w-full bg-[var(--color-bg-card)] hover:bg-[var(--color-bg-card)] text-[var(--color-text-primary)] text-xs font-medium py-2.5 rounded-xl transition-colors border border-[var(--color-border)] disabled:opacity-50" disabled={!nextPost}>
            Pause Queue
          </button>
        </div>
      </div>

      {showModal && selectedDate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[var(--color-bg-primary)]/60 backdrop-blur-md">
          <div className="glass-modal border border-[var(--color-border)] p-6 rounded-2xl w-full max-w-sm shadow-2xl relative">
            <button 
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
            >
              &times;
            </button>
            <h3 className="text-xl font-[family-name:var(--font-heading)] font-bold text-[var(--color-text-primary)] mb-1">Schedule Post</h3>
            <p className="text-sm text-indigo-300 font-medium mb-6">
              For {selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
            </p>
            
            <label className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest font-bold mb-2 block">Platform</label>
            <select className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-sm text-[var(--color-text-primary)] mb-4 focus:outline-none focus:border-[var(--color-accent-primary)]">
              <option value="linkedin">LinkedIn</option>
              <option value="twitter">X (Twitter)</option>
              <option value="instagram">Instagram</option>
            </select>
            
            <label className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest font-bold mb-2 block">Time</label>
            <input 
              type="time" 
              className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-4 py-2.5 text-sm text-[var(--color-text-primary)] mb-6 focus:outline-none focus:border-[var(--color-accent-primary)]" 
              defaultValue="10:00" 
            />
            
            <div className="bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/10 border border-[var(--color-accent-primary)]/20 text-indigo-300 text-xs p-3 rounded-lg mb-6">
               Note: Currently scheduling dummy placeholders. To schedule real content, approve a draft from the Review screen.
            </div>
            
            <div className="flex gap-3">
              <button onClick={() => setShowModal(false)} className="flex-1 bg-[var(--color-bg-card)] hover:bg-[var(--color-bg-card)] text-[var(--color-text-primary)] font-medium rounded-xl py-2.5 transition-colors border border-[var(--color-border)] text-sm">Cancel</button>
              <button 
                onClick={() => {
                   alert("Scheduling interaction noted. To wire this up, backend needs a draft_id.");
                   setShowModal(false);
                }} 
                className="flex-1 bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] hover:bg-[var(--color-accent-hover)] text-[var(--color-text-primary)] font-medium rounded-xl py-2.5 shadow-lg shadow-none transition-colors border border-[var(--color-accent-primary)] text-sm"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
