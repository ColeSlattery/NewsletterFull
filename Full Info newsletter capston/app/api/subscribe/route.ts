import { NextRequest, NextResponse } from 'next/server';
import { db } from '@/lib/db';
import { subscribers } from '@/db/schema';
import { v4 as uuidv4 } from 'uuid';
import { eq } from 'drizzle-orm';

export async function POST(request: NextRequest) {
  try {
    const { email } = await request.json();

    if (!email || typeof email !== 'string') {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      );
    }

    // Check if email already exists
    const existingSubscriber = await db
      .select()
      .from(subscribers)
      .where(eq(subscribers.email, email.toLowerCase()))
      .limit(1);

    if (existingSubscriber.length > 0) {
      if (existingSubscriber[0].status === 'subscribed') {
        return NextResponse.json(
          { message: 'Email is already subscribed' },
          { status: 200 }
        );
      } else {
        // Reactivate subscription
        await db
          .update(subscribers)
          .set({ 
            status: 'subscribed',
            unsubToken: uuidv4()
          })
          .where(eq(subscribers.email, email.toLowerCase()));

        return NextResponse.json(
          { message: 'Subscription reactivated successfully' },
          { status: 200 }
        );
      }
    }

    // Create new subscriber
    const unsubToken = uuidv4();
    await db.insert(subscribers).values({
      email: email.toLowerCase(),
      unsubToken,
    });

    return NextResponse.json(
      { message: 'Successfully subscribed to IPO Hype Tracker newsletter!' },
      { status: 201 }
    );
  } catch (error) {
    console.error('Subscribe error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
