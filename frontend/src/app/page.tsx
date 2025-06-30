'use client';

import { useState } from 'react';
import AssessmentDashboard from './components/AssessmentDashboard';
import LiveInterview from './components/LiveInterview';

export default function Home() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'interview'>('dashboard');

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Tech4Good Live Assessment
              </h1>
            </div>
            <nav className="flex space-x-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'dashboard'
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                    : 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('interview')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentView === 'interview'
                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                    : 'text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white'
                }`}
              >
                Live Interview
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'dashboard' ? (
          <AssessmentDashboard />
        ) : (
          <LiveInterview />
        )}
      </main>
    </div>
  );
}
