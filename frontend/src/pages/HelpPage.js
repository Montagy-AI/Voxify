import React from 'react';
import { useNavigate } from 'react-router-dom';

const HelpPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-black text-white px-4 py-12">
      <div className="max-w-3xl mx-auto">
        <div className="bg-zinc-800 rounded-xl shadow-lg p-8 space-y-6">
          <h1 className="text-4xl font-bold">Welcome to Voxify</h1>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-gray-200">
              What is Voxify?
            </h2>
            <p className="text-gray-300">
              Voxify is an AI-powered platform for voice cloning and
              text-to-speech generation. This project focuses on building the
              core infrastructure — including APIs, model pipelines, data
              handling, and security.
            </p>
            <p className="text-gray-300">
              Our backend services are built using <strong>Python</strong> and{' '}
              <strong>Flask</strong>, with <strong>SQLite</strong> and{' '}
              <strong>ChromaDB</strong> for data storage. We use{' '}
              <strong>F5-TTS</strong> for high-quality voice synthesis,
              leveraging open-source AI models.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-gray-200">
              Using the Dashboard
            </h2>
            <p className="text-gray-300">From your dashboard, you can:</p>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              <li>
                Click <strong>"Clone Your Voice"</strong> to create your own
                voice clone.
              </li>
              <li>
                Use <strong>"Text-To-Speech"</strong> to generate audio using
                your cloned voice.
              </li>
            </ul>
          </section>

          <section className="space-y-3">
            <h2 className="text-xl font-semibold text-gray-200">Navigation</h2>
            <ul className="list-disc list-inside text-gray-300 space-y-1">
              <li>
                View all your cloned voices by clicking{' '}
                <strong>"Voices"</strong> in the top toolbar.
              </li>
              <li>
                Access your generated audio clips via <strong>"Tasks"</strong>{' '}
                or by clicking <strong>"View All Tasks"</strong> at the bottom
                of the page.
              </li>
              <li>
                Update your email or password from the{' '}
                <strong>"Settings"</strong> tab.
              </li>
            </ul>
          </section>

          {/* Action buttons */}
          <div className="pt-6 flex justify-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="bg-black text-white px-6 py-3 rounded-md hover:bg-white hover:text-black transition-colors"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => navigate('/voice-clone')}
              className="bg-black text-white px-6 py-3 rounded-md hover:bg-white hover:text-black transition-colors"
            >
              Clone Your Voice
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HelpPage;
