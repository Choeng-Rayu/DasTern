import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { successResponse, errorResponse } from '@/lib/utils/response';

export async function POST(req: NextRequest) {
  try {
    const { doctor_id, patient_id } = await req.json();
    // Patient approves access
    await query(
      `UPDATE doctor_patient_access SET status = 'approved', approved_at = NOW()
       WHERE doctor_id = $1 AND patient_id = $2 AND status = 'pending'`,
      [doctor_id, patient_id]
    );
    return successResponse({}, 'Access approved');
  } catch (error) {
    return errorResponse('Failed to approve access', 500);
  }
}