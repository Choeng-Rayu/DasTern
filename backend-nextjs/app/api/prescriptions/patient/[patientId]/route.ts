import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { successResponse, errorResponse } from '@/lib/utils/response';

export async function GET(req: NextRequest, { params }: { params: { patient_id: string } }) {
  try {
    const { patient_id } = params;
    // Fetch prescriptions for patient
    const result = await query(
      `SELECT * FROM prescriptions WHERE patient_id = $1 ORDER BY created_at DESC`,
      [patient_id]
    );
    return successResponse(result.rows, 'Prescriptions fetched');
  } catch (error) {
    return errorResponse('Failed to fetch prescriptions', 500);
  }
}