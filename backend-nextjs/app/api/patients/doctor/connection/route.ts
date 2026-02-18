import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { withPatientAuth } from '@/lib/middleware/auth';

export const GET = withPatientAuth(async (req, auth) => {
    // Get all doctor connections for this patient
    const result = await query(
        `SELECT dpr.id, dpr.status, dpr.created_at, dpr.updated_at,
            u.id as doctor_id, u.first_name, u.last_name, u.email
     FROM doctor_patient_relationships dpr
     JOIN users u ON dpr.doctor_id = u.id
     WHERE dpr.patient_id = $1`,
        [auth.userId]
    );

    return NextResponse.json(result.rows, { status: 200 });
});