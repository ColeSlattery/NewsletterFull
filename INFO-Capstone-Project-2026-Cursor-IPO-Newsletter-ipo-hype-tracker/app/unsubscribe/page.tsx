'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

export default function UnsubscribePage() {
  const searchParams = useSearchParams();
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSuccess, setIsSuccess] = useState(false);
  const [email, setEmail] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setMessage('Invalid unsubscribe link. Please check your email for the correct link.');
      setIsLoading(false);
      return;
    }

    const handleUnsubscribe = async () => {
      try {
        const response = await fetch(`/api/unsubscribe?token=${encodeURIComponent(token)}`, {
          method: 'GET',
        });

        const data = await response.json();

        if (response.ok) {
          setIsSuccess(true);
          setMessage(data.message);
          setEmail(data.email);
        } else {
          setIsSuccess(false);
          setMessage(data.error);
        }
      } catch (error) {
        setIsSuccess(false);
        setMessage('An error occurred while processing your unsubscribe request.');
      } finally {
        setIsLoading(false);
      }
    };

    handleUnsubscribe();
  }, [searchParams]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8 md:p-12">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              {isLoading ? (
                <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
              ) : isSuccess ? (
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 font-raleway">
              {isLoading ? 'Processing...' : isSuccess ? 'Unsubscribed Successfully' : 'Unsubscribe Failed'}
            </h1>
          </div>

          {/* Content */}
          <div className="text-center">
            {isLoading ? (
              <p className="text-lg text-gray-600 font-raleway">
                Processing your unsubscribe request...
              </p>
            ) : (
              <>
                <div className={`p-4 rounded-lg mb-6 ${isSuccess ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                  <p className="font-raleway">{message}</p>
                  {isSuccess && email && (
                    <p className="mt-2 text-sm font-raleway">
                      Email: <span className="font-medium">{email}</span>
                    </p>
                  )}
                </div>

                {isSuccess && (
                  <div className="space-y-4">
                    <p className="text-gray-600 font-raleway">
                      You have been successfully unsubscribed from the IPO Hype Tracker newsletter.
                    </p>
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="text-sm text-blue-800 font-raleway">
                        <strong>Note:</strong> If you change your mind, you can always subscribe again by visiting our homepage.
                      </p>
                    </div>
                    <a
                      href="/"
                      className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium font-raleway"
                    >
                      Return to Homepage
                    </a>
                  </div>
                )}

                {!isSuccess && (
                  <div className="space-y-4">
                    <p className="text-gray-600 font-raleway">
                      There was an issue processing your unsubscribe request. This could be due to:
                    </p>
                    <ul className="text-left text-gray-600 space-y-1 font-raleway">
                      <li>• Invalid or expired unsubscribe link</li>
                      <li>• Network connection issues</li>
                      <li>• Server temporarily unavailable</li>
                    </ul>
                    <div className="pt-4">
                      <a
                        href="/"
                        className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium font-raleway"
                      >
                        Return to Homepage
                      </a>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
