/**
 * Medication Model
 * Database operations and business logic for medications
 */

import { query, getClient } from '../db';
import {
  Medication,
  MedicationForm,
  DosageSchedule,
  ExtractedMedication,
} from './types';

export class MedicationModel {
  /**
   * Create a new medication record
   */
  static async create(data: {
    prescription_id: string;
    sequence_number: number;
    name: string;
    generic_name?: string;
    brand_name?: string;
    strength?: string;
    form?: MedicationForm;
    quantity?: number;
    quantity_unit?: string;
    duration_days?: number;
    dosage_schedule: DosageSchedule;
    instructions?: string;
    take_with_food?: boolean;
    take_before_meal?: boolean;
    take_after_meal?: boolean;
  }): Promise<Medication> {
    const result = await query(
      `INSERT INTO medications (
        prescription_id, sequence_number, name, generic_name, brand_name,
        strength, form, quantity, quantity_unit, duration_days,
        dosage_schedule, instructions, take_with_food, take_before_meal,
        take_after_meal, is_active
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, TRUE)
      RETURNING *`,
      [
        data.prescription_id,
        data.sequence_number,
        data.name,
        data.generic_name || null,
        data.brand_name || null,
        data.strength || null,
        data.form || 'tablet',
        data.quantity || null,
        data.quantity_unit || null,
        data.duration_days || null,
        JSON.stringify(data.dosage_schedule),
        data.instructions || null,
        data.take_with_food || false,
        data.take_before_meal || false,
        data.take_after_meal || false,
      ]
    );
    return result.rows[0];
  }

  /**
   * Create multiple medications from OCR extraction
   */
  static async createFromExtraction(
    prescriptionId: string,
    medications: ExtractedMedication[]
  ): Promise<Medication[]> {
    const client = await getClient();
    const createdMedications: Medication[] = [];

    try {
      await client.query('BEGIN');

      for (const med of medications) {
        const result = await client.query(
          `INSERT INTO medications (
            prescription_id, sequence_number, name, quantity, quantity_unit,
            dosage_schedule, form, is_active
          ) VALUES ($1, $2, $3, $4, $5, $6, $7, TRUE)
          RETURNING *`,
          [
            prescriptionId,
            med.sequence_number,
            med.name,
            med.quantity || null,
            med.unit || null,
            JSON.stringify(med.dosage_schedule),
            'tablet', // Default form
          ]
        );
        createdMedications.push(result.rows[0]);
      }

      await client.query('COMMIT');
      return createdMedications;
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  /**
   * Find medication by ID
   */
  static async findById(id: string): Promise<Medication | null> {
    const result = await query(
      'SELECT * FROM medications WHERE id = $1',
      [id]
    );
    return result.rows[0] || null;
  }

  /**
   * Find all medications for a prescription
   */
  static async findByPrescriptionId(prescriptionId: string): Promise<Medication[]> {
    const result = await query(
      'SELECT * FROM medications WHERE prescription_id = $1 ORDER BY sequence_number',
      [prescriptionId]
    );
    return result.rows;
  }

  /**
   * Find all active medications for a patient
   */
  static async findActiveByPatientId(patientId: string): Promise<Medication[]> {
    const result = await query(
      `SELECT m.* FROM medications m
       JOIN prescriptions p ON m.prescription_id = p.id
       WHERE p.patient_id = $1 
         AND m.is_active = TRUE
         AND p.status = 'completed'
       ORDER BY p.created_at DESC, m.sequence_number`,
      [patientId]
    );
    return result.rows;
  }

  /**
   * Update medication with AI analysis results
   */
  static async updateAIAnalysis(
    id: string,
    analysis: {
      ai_drug_interactions?: string[];
      ai_side_effects?: string[];
      ai_warnings?: string[];
      ai_contraindications?: string[];
      ai_description?: string;
    }
  ): Promise<Medication | null> {
    const result = await query(
      `UPDATE medications SET
        ai_drug_interactions = $2,
        ai_side_effects = $3,
        ai_warnings = $4,
        ai_contraindications = $5,
        ai_description = $6
      WHERE id = $1 RETURNING *`,
      [
        id,
        analysis.ai_drug_interactions || null,
        analysis.ai_side_effects || null,
        analysis.ai_warnings || null,
        analysis.ai_contraindications || null,
        analysis.ai_description || null,
      ]
    );
    return result.rows[0] || null;
  }

  /**
   * Deactivate medication
   */
  static async deactivate(id: string): Promise<boolean> {
    const result = await query(
      'UPDATE medications SET is_active = FALSE WHERE id = $1',
      [id]
    );
    return result.rowCount! > 0;
  }
}

