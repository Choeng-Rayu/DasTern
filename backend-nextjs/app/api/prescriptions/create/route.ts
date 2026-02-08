import { NextRequest } from 'next/server';
import { query } from '@/lib/db';
import { successResponse, errorResponse } from '@/lib/utils/response';

export async function POST(req: NextRequest) {
  try {
    const {
      doctor_id,
      patient_id,
      diagnosis,
      notes,
      medications
    } = await req.json();

    // 1. Check doctor-patient relationship is approved
    const rel = await query(
      `SELECT status FROM doctor_patient_relationships WHERE doctor_id = $1 AND patient_id = $2 AND status = 'approved'`,
      [doctor_id, patient_id]
    );
    if (!rel.rowCount) {
      return errorResponse('Doctor does not have approved access to this patient', 403);
    }

    // 2. Create prescription
    const presRes = await query(
      `INSERT INTO prescriptions (doctor_id, patient_id, diagnosis, notes, created_at)
       VALUES ($1, $2, $3, $4, NOW())
       RETURNING id`,
      [doctor_id, patient_id, diagnosis, notes]
    );
    const prescription_id = presRes.rows[0].id;

    // 3. Insert medications
    for (let i = 0; i < medications.length; i++) {
      const med = medications[i];
      await query(
        `INSERT INTO medications (
          prescription_id, sequence_number, name, strength, form, quantity, duration_days,
          dosage_schedule, frequency, instructions, take_with_food, take_before_meal, take_after_meal, special_instructions, created_at
        ) VALUES (
          $1, $2, $3, $4, $5, $6, $7,
          $8, $9, $10, $11, $12, $13, $14, NOW()
        )`,
        [
          prescription_id,
          i + 1,
          med.name,
          med.strength,
          med.form,
          med.quantity,
          med.duration_days,
          JSON.stringify(med.dosage_schedule),
          med.frequency,
          med.instructions,
          med.take_with_food,
          med.take_before_meal,
          med.take_after_meal,
          med.special_instructions
        ]
      );
    }

    return successResponse({ prescription_id }, 'Prescription created');
  } catch (error) {
    return errorResponse('Failed to create prescription', 500);
  }
}