import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { subscribers } from '@/db/schema';
import { eq } from 'drizzle-orm';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const token = searchParams.get('token');

    if (!token) {
      return NextResponse.json(
        { error: 'Unsubscribe token is required' },
        { status: 400 }
      );
    }

    // Find subscriber by token
    const subscriber = await db
      .select()
      .from(subscribers)
      .where(eq(subscribers.unsubToken, token))
      .limit(1);

    if (subscriber.length === 0) {
      return NextResponse.json(
        { error: 'Invalid unsubscribe token' },
        { status: 404 }
      );
    }

    // Update status to unsubscribed
    await db
      .update(subscribers)
      .set({ status: 'unsubscribed' })
      .where(eq(subscribers.unsubToken, token));

    return NextResponse.json(
      { 
        message: 'Successfully unsubscribed from IPO Hype Tracker newsletter',
        email: subscriber[0].email
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Unsubscribe error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
