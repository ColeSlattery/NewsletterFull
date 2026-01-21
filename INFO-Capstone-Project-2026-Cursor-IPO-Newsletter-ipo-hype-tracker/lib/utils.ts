// TODO: Add utility functions for:
// - Email validation
// - Date formatting
// - Data processing for IPO filings
// - Newsletter content generation

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export function generateUnsubToken(): string {
  // This is handled by uuid in the API routes
  return '';
}
