/**
 * Prescription Processing Service
 * Handles the full flow from OCR to reminder creation
 */

import { PrescriptionModel } from '../models/prescription.model';
import { MedicationModel } from '../models/medication.model';
import { ReminderModel } from '../models/reminder.model';
import {
  Prescription,
  Medication,
  MedicationReminder,
  OCRStructuredData,
  ExtractedMedication,
  DosageSchedule,
  TimeSlot,
  BulkRemindersResponse,
} from '../models/types';

export interface ProcessPrescriptionResult {
  prescription: Prescription;
  medications: Medication[];
  reminders: MedicationReminder[];
  warnings: string[];
}

export class PrescriptionService {
  /**
   * Process a prescription from OCR results and create reminders
   */
  static async processFromOCR(
    prescriptionId: string,
    patientId: string,
    ocrData: {
      raw_text: string;
      corrected_text?: string;
      structured_data: OCRStructuredData;
      confidence_score: number;
      language_detected?: string;
      processing_time: number;
    },
    createReminders: boolean = true
  ): Promise<ProcessPrescriptionResult> {
    const warnings: string[] = [];

    // 1. Update prescription with OCR results
    const prescription = await PrescriptionModel.updateOCRResults(prescriptionId, {
      ocr_raw_text: ocrData.raw_text,
      ocr_corrected_text: ocrData.corrected_text,
      ocr_structured_data: ocrData.structured_data,
      ocr_confidence_score: ocrData.confidence_score,
      ocr_language_detected: ocrData.language_detected,
      ocr_processing_time: ocrData.processing_time,
    });

    if (!prescription) {
      throw new Error(`Prescription ${prescriptionId} not found`);
    }

    // 2. Update prescription metadata from structured data
    if (ocrData.structured_data.header) {
      const header = ocrData.structured_data.header;
      await PrescriptionModel.updateExtractedMetadata(prescriptionId, {
        hospital_name: header.hospital_name,
        patient_name_on_doc: header.patient_name,
        patient_age: header.age,
        patient_gender: header.gender,
        diagnosis: header.diagnosis,
        department: header.department,
        prescription_date: header.date ? new Date(header.date) : undefined,
      });
    }

    // 3. Create medication records
    const medications = await MedicationModel.createFromExtraction(
      prescriptionId,
      ocrData.structured_data.medications
    );

    if (medications.length === 0) {
      warnings.push('No medications were extracted from the prescription');
    }

    // 4. Create reminders if requested
    let reminders: MedicationReminder[] = [];
    if (createReminders && medications.length > 0) {
      reminders = await ReminderModel.createForPrescription(
        prescriptionId,
        patientId,
        medications
      );
    }

    // 5. Mark prescription as completed
    await PrescriptionModel.updateStatus(prescriptionId, 'completed');

    return {
      prescription: (await PrescriptionModel.findByIdWithMedications(prescriptionId))!,
      medications,
      reminders,
      warnings,
    };
  }

  /**
   * Parse Cambodian prescription format into structured medications
   * Based on the prescription image format from Khmer-Soviet Friendship Hospital
   */
  static parseCambodianPrescription(
    rawMedications: Array<{
      number: number;
      name: string;
      quantity: number;
      unit: string;
      morning?: number;
      noon?: number;
      afternoon?: number;
      night?: number;
    }>
  ): ExtractedMedication[] {
    return rawMedications.map((med) => {
      const dosageSchedule: DosageSchedule = {
        times_per_day: 0,
      };

      // Map Cambodian prescription columns to time slots
      if (med.morning && med.morning > 0) {
        dosageSchedule.morning = { dose: med.morning };
        dosageSchedule.times_per_day!++;
      }
      if (med.noon && med.noon > 0) {
        dosageSchedule.noon = { dose: med.noon };
        dosageSchedule.times_per_day!++;
      }
      if (med.afternoon && med.afternoon > 0) {
        dosageSchedule.afternoon = { dose: med.afternoon };
        dosageSchedule.times_per_day!++;
      }
      if (med.night && med.night > 0) {
        dosageSchedule.night = { dose: med.night };
        dosageSchedule.times_per_day!++;
      }

      return {
        sequence_number: med.number,
        name: med.name,
        quantity: med.quantity,
        unit: med.unit,
        dosage_schedule: dosageSchedule,
      };
    });
  }

  /**
   * Get prescription with full details including medications and reminders
   */
  static async getFullDetails(prescriptionId: string): Promise<{
    prescription: Prescription;
    medications: Medication[];
    reminders: MedicationReminder[];
  } | null> {
    const prescription = await PrescriptionModel.findByIdWithMedications(prescriptionId);
    if (!prescription) return null;

    const reminders: MedicationReminder[] = [];
    for (const medication of prescription.medications || []) {
      const medReminders = await ReminderModel.findByMedicationId(medication.id);
      reminders.push(...medReminders);
    }

    return {
      prescription,
      medications: prescription.medications || [],
      reminders,
    };
  }
}

