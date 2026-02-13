import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { successResponse, errorResponse } from '@/lib/utils/response';

export async function POST(req: NextRequest) {
  try {
    const { phone_number } = await req.json();

    // TODO: Get doctor_id from authentication/session
    const doctor_id = req.headers.get('x-doctor-id'); // Example: replace with your auth logic

    // 1. Find patient by phone number
    const patientRes = await query(
      `SELECT id FROM users WHERE phone_number = $1 AND role = 'patient'`,
      [phone_number]
    );
    if (patientRes.rowCount === 0) {
      return errorResponse('Patient not found', 404);
    }
    const patient_id = patientRes.rows[0].id;

    // 2. Insert relationship request
    await query(
      `INSERT INTO doctor_patient_relationships (doctor_id, patient_id, status, created_at)
       VALUES ($1, $2, 'pending', NOW()) ON CONFLICT (doctor_id, patient_id) DO NOTHING`,
      [doctor_id, patient_id]
    );

    return successResponse({}, 'Access request sent');
  } catch (error) {
    return errorResponse('Failed to request access', 500);
  }
}