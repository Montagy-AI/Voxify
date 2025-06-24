import React from 'react';
import { Link } from 'react-router-dom';
import authService from '../services/auth.service';

const Dashboard = () => {
  const user = authService.getCurrentUser();
  const firstName = user?.first_name || 'there';

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-4">
          Welcome back, {firstName}!
        </h1>
        <p className="text-gray-400 mb-8">
          Ready to start a new task? Choose an option below.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link
            to="/tasks/voice-clone"
            className="group bg-zinc-900 rounded-lg p-6 hover:bg-zinc-800 transition-colors border border-zinc-800"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Clone Your Voice</h2>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6 text-white group-hover:translate-x-1 transition-transform"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </div>
            <p className="text-gray-400">
              Create a digital copy of your voice that can speak any text naturally.
            </p>
          </Link>

          <Link
            to="/tasks/text-to-speech"
            className="group bg-zinc-900 rounded-lg p-6 hover:bg-zinc-800 transition-colors border border-zinc-800"
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Text-to-Speech</h2>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6 text-white group-hover:translate-x-1 transition-transform"
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </div>
            <p className="text-gray-400">
              Convert any text into natural-sounding speech using your voice clones.
            </p>
          </Link>
        </div>

        {/* Quick Stats */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
            <h3 className="text-gray-400 text-sm mb-2">Voice Clones</h3>
            <p className="text-2xl font-semibold">3</p>
          </div>
          <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
            <h3 className="text-gray-400 text-sm mb-2">Completed Tasks</h3>
            <p className="text-2xl font-semibold">12</p>
          </div>
          <div className="bg-zinc-900 rounded-lg p-6 border border-zinc-800">
            <h3 className="text-gray-400 text-sm mb-2">Processing</h3>
            <p className="text-2xl font-semibold">1</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 