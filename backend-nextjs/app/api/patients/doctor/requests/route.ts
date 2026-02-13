import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { withPatientAuth } from '@/lib/middleware/auth';

export const GET = withPatientAuth(async (req, auth) => {
  try {
    const result = await query(
      `SELECT dpr.id, dpr.doctor_id, dpr.status, dpr.created_at, dpr.updated_at,
              u.first_name AS doctor_first_name, u.last_name AS doctor_last_name, u.email AS doctor_email
       FROM doctor_patient_relationships dpr
       JOIN users u ON dpr.doctor_id = u.id
       WHERE dpr.patient_id = $1 AND dpr.status = 'pending'`,
      [auth.userId]
    );
    return NextResponse.json(
      {
        success: true,
        message: 'Doctor requests fetched successfully',
        data: result.rows
      },
      { status: 200 }
    );
  } catch (error: any) {
    console.error('Error fetching doctor requests:', error.message, error.stack);
    return NextResponse.json(
      { success: false, error: error.message || 'Failed to fetch doctor requests' },
      { status: 500 }
    );
  }
});