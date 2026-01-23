/**
 * Prescription Model
 * Database operations and business logic for prescriptions
 */

import { query } from '../db';
import {
  Prescription,
  PrescriptionStatus,
  OCRStructuredData,
  ImageMetadata,
} from './types';

export class PrescriptionModel {
  /**
   * Create a new prescription record
   */
  static async create(data: {
    patient_id: string;
    original_image_url: string;
    thumbnail_url?: string;
    image_metadata?: ImageMetadata;
    doctor_id?: string;
  }): Promise<Prescription> {
    const result = await query(
      `INSERT INTO prescriptions (
        patient_id, doctor_id, original_image_url, thumbnail_url, 
        image_metadata, status, processing_started_at
      ) VALUES ($1, $2, $3, $4, $5, 'pending', NOW())
      RETURNING *`,
      [
        data.patient_id,
        data.doctor_id || null,
        data.original_image_url,
        data.thumbnail_url || null,
        data.image_metadata ? JSON.stringify(data.image_metadata) : null,
      ]
    );
    return result.rows[0];
  }

  /**
   * Find prescription by ID
   */
  static async findById(id: string): Promise<Prescription | null> {
    const result = await query(
      'SELECT * FROM prescriptions WHERE id = $1',
      [id]
    );
    return result.rows[0] || null;
  }

  /**
   * Find prescription by ID with medications
   */
  static async findByIdWithMedications(id: string): Promise<Prescription | null> {
    const prescription = await this.findById(id);
    if (!prescription) return null;

    const medications = await query(
      'SELECT * FROM medications WHERE prescription_id = $1 ORDER BY sequence_number',
      [id]
    );
    prescription.medications = medications.rows;
    return prescription;
  }

  /**
   * Find all prescriptions for a patient
   */
  static async findByPatientId(
    patientId: string,
    options: { limit?: number; offset?: number; status?: PrescriptionStatus } = {}
  ): Promise<{ prescriptions: Prescription[]; total: number }> {
    const { limit = 10, offset = 0, status } = options;
    
    let whereClause = 'WHERE patient_id = $1';
    const params: any[] = [patientId];
    
    if (status) {
      whereClause += ' AND status = $2';
      params.push(status);
    }

    const countResult = await query(
      `SELECT COUNT(*) FROM prescriptions ${whereClause}`,
      params
    );

    const result = await query(
      `SELECT * FROM prescriptions ${whereClause} 
       ORDER BY created_at DESC 
       LIMIT $${params.length + 1} OFFSET $${params.length + 2}`,
      [...params, limit, offset]
    );

    return {
      prescriptions: result.rows,
      total: parseInt(countResult.rows[0].count),
    };
  }

  /**
   * Update prescription status
   */
  static async updateStatus(
    id: string,
    status: PrescriptionStatus,
    errorMessage?: string
  ): Promise<Prescription | null> {
    const updates: string[] = ['status = $2'];
    const params: any[] = [id, status];
    
    if (status === 'completed' || status === 'error') {
      updates.push('processing_completed_at = NOW()');
    }
    if (errorMessage) {
      updates.push(`error_message = $${params.length + 1}`);
      params.push(errorMessage);
    }

    const result = await query(
      `UPDATE prescriptions SET ${updates.join(', ')} WHERE id = $1 RETURNING *`,
      params
    );
    return result.rows[0] || null;
  }

  /**
   * Update OCR results
   */
  static async updateOCRResults(
    id: string,
    data: {
      ocr_raw_text: string;
      ocr_corrected_text?: string;
      ocr_structured_data?: OCRStructuredData;
      ocr_confidence_score: number;
      ocr_language_detected?: string;
      ocr_processing_time: number;
    }
  ): Promise<Prescription | null> {
    const result = await query(
      `UPDATE prescriptions SET
        ocr_raw_text = $2,
        ocr_corrected_text = $3,
        ocr_structured_data = $4,
        ocr_confidence_score = $5,
        ocr_language_detected = $6,
        ocr_processing_time = $7,
        status = 'ocr_completed'
      WHERE id = $1 RETURNING *`,
      [
        id,
        data.ocr_raw_text,
        data.ocr_corrected_text || data.ocr_raw_text,
        data.ocr_structured_data ? JSON.stringify(data.ocr_structured_data) : null,
        data.ocr_confidence_score,
        data.ocr_language_detected || null,
        data.ocr_processing_time,
      ]
    );
    return result.rows[0] || null;
  }

  /**
   * Update prescription metadata extracted from document
   */
  static async updateExtractedMetadata(
    id: string,
    metadata: {
      hospital_name?: string;
      hospital_address?: string;
      prescription_number?: string;
      patient_name_on_doc?: string;
      patient_age?: number;
      patient_gender?: string;
      diagnosis?: string;
      department?: string;
      prescribing_doctor_name?: string;
      prescription_date?: Date;
    }
  ): Promise<Prescription | null> {
    // Build dynamic update query
    const updates: string[] = [];
    const params: any[] = [id];
    let paramIndex = 2;
    
    Object.entries(metadata).forEach(([key, value]) => {
      if (value !== undefined) {
        updates.push(`${key} = $${paramIndex}`);
        params.push(value);
        paramIndex++;
      }
    });

    if (updates.length === 0) return this.findById(id);

    const result = await query(
      `UPDATE prescriptions SET ${updates.join(', ')} WHERE id = $1 RETURNING *`,
      params
    );
    return result.rows[0] || null;
  }
}

