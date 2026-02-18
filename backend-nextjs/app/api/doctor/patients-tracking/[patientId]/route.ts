import { successResponse, errorResponse } from "@/lib/utils/response";
import { query } from '@/lib/db'
import { NextRequest } from "next/server";
import { withDoctorAuth } from "@/lib/middleware/auth";

export async function GET(
    req: Request,
    context: { params: Promise<{ patientId: string }> }

) {
    try {
        const { patientId } = await context.params;

        const result = await query(
            ` SELECT
            mr.id,
            m.name AS medication_name,
            mr.adherence_rate,
            mr.completed_doses,
            mr.missed_doses,
            mr.next_reminder_at,
            mrl.status,
            mrl.actual_time
            FROM medication_reminders mr
            JOIN medications m ON mr.medication_id = m.id
            LEFT JOIN medication_reminder_logs mrl 
            ON mr.id = mrl.reminder_id
            WHERE mr.patient_id = $1
            ORDER BY mrl.created_at DESC;
            `, [patientId]
        );
        return successResponse(result.rows, "sucess");
    } catch (error)
    {
        console.error(error);
        return errorResponse("Failed to view patient prescription");
    }
}

