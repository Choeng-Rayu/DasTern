import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { withDoctorAuth } from '@/lib/middleware/auth';

export const POST = withDoctorAuth(async (req, auth) => {
  try {
    const { patient_id } = await req.json();
    if (!patient_id) {
      return NextResponse.json({ error: 'Missing patient_id' }, { status: 400 });
    }

    await query(
      `INSERT INTO doctor_patient_relationships (doctor_id, patient_id, status, created_at, updated_at)
       VALUES ($1, $2, 'pending', NOW(), NOW())
       ON CONFLICT (doctor_id, patient_id) DO UPDATE SET status = 'pending', updated_at = NOW()`,
      [auth.userId, patient_id]
    );

    return NextResponse.json({ success: true }, { status: 200 });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
});