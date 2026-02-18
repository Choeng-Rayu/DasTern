import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { withPatientAuth } from '@/lib/middleware/auth';

export const PATCH = async (req: NextRequest, context: any) => {
  return withPatientAuth(async (req, auth) => {
    const { answer } = await req.json();
    if (!['approved', 'rejected'].includes(answer)) {
      return NextResponse.json({ error: 'Invalid answer' }, { status: 400 });
    }

    // Await context.params for dynamic API routes
    const { requestId } = await context.params;

    const result = await query(
      `UPDATE doctor_patient_relationships
       SET status = $1, updated_at = NOW()
       WHERE id = $2 AND patient_id = $3
       RETURNING *`,
      [answer, requestId, auth.userId]
    );

    if (result.rowCount === 0) {
      return NextResponse.json({ error: 'Request not found' }, { status: 404 });
    }

    return NextResponse.json({ success: true }, { status: 200 });
  })(req);
};