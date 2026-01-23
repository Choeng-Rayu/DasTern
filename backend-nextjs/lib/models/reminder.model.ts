/**
 * Medication Reminder Model
 * Database operations and business logic for reminders
 */

import { query, getClient } from '../db';
import {
  MedicationReminder,
  MedicationReminderLog,
  TimeSlot,
  ReminderLogStatus,
  DosageSchedule,
  DEFAULT_TIME_SLOTS,
  Medication,
} from './types';

export class ReminderModel {
  /**
   * Create a single reminder
   */
  static async create(data: {
    medication_id: string;
    prescription_id: string;
    patient_id: string;
    time_slot: TimeSlot;
    scheduled_time: string;
    dose_amount: number;
    dose_unit?: string;
    start_date: Date;
    end_date?: Date;
    days_of_week?: number[];
    advance_notification_minutes?: number;
  }): Promise<MedicationReminder> {
    const daysOfWeek = data.days_of_week || [1, 2, 3, 4, 5, 6, 7];
    
    const result = await query(
      `INSERT INTO medication_reminders (
        medication_id, prescription_id, patient_id, time_slot, scheduled_time,
        dose_amount, dose_unit, start_date, end_date, days_of_week,
        advance_notification_minutes, is_active, total_doses, completed_doses, missed_doses
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, TRUE, 0, 0, 0)
      RETURNING *`,
      [
        data.medication_id,
        data.prescription_id,
        data.patient_id,
        data.time_slot,
        data.scheduled_time,
        data.dose_amount,
        data.dose_unit || null,
        data.start_date,
        data.end_date || null,
        daysOfWeek,
        data.advance_notification_minutes || 15,
      ]
    );
    return result.rows[0];
  }

  /**
   * Create reminders from medication dosage schedule
   */
  static async createFromDosageSchedule(
    medication: Medication,
    patientId: string,
    customTimes?: Record<TimeSlot, string>
  ): Promise<MedicationReminder[]> {
    const schedule = medication.dosage_schedule as DosageSchedule;
    const reminders: MedicationReminder[] = [];
    const startDate = new Date();
    
    // Calculate end date based on medication duration
    let endDate: Date | undefined;
    if (medication.duration_days) {
      endDate = new Date();
      endDate.setDate(endDate.getDate() + medication.duration_days);
    }

    const timeSlots: TimeSlot[] = ['morning', 'noon', 'afternoon', 'evening', 'night'];

    for (const slot of timeSlots) {
      const dosage = schedule[slot];
      if (dosage && dosage.dose > 0) {
        const scheduledTime = customTimes?.[slot] || 
                              dosage.preferred_time || 
                              DEFAULT_TIME_SLOTS[slot].default;

        const reminder = await this.create({
          medication_id: medication.id,
          prescription_id: medication.prescription_id,
          patient_id: patientId,
          time_slot: slot,
          scheduled_time: scheduledTime,
          dose_amount: dosage.dose,
          dose_unit: dosage.unit || medication.quantity_unit,
          start_date: startDate,
          end_date: endDate,
        });
        reminders.push(reminder);
      }
    }

    return reminders;
  }

  /**
   * Create reminders for all medications in a prescription
   */
  static async createForPrescription(
    prescriptionId: string,
    patientId: string,
    medications: Medication[],
    customTimes?: Record<TimeSlot, string>
  ): Promise<MedicationReminder[]> {
    const allReminders: MedicationReminder[] = [];

    for (const medication of medications) {
      if (medication.dosage_schedule) {
        const reminders = await this.createFromDosageSchedule(
          medication,
          patientId,
          customTimes
        );
        allReminders.push(...reminders);
      }
    }

    return allReminders;
  }

  /**
   * Find reminder by ID
   */
  static async findById(id: string): Promise<MedicationReminder | null> {
    const result = await query(
      'SELECT * FROM medication_reminders WHERE id = $1',
      [id]
    );
    return result.rows[0] || null;
  }

  /**
   * Find all reminders for a patient
   */
  static async findByPatientId(
    patientId: string,
    activeOnly: boolean = true
  ): Promise<MedicationReminder[]> {
    const whereClause = activeOnly 
      ? 'WHERE patient_id = $1 AND is_active = TRUE' 
      : 'WHERE patient_id = $1';
    
    const result = await query(
      `SELECT mr.*, m.name as medication_name, m.strength, m.form
       FROM medication_reminders mr
       JOIN medications m ON mr.medication_id = m.id
       ${whereClause}
       ORDER BY mr.scheduled_time`,
      [patientId]
    );
    return result.rows;
  }

  /**
   * Find reminders for a specific medication
   */
  static async findByMedicationId(medicationId: string): Promise<MedicationReminder[]> {
    const result = await query(
      'SELECT * FROM medication_reminders WHERE medication_id = $1 ORDER BY scheduled_time',
      [medicationId]
    );
    return result.rows;
  }

