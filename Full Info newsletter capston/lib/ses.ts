import { SESClient, SendEmailCommand } from '@aws-sdk/client-ses';

// Initialize AWS SES client
const sesClient = new SESClient({
  region: process.env.AWS_REGION || 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

export { sesClient };

// Email configuration
export const EMAIL_CONFIG = {
  from: 'brandon.h.lui@gmail.com', // Using your verified email (no display name in sandbox mode)
  replyTo: 'brandon.h.lui@gmail.com', // Using your verified email
  subject: 'IPO Hype Tracker - Weekly Market Update',
} as const;

// Email sending function
export async function sendEmail({
  to,
  subject,
  html,
  text,
}: {
  to: string | string[];
  subject: string;
  html: string;
  text?: string;
}) {
  try {
    const recipients = Array.isArray(to) ? to : [to];
    
    const command = new SendEmailCommand({
      Source: EMAIL_CONFIG.from,
      Destination: {
        ToAddresses: recipients,
      },
      Message: {
        Subject: {
          Data: subject,
          Charset: 'UTF-8',
        },
        Body: {
          Html: {
            Data: html,
            Charset: 'UTF-8',
          },
          ...(text && {
            Text: {
              Data: text,
              Charset: 'UTF-8',
            },
          }),
        },
      },
    });

    const response = await sesClient.send(command);
    console.log('Email sent successfully:', response.MessageId);
    return response;
  } catch (error) {
    console.error('Error sending email:', error);
    throw error;
  }
}

// Bulk email sending for newsletters
export async function sendBulkEmails({
  recipients,
  subject,
  html,
  text,
  batchSize = 50,
}: {
  recipients: string[];
  subject: string;
  html: string;
  text?: string;
  batchSize?: number;
}) {
  const results = [];
  const errors = [];

  // Send emails in batches to respect SES limits
  for (let i = 0; i < recipients.length; i += batchSize) {
    const batch = recipients.slice(i, i + batchSize);
    
    try {
      const result = await sendEmail({
        to: batch,
        subject,
        html,
        text,
      });
      
      results.push({
        batch: i / batchSize + 1,
        recipients: batch.length,
        messageId: result.MessageId,
      });
      
      // Add delay between batches to respect rate limits
      if (i + batchSize < recipients.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    } catch (error) {
      errors.push({
        batch: i / batchSize + 1,
        recipients: batch,
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }

  return {
    successful: results,
    failed: errors,
    totalSent: results.reduce((sum, r) => sum + r.recipients, 0),
    totalFailed: errors.reduce((sum, e) => sum + e.recipients.length, 0),
  };
}

// TODO for Developer:
// 1. Set up AWS account and get access keys
// 2. Verify your domain in AWS SES console
// 3. Add AWS credentials to .env.local:
//    AWS_ACCESS_KEY_ID=your_access_key
//    AWS_SECRET_ACCESS_KEY=your_secret_key
//    AWS_REGION=us-east-1
// 4. Update the 'from' and 'replyTo' fields above with your verified domain
