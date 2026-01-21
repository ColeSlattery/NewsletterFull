'use client';

import { useState } from 'react';

export default function Home() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsSuccess(true);
        setMessage(data.message);
        setEmail('');
      } else {
        setIsSuccess(false);
        setMessage(data.error);
      }
    } catch (error) {
      setIsSuccess(false);
      setMessage('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="py-4 bg-black sm:py-6">
        <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="shrink-0">
              <a href="#" title="" className="flex">
                <span className="text-2xl font-bold text-white font-raleway">IPO Hype Tracker</span>
              </a>
            </div>

            <div className="flex md:hidden">
              <button type="button" className="text-white">
                <svg className="w-7 h-7" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>

            <nav className="hidden ml-10 mr-auto space-x-10 lg:ml-20 lg:space-x-12 md:flex md:items-center md:justify-start">
              <a href="#features" className="text-base font-normal text-gray-400 transition-all duration-200 hover:text-white font-raleway">Features</a>
              <a href="#newsletter" className="text-base font-normal text-gray-400 transition-all duration-200 hover:text-white font-raleway">Newsletter</a>
              <a href="#about" className="text-base font-normal text-gray-400 transition-all duration-200 hover:text-white font-raleway">About</a>
            </nav>

            <div className="relative hidden md:items-center md:justify-center md:inline-flex group">
              <div className="absolute transition-all duration-200 rounded-full -inset-px bg-gradient-to-r from-cyan-500 to-purple-500 group-hover:shadow-lg group-hover:shadow-cyan-500/50"></div>
              <a href="#newsletter" className="relative inline-flex items-center justify-center px-6 py-2 text-base font-normal text-white bg-black border border-transparent rounded-full font-raleway" role="button">Subscribe Now</a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-12 overflow-hidden bg-black sm:pb-16 lg:pb-20 xl:pb-24">
        <div className="px-4 mx-auto relative sm:px-6 lg:px-8 max-w-7xl">
          <div className="grid items-center grid-cols-1 gap-y-12 lg:grid-cols-2 gap-x-16">
            <div>
              <h1 className="text-4xl font-normal text-white sm:text-5xl lg:text-6xl xl:text-7xl font-raleway">Stay Ahead of the IPO Market</h1>
              <p className="mt-4 text-lg font-normal text-gray-400 sm:mt-8 font-raleway">
                Get comprehensive IPO tracking, market sentiment analysis, and weekly insights delivered directly to your inbox. 
                Join thousands of investors who rely on our data-driven approach.
              </p>

              <form onSubmit={handleSubmit} className="relative mt-8 rounded-full sm:mt-12">
                <div className="relative">
                  <div className="absolute rounded-full -inset-px bg-gradient-to-r from-cyan-500 to-purple-500"></div>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-6">
                      <svg className="w-5 h-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <input 
                      type="email" 
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Enter your email address" 
                      className="block w-full py-4 pr-6 text-white placeholder-gray-500 bg-black border border-transparent rounded-full pl-14 sm:py-5 focus:border-transparent focus:ring-0 font-raleway" 
                      required
                      disabled={isLoading}
                    />
                  </div>
                </div>
                <div className="sm:absolute flex sm:right-1.5 sm:inset-y-1.5 mt-4 sm:mt-0">
                  <button 
                    type="submit" 
                    disabled={isLoading}
                    className="inline-flex items-center justify-center w-full px-5 py-5 text-sm font-semibold tracking-widest text-black uppercase transition-all duration-200 bg-white rounded-full sm:w-auto sm:py-3 hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed font-raleway"
                  >
                    {isLoading ? 'Subscribing...' : 'Subscribe'}
                  </button>
                </div>
              </form>

              {/* Message */}
              {message && (
                <div className={`mt-4 p-4 rounded-lg ${isSuccess ? 'bg-green-900/20 text-green-400 border border-green-500/20' : 'bg-red-900/20 text-red-400 border border-red-500/20'}`}>
                  <p className="font-raleway text-sm">{message}</p>
                </div>
              )}

              <div className="mt-8 sm:mt-12">
                <p className="text-lg font-normal text-white font-raleway">Trusted by 10k+ investors</p>

                <div className="flex items-center mt-3">
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <svg key={i} className="w-5 h-5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                          d="M10.8586 4.71248C11.2178 3.60691 12.7819 3.60691 13.1412 4.71248L14.4246 8.66264C14.5853 9.15706 15.046 9.49182 15.5659 9.49182H19.7193C20.8818 9.49182 21.3651 10.9794 20.4247 11.6626L17.0645 14.104C16.6439 14.4095 16.4679 14.9512 16.6286 15.4456L17.912 19.3958C18.2713 20.5013 17.0059 21.4207 16.0654 20.7374L12.7052 18.2961C12.2846 17.9905 11.7151 17.9905 11.2945 18.2961L7.93434 20.7374C6.99388 21.4207 5.72851 20.5013 6.08773 19.3958L7.37121 15.4456C7.53186 14.9512 7.35587 14.4095 6.93529 14.104L3.57508 11.6626C2.63463 10.9794 3.11796 9.49182 4.28043 9.49182H8.43387C8.95374 9.49182 9.41448 9.15706 9.57513 8.66264L10.8586 4.71248Z"
                          fill="url(#star-gradient)"
                        />
                        <defs>
                          <linearGradient id="star-gradient" x1="3.07813" y1="3.8833" x2="23.0483" y2="6.90161" gradientUnits="userSpaceOnUse">
                            <stop offset="0%" stopColor="#06b6d4" />
                            <stop offset="100%" stopColor="#8b5cf6" />
                          </linearGradient>
                        </defs>
                      </svg>
                    ))}
                  </div>
                  <span className="ml-2 text-base font-normal text-white font-raleway"> 4.8/5 </span>
                  <span className="ml-1 text-base font-normal text-gray-500 font-raleway"> (2.1k Reviews) </span>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="absolute inset-0">
                <svg className="blur-3xl filter opacity-70" style={{filter: 'blur(64px)'}} width="444" height="536" viewBox="0 0 444 536" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M225.919 112.719C343.98 64.6648 389.388 -70.487 437.442 47.574C485.496 165.635 253.266 481.381 135.205 529.435C17.1445 577.488 57.9596 339.654 9.9057 221.593C-38.1482 103.532 107.858 160.773 225.919 112.719Z" fill="url(#hero-gradient)" />
                  <defs>
                    <linearGradient id="hero-gradient" x1="82.7339" y1="550.792" x2="-39.945" y2="118.965" gradientUnits="userSpaceOnUse">
                      <stop offset="0%" stopColor="#06b6d4" />
                      <stop offset="100%" stopColor="#8b5cf6" />
                    </linearGradient>
                  </defs>
                </svg>
              </div>

              <div className="absolute inset-0">
                <img className="object-cover w-full h-full opacity-50" src="https://landingfoliocom.imgix.net/store/collection/dusk/images/noise.png" alt="" />
              </div>

              {/* IPO Chart Illustration */}
              <div className="relative w-full max-w-md mx-auto bg-gray-900/50 backdrop-blur-sm rounded-2xl p-6 border border-gray-800">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-white font-raleway">Top IPO Trends</h3>
                    <span className="text-sm text-green-400 font-raleway">+12.5%</span>
                  </div>
                  
                  {/* Mock Chart */}
                  <div className="h-32 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-lg p-4 flex items-end justify-between">
                    {[40, 65, 45, 80, 60, 90, 75].map((height, i) => (
                      <div key={i} className="bg-gradient-to-t from-cyan-500 to-purple-500 rounded-t" style={{height: `${height}%`, width: '12%'}}></div>
                    ))}
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-400 font-raleway">Active IPOs</p>
                      <p className="text-white font-bold font-raleway">47</p>
                    </div>
                    <div>
                      <p className="text-gray-400 font-raleway">Avg. Return</p>
                      <p className="text-green-400 font-bold font-raleway">+18.2%</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 bg-gray-900/50">
        <div className="px-4 mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-white sm:text-4xl font-raleway">Why Choose IPO Hype Tracker?</h2>
            <p className="mt-4 text-lg text-gray-400 font-raleway">Comprehensive IPO market intelligence at your fingertips</p>
          </div>

          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            <div className="p-6 bg-gray-800/50 rounded-xl border border-gray-700">
              <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2 font-raleway">Real-time Tracking</h3>
              <p className="text-gray-400 font-raleway">Monitor IPO filings, market sentiment, and search trends in real-time with our advanced data pipeline.</p>
            </div>

            <div className="p-6 bg-gray-800/50 rounded-xl border border-gray-700">
              <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2 font-raleway">Trend Analysis</h3>
              <p className="text-gray-400 font-raleway">Get insights on market trends, investor sentiment, and performance analytics with our AI-powered analysis.</p>
            </div>

            <div className="p-6 bg-gray-800/50 rounded-xl border border-gray-700">
              <div className="w-12 h-12 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-white mb-2 font-raleway">Weekly Newsletter</h3>
              <p className="text-gray-400 font-raleway">Receive curated insights, top IPO picks, and market analysis delivered directly to your inbox every week.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="newsletter" className="py-16 bg-black">
        <div className="px-4 mx-auto max-w-4xl sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white sm:text-4xl font-raleway">Ready to Stay Ahead?</h2>
          <p className="mt-4 text-lg text-gray-400 font-raleway">Join thousands of investors who rely on our data-driven IPO insights</p>
          
          <div className="mt-8">
            <div className="relative inline-flex items-center justify-center group">
              <div className="absolute transition-all duration-200 rounded-full -inset-px bg-gradient-to-r from-cyan-500 to-purple-500 group-hover:shadow-lg group-hover:shadow-cyan-500/50"></div>
              <a href="#newsletter" className="relative inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-white bg-black border border-transparent rounded-full font-raleway">
                Start Your Free Subscription
              </a>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
