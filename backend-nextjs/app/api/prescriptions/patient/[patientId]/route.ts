import { query } from '@/lib/db';
import { successResponse, errorResponse } from '@/lib/utils/response';

export async function GET(
  req: Request,
  context: { params: Promise<{ patientId: string }> }
) {
  try {

    const { patientId } = await context.params;

    console.log("Received patientId:", patientId);

    const result = await query(
      `
      SELECT 
        p.*,
        COALESCE(
          json_agg(
            json_build_object(
              'id', m.id,
              'sequence_number', m.sequence_number,
              'name', m.name,
              'strength', m.strength,
              'form', m.form,
              'quantity', m.quantity,
              'duration_days', m.duration_days,
              'dosage_schedule', m.dosage_schedule,
              'instructions', m.instructions,
              'take_with_food', m.take_with_food,
              'take_before_meal', m.take_before_meal,
              'take_after_meal', m.take_after_meal
            )
          ) FILTER (WHERE m.id IS NOT NULL),
          '[]'
        ) AS medications
      FROM prescriptions p
      LEFT JOIN medications m ON p.id = m.prescription_id
      WHERE p.patient_id = $1
      GROUP BY p.id
      ORDER BY p.created_at DESC
      `,
      [patientId]
    );

    return successResponse(result.rows, "Prescriptions fetched successfully");
  } catch (error) {
    console.error(error);
    return errorResponse("Failed to fetch prescriptions", 500);
  }
}
