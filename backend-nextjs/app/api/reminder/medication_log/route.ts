import { query } from "@/lib/db";
import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const {
      reminder_id,
      medication_id,
      patient_id,
      status,
      dose_taken
    } = await req.json();

    const now = new Date();

    // 1️⃣ Insert log
    await query(
      `INSERT INTO medication_reminder_logs (
        reminder_id,
        medication_id,
        patient_id,
        scheduled_date,
        scheduled_time,
        actual_time,
        status,
        dose_taken
      )
      VALUES ($1,$2,$3,$4,$5,$6,$7,$8)`,
      [
        reminder_id,
        medication_id,
        patient_id,
        now.toISOString().split("T")[0],
        now.toTimeString().split(" ")[0],
        now,
        status,
        dose_taken
      ]
    );

    // 2️⃣ Update reminder stats
    if (status === "taken") {
      await query(`
        UPDATE medication_reminders
        SET completed_doses = completed_doses + 1,
            total_doses = total_doses + 1,
            last_taken_at = NOW(),
            adherence_rate = 
              (completed_doses + 1) * 100.0 / (total_doses + 1)
        WHERE id = '${reminder_id}'
      `);
    }

    if (status === "missed") {
      await query(`
        UPDATE medication_reminders
        SET missed_doses = missed_doses + 1,
            total_doses = total_doses + 1,
            last_missed_at = NOW()
        WHERE id = '${reminder_id}'
      `);
    }

    return Response.json({ success: true });

  } catch (err) {
    return Response.json({ success: false }, { status: 500 });
  }
}