  /**
   * Get today's reminders for a patient
   */
  static async getTodayReminders(patientId: string): Promise<any[]> {
    const today = new Date();
    const dayOfWeek = today.getDay() === 0 ? 7 : today.getDay(); // Convert Sunday from 0 to 7

    const result = await query(
      `SELECT
        mr.id as reminder_id,
        mr.medication_id,
        mr.prescription_id,
        m.name as medication_name,
        m.strength as medication_strength,
        mr.time_slot,
        mr.scheduled_time,
        mr.dose_amount,
        mr.dose_unit,
        COALESCE(mrl.status, 'pending') as status,
        mrl.actual_time as taken_at,
        CASE WHEN mr.scheduled_time < CURRENT_TIME AND COALESCE(mrl.status, 'pending') = 'pending'
             THEN TRUE ELSE FALSE END as is_overdue
       FROM medication_reminders mr
       JOIN medications m ON mr.medication_id = m.id
       LEFT JOIN medication_reminder_logs mrl ON mr.id = mrl.reminder_id
         AND mrl.scheduled_date = CURRENT_DATE
       WHERE mr.patient_id = $1
         AND mr.is_active = TRUE
         AND $2 = ANY(mr.days_of_week)
         AND (mr.start_date <= CURRENT_DATE)
         AND (mr.end_date IS NULL OR mr.end_date >= CURRENT_DATE)
       ORDER BY mr.scheduled_time`,
      [patientId, dayOfWeek]
    );
    return result.rows;
  }

  /**
   * Log medication taken/missed/skipped
   */
  static async logMedication(data: {
    reminder_id: string;
    medication_id: string;
    patient_id: string;
    status: ReminderLogStatus;
    scheduled_date?: Date;
    scheduled_time?: string;
    actual_time?: Date;
    notes?: string;
    dose_taken?: number;
    skipped_reason?: string;
    logged_from_device?: string;
  }): Promise<MedicationReminderLog> {
    const scheduledDate = data.scheduled_date || new Date();

    const result = await query(
      `INSERT INTO medication_reminder_logs (
        reminder_id, medication_id, patient_id, scheduled_date, scheduled_time,
        actual_time, status, notes, dose_taken, skipped_reason, logged_from_device
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
      RETURNING *`,
      [
        data.reminder_id,
        data.medication_id,
        data.patient_id,
        scheduledDate,
        data.scheduled_time || null,
        data.actual_time || (data.status === 'taken' ? new Date() : null),
        data.status,
        data.notes || null,
        data.dose_taken || null,
        data.skipped_reason || null,
        data.logged_from_device || null,
      ]
    );

    // Update reminder statistics
    await this.updateReminderStats(data.reminder_id, data.status);

    return result.rows[0];
  }

  /**
   * Update reminder statistics after logging
   */
  private static async updateReminderStats(
    reminderId: string,
    status: ReminderLogStatus
  ): Promise<void> {
    let updateField = '';
    if (status === 'taken') {
      updateField = 'completed_doses = completed_doses + 1, last_taken_at = NOW()';
    } else if (status === 'missed') {
      updateField = 'missed_doses = missed_doses + 1, last_missed_at = NOW()';
    }

    if (updateField) {
      await query(
        `UPDATE medication_reminders SET
          total_doses = total_doses + 1,
          ${updateField},
          adherence_rate = CASE
            WHEN (total_doses + 1) > 0
            THEN (completed_doses + CASE WHEN '${status}' = 'taken' THEN 1 ELSE 0 END)::DECIMAL / (total_doses + 1) * 100
            ELSE 0
          END
        WHERE id = $1`,
        [reminderId]
      );
    }
  }

  /**
   * Get adherence statistics for a patient
   */
  static async getAdherenceStats(
    patientId: string,
    days: number = 30
  ): Promise<{
    total_doses: number;
    taken: number;
    missed: number;
    skipped: number;
    adherence_rate: number;
  }> {
    const result = await query(
      `SELECT
        COUNT(*) as total_doses,
        SUM(CASE WHEN status = 'taken' THEN 1 ELSE 0 END) as taken,
        SUM(CASE WHEN status = 'missed' THEN 1 ELSE 0 END) as missed,
        SUM(CASE WHEN status = 'skipped' THEN 1 ELSE 0 END) as skipped
       FROM medication_reminder_logs
       WHERE patient_id = $1
         AND scheduled_date >= CURRENT_DATE - INTERVAL '${days} days'`,
      [patientId]
    );

    const stats = result.rows[0];
    const total = parseInt(stats.total_doses) || 0;
    const taken = parseInt(stats.taken) || 0;

    return {
      total_doses: total,
      taken: taken,
      missed: parseInt(stats.missed) || 0,
      skipped: parseInt(stats.skipped) || 0,
      adherence_rate: total > 0 ? (taken / total) * 100 : 0,
    };
  }

  /**
   * Deactivate reminder
   */
  static async deactivate(id: string): Promise<boolean> {
    const result = await query(
      'UPDATE medication_reminders SET is_active = FALSE WHERE id = $1',
      [id]
    );
    return result.rowCount! > 0;
  }

  /**
   * Deactivate all reminders for a prescription
   */
  static async deactivateByPrescriptionId(prescriptionId: string): Promise<number> {
    const result = await query(
      'UPDATE medication_reminders SET is_active = FALSE WHERE prescription_id = $1',
      [prescriptionId]
    );
    return result.rowCount || 0;
  }
}

