import React from 'react';
import { Link } from 'react-router-dom';

const Landing = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-zinc-900 to-black text-white relative overflow-hidden">
      {/* Global Background Elements */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Base gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/3 via-transparent to-purple-500/3"></div>
        {/* Large decorative blurs */}
        <div className="absolute top-20 left-10 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl"></div>
        <div className="absolute top-1/3 right-10 w-80 h-80 bg-purple-500/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 left-1/3 w-64 h-64 bg-blue-400/4 rounded-full blur-2xl"></div>
        {/* Floating particles */}
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400/20 rounded-full animate-bounce delay-700"></div>
        <div className="absolute top-1/3 right-1/3 w-1 h-1 bg-purple-400/30 rounded-full animate-pulse delay-1000"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-blue-300/10 rounded-full animate-bounce delay-500"></div>
        <div className="absolute top-1/2 right-1/4 w-2 h-2 bg-purple-300/20 rounded-full animate-pulse delay-300"></div>
        <div className="absolute bottom-1/3 right-1/5 w-1 h-1 bg-blue-400/25 rounded-full animate-bounce delay-1200"></div>
      </div>

      {/* Hero Section */}
      <div className="relative">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16 text-center lg:pt-32 z-10">
          <div className="mx-auto max-w-4xl">
            <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl">
              Clone Your Voice with
              <span className="block text-white">AI Precision</span>
            </h1>
            <p className="mt-6 text-lg leading-8 text-gray-400 max-w-2xl mx-auto">
              Create stunning voice clones and convert text to speech with advanced AI technology. 
              Experience natural-sounding voices with multilingual support and professional quality.
            </p>
                         <div className="mt-10 flex items-center justify-center gap-x-6">
               <Link
                 to="/register"
                 className="rounded-md bg-white px-6 py-3 text-sm font-semibold text-black shadow-sm hover:bg-gray-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200 cursor-pointer transform hover:scale-105 active:scale-95"
               >
                 Get Started Free
               </Link>
               <Link
                 to="/login"
                 className="text-sm font-semibold leading-6 text-white border border-zinc-800 px-6 py-3 rounded-md hover:bg-zinc-800 hover:border-zinc-600 transition-all duration-200 cursor-pointer transform hover:scale-105 active:scale-95"
               >
                 Sign In <span aria-hidden="true">→</span>
               </Link>
             </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative py-24">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Powerful Voice AI Features
            </h2>
            <p className="mt-4 text-lg text-gray-400">
              Everything you need to create professional voice content
            </p>
          </div>

          <div className="mt-20 grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-3">
            {/* Voice Cloning */}
            <div className="relative bg-black p-8 rounded-lg border border-zinc-800">
              <div className="flex items-center justify-center h-12 w-12 rounded-md bg-blue-500/10 border border-blue-800 mb-6">
                <svg
                  className="h-6 w-6 text-blue-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M19 114a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Voice Cloning</h3>
              <p className="text-gray-400">
                Create high-quality voice clones from just a few seconds of audio. 
                Your digital voice that sounds incredibly natural.
              </p>
            </div>

            {/* Text-to-Speech */}
            <div className="relative bg-black p-8 rounded-lg border border-zinc-800">
              <div className="flex items-center justify-center h-12 w-12 rounded-md bg-green-500/10 border border-green-800 mb-6">
                <svg
                  className="h-6 w-6 text-green-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.627 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Text-to-Speech</h3>
              <p className="text-gray-400">
                Convert any text into natural-sounding speech using your cloned voices. 
                Perfect for content creation and accessibility.
              </p>
            </div>

            {/* Multilingual Support */}
            <div className="relative bg-black p-8 rounded-lg border border-zinc-800">
              <div className="flex items-center justify-center h-12 w-12 rounded-md bg-purple-500/10 border border-purple-800 mb-6">
                <svg
                  className="h-6 w-6 text-purple-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth="1.5"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="m10.5 21 5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 0 1 6-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 0 1-3.827-5.802"
                  />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Multilingual Support</h3>
              <p className="text-gray-400">
                Support for multiple languages including English, Chinese, Japanese, 
                French, German, Spanish, and more.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="relative py-24">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              How It Works
            </h2>
            <p className="mt-4 text-lg text-gray-400">
              Create professional voice content in three simple steps
            </p>
          </div>

          <div className="mt-20">
            <div className="grid grid-cols-1 gap-12 lg:grid-cols-3">
              {/* Step 1 */}
              <div className="text-center">
                <div className="flex items-center justify-center h-16 w-16 rounded-full bg-zinc-900 border border-zinc-800 mx-auto mb-6">
                  <span className="text-xl font-bold text-white">1</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-4">Record Your Voice</h3>
                <p className="text-gray-400">
                  Upload a high-quality audio sample of your voice. Just a few seconds 
                  is enough to create an accurate clone.
                </p>
              </div>

              {/* Step 2 */}
              <div className="text-center">
                <div className="flex items-center justify-center h-16 w-16 rounded-full bg-zinc-900 border border-zinc-800 mx-auto mb-6">
                  <span className="text-xl font-bold text-white">2</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-4">AI Processing</h3>
                <p className="text-gray-400">
                  Our advanced AI analyzes your voice patterns and creates a 
                  high-fidelity digital representation.
                </p>
              </div>

              {/* Step 3 */}
              <div className="text-center">
                <div className="flex items-center justify-center h-16 w-16 rounded-full bg-zinc-900 border border-zinc-800 mx-auto mb-6">
                  <span className="text-xl font-bold text-white">3</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-4">Generate Speech</h3>
                <p className="text-gray-400">
                  Type any text and hear it spoken in your cloned voice. 
                  Download the audio for any use case.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Benefits Section */}
      <div className="relative py-24">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
          <div className="lg:grid lg:grid-cols-2 lg:gap-16 lg:items-center">
            <div>
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                Why Choose Voxify?
              </h2>
              <p className="mt-4 text-lg text-gray-400">
                Professional-grade voice AI technology that delivers exceptional results
              </p>

              <div className="mt-12 space-y-8">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-500/10 border border-blue-800">
                      <svg
                        className="h-4 w-4 text-blue-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-white">High-Quality Audio</h3>
                    <p className="mt-2 text-gray-400">
                      Generate crystal-clear audio with natural intonation and emotion
                    </p>
                  </div>
                </div>

                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-500/10 border border-blue-800">
                      <svg
                        className="h-4 w-4 text-blue-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-white">Fast Processing</h3>
                    <p className="mt-2 text-gray-400">
                      Quick voice cloning and text-to-speech generation in seconds
                    </p>
                  </div>
                </div>

                <div className="flex">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-8 w-8 rounded-md bg-blue-500/10 border border-blue-800">
                      <svg
                        className="h-4 w-4 text-blue-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-white">Secure & Private</h3>
                    <p className="mt-2 text-gray-400">
                      Your voice data is encrypted and protected with enterprise-grade security
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-12 lg:mt-0">
              <div className="bg-black rounded-lg p-8 border border-zinc-800">
                <div className="space-y-6">
                  <div className="flex items-center">
                    <div className="h-10 w-10 rounded-full bg-orange-500 flex items-center justify-center">
                      <span className="text-sm font-medium text-white">U</span>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-white">User Voice Sample</p>
                      <p className="text-xs text-gray-400">2.3 seconds • High quality</p>
                    </div>
                  </div>
                  
                  <div className="border-l-2 border-zinc-800 pl-4 ml-5">
                    <div className="space-y-3">
                      <div className="flex items-center text-sm">
                        <div className="h-2 w-2 rounded-full bg-blue-400 mr-3"></div>
                        <span className="text-gray-400">Analyzing voice patterns...</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <div className="h-2 w-2 rounded-full bg-green-400 mr-3"></div>
                        <span className="text-gray-400">Creating neural model...</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <div className="h-2 w-2 rounded-full bg-green-400 mr-3"></div>
                        <span className="text-gray-400">Voice clone ready!</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-zinc-900 rounded-lg p-4 border border-zinc-800">
                    <p className="text-sm text-gray-400 mb-2">Generated Text-to-Speech:</p>
                    <p className="text-white italic">"Hello! This is my cloned voice speaking any text naturally."</p>
                    <div className="mt-3 flex items-center">
                      <button className="text-blue-400 hover:text-blue-300 transition-colors">
                        <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                        </svg>
                      </button>
                      <span className="ml-2 text-xs text-gray-400">0:03</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative py-16">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center z-10">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ready to Clone Your Voice?
          </h2>
          <p className="mt-4 text-lg text-gray-400 max-w-2xl mx-auto">
            Join us in creating professional voice content with Voxify. 
          </p>
                     <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
             <Link
               to="/register"
               className="rounded-md bg-white px-8 py-3 text-base font-semibold text-black shadow-sm hover:bg-gray-200 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-all duration-200 cursor-pointer transform hover:scale-105 active:scale-95"
             >
               Start Trial
             </Link>
             <Link
               to="/help"
               className="rounded-md border border-zinc-800 px-8 py-3 text-base font-semibold text-white hover:bg-zinc-800 hover:border-zinc-600 transition-all duration-200 cursor-pointer transform hover:scale-105 active:scale-95"
             >
               Learn More
             </Link>
           </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative border-t border-zinc-800/50">
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 z-10">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <h3 className="text-lg font-semibold text-white mb-4">Voxify</h3>
              <p className="text-gray-400 text-sm max-w-md">
                Advanced AI voice cloning and text-to-speech technology. 
                Create natural-sounding voices for any application.
              </p>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/voice-clone" className="hover:text-white transition-colors">Voice Cloning</Link></li>
                <li><Link to="/text-to-speech" className="hover:text-white transition-colors">Text-to-Speech</Link></li>
                <li><Link to="/help" className="hover:text-white transition-colors">Documentation</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-sm font-semibold text-white mb-4">Account</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/login" className="hover:text-white transition-colors">Sign In</Link></li>
                <li><Link to="/register" className="hover:text-white transition-colors">Create Account</Link></li>
                <li><Link to="/settings" className="hover:text-white transition-colors">Settings</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="mt-8 pt-8 border-t border-zinc-800 text-center">
            <p className="text-xs text-gray-400">
              © 2025 Voxify. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
