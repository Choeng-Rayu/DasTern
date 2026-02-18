import { query } from "@/lib/db";
import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { prescription_id, patient_id } = await req.json();


    const medsRes = await query(
      `SELECT * FROM medications WHERE prescription_id = $1`,
      [prescription_id]
    );

 
    const profileRes = await query(
      `SELECT * FROM patient_profiles WHERE user_id = $1`,
      [patient_id]
    );

    const profile = profileRes.rows[0];
    const mealSchedule = profile?.meal_schedule || {};

    for (const med of medsRes.rows) {

      // Determine scheduled_time
      let scheduledTime = "08:00";

      if (med.take_before_meal && mealSchedule.breakfast)
        scheduledTime = mealSchedule.breakfast;

      if (med.take_after_meal && mealSchedule.lunch)
        scheduledTime = mealSchedule.lunch;

      const startDate = new Date();
      const endDate = new Date();
      endDate.setDate(startDate.getDate() + med.duration_days);

      await query(
        `INSERT INTO medication_reminders (
          medication_id,
          prescription_id,
          patient_id,
          time_slot,
          scheduled_time,
          dose_amount,
          dose_unit,
          start_date,
          end_date,
          next_reminder_at
        )
        VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)`,
        [
          med.id,
          prescription_id,
          patient_id,
          "morning",
          scheduledTime,
          med.dosage_schedule?.amount || 1,
          med.dosage_schedule?.unit || "tablet",
          startDate,
          endDate,
          new Date(`${startDate.toISOString().split("T")[0]} ${scheduledTime}`)
        ]
      );
    }

    return Response.json({ success: true });

  } catch (err) {
    return Response.json({ success: false }, { status: 500 });
  }
}
