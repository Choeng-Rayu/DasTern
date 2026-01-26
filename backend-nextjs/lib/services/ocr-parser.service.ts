/**
 * OCR Parser Service
 * Parses OCR results specifically for Cambodian hospital prescription format
 * Based on Khmer-Soviet Friendship Hospital prescription layout
 */

import {
  OCRStructuredData,
  PrescriptionHeader,
  ExtractedMedication,
  DosageSchedule,
  KHMER_TIME_SLOT_MAP,
} from '../models/types';

export interface CambodianPrescriptionData {
  // Header fields (Khmer/English)
  hospital_name?: string;
  prescription_number?: string;  // លេខកូដ (e.g., HAKF1354164)
  patient_name?: string;         // ឈ្មោះអ្នកជំងឺ
  patient_age?: number;          // អាយុ
  patient_gender?: string;       // ភេទ (ស្រី = Female, ប្រុស = Male)
  medical_id?: string;           // មូលនិធិសមធម៌
  diagnosis?: string;            // រោគវិនិច្ឆ័យ
  department?: string;           // ផ្នែក
  date?: string;                 // ថ្ងៃទី
  doctor_name?: string;          // គ្រូពេទ្យព្យាបាល
  
  // Medication table
  medications: CambodianMedication[];
}

export interface CambodianMedication {
  row_number: number;           // ល.រ (sequence number)
  name: string;                 // ឈ្មោះឱសថ (medication name)
  quantity: number;             // ចំនួន (quantity)
  unit: string;                 // វិធីប្រើ (unit - គ្រាប់, គ្រាប់ស្រាប, etc.)
  morning?: number;             // ព្រឹក (6-8)
  noon?: number;                // ថ្ងៃត្រង់ (11-12)
  afternoon?: number;           // ល្ងាច (05-06)
  night?: number;               // យប់ (08-10)
}

export class OCRParserService {
  /**
   * Parse raw OCR text into structured Cambodian prescription data
   */
  static parseCambodianPrescription(rawText: string): CambodianPrescriptionData {
    // This is a placeholder for actual OCR parsing logic
    // In production, this would use regex patterns to extract data
    const lines = rawText.split('\n').map(l => l.trim()).filter(l => l);
    
    const data: CambodianPrescriptionData = {
      medications: [],
    };

    // Extract header information
    for (const line of lines) {
      // Prescription number pattern (e.g., HAKF1354164)
      const prescNumMatch = line.match(/លេខកូដ[:：]?\s*([A-Z]{4}\d+)/);
      if (prescNumMatch) data.prescription_number = prescNumMatch[1];

      // Diagnosis pattern
      const diagMatch = line.match(/រោគវិនិច្ឆ័យ[:：]?\s*(.+)/);
      if (diagMatch) data.diagnosis = diagMatch[1];

      // Age pattern
      const ageMatch = line.match(/អាយុ[:：]?\s*(\d+)/);
      if (ageMatch) data.patient_age = parseInt(ageMatch[1]);
    }

    return data;
  }

  /**
   * Convert Cambodian prescription medication to structured format
   */
  static medicationToExtracted(med: CambodianMedication): ExtractedMedication {
    const dosageSchedule: DosageSchedule = {
      times_per_day: 0,
    };

    // Map the columns to time slots
    if (med.morning && med.morning > 0) {
      dosageSchedule.morning = { 
        dose: med.morning,
        time_range_start: '06:00',
        time_range_end: '08:00',
        preferred_time: '07:00'
      };
      dosageSchedule.times_per_day!++;
    }

    if (med.noon && med.noon > 0) {
      dosageSchedule.noon = { 
        dose: med.noon,
        time_range_start: '11:00',
        time_range_end: '12:00',
        preferred_time: '11:30'
      };
      dosageSchedule.times_per_day!++;
    }

    if (med.afternoon && med.afternoon > 0) {
      dosageSchedule.afternoon = { 
        dose: med.afternoon,
        time_range_start: '17:00',
        time_range_end: '18:00',
        preferred_time: '17:30'
      };
      dosageSchedule.times_per_day!++;
    }

    if (med.night && med.night > 0) {
      dosageSchedule.night = { 
        dose: med.night,
        time_range_start: '20:00',
        time_range_end: '22:00',
        preferred_time: '21:00'
      };
      dosageSchedule.times_per_day!++;
    }

    return {
      sequence_number: med.row_number,
      name: med.name,
      quantity: med.quantity,
      unit: med.unit,
      dosage_schedule: dosageSchedule,
    };
  }

  /**
   * Build complete structured data from Cambodian prescription
   */
  static buildStructuredData(data: CambodianPrescriptionData): OCRStructuredData {
    const header: PrescriptionHeader = {
      hospital_name: data.hospital_name,
      patient_id: data.prescription_number,
      patient_name: data.patient_name,
      age: data.patient_age,
      gender: data.patient_gender,
      diagnosis: data.diagnosis,
      department: data.department,
      date: data.date,
    };

    const medications = data.medications.map(med => 
      this.medicationToExtracted(med)
    );

    return {
      header,
      medications,
      footer: {
        doctor_name: data.doctor_name,
        date: data.date,
      },
    };
  }

  /**
   * Example: Parse the sample prescription from the image
   */
  static getSamplePrescription(): OCRStructuredData {
    // This represents the data from the provided prescription image
    const sampleData: CambodianPrescriptionData = {
      hospital_name: 'មន្ទីរពេទ្យមិត្តភាពខ្មែរ-សូវៀត (Khmer-Soviet Friendship Hospital)',
      prescription_number: 'HAKF1354164',
      patient_name: 'ហុ ចាន',
      patient_age: 19,
      patient_gender: 'ស្រី', // Female
      medical_id: '20051002-0409',
      diagnosis: 'Chronic Cystitis',
      department: 'បន្ទប់លេខ 5',
      date: '15/06/2025',
      doctor_name: 'Srvheng',
      medications: [
        { row_number: 1, name: 'Butylscopolamine 10mg', quantity: 14, unit: 'គ្រាប់', morning: 1, noon: undefined, afternoon: 1, night: 1 },
        { row_number: 2, name: 'Celcoxx 100mg', quantity: 14, unit: 'គ្រាប់ស្រាប', morning: 1, noon: undefined, afternoon: 1, night: 1 },
        { row_number: 3, name: 'Omeprazole 20mg', quantity: 14, unit: 'គ្រាប់', morning: 1, noon: 1, afternoon: 1, night: 1 },
        { row_number: 4, name: 'Multivitamine', quantity: 21, unit: 'គ្រាប់', morning: 1, noon: 1, afternoon: 1, night: undefined },
      ],
    };

    return this.buildStructuredData(sampleData);
  }
}

