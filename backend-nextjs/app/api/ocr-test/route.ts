// /**
//  * API Route: OCR Test - Process prescription images without database storage
//  * POST /api/ocr-test
//  *
//  * This endpoint tests OCR and returns structured prescription data:
//  * - Prescription metadata (hospital, ID, date, doctor)
//  * - Patient information (name, age, gender)
//  * - Medication table with schedule (morning/noon/evening/night doses)
//  * - Vitals (if present)
//  * - Reminder generation data
//  *
//  * Flow: OCR → AI Enhancement (optional) → Structured Output
//  * Note: AI enhancement is optional - if AI doesn't respond, OCR continues
//  */

// import { NextRequest, NextResponse } from 'next/server';

// // Interfaces for structured prescription data
// interface DosageSchedule {
//   morning: number;
//   noon: number;
//   evening: number;
//   night: number;
// }

// interface Medication {
//   name: string;
//   strength: string | null;
//   form: string;
//   schedule: DosageSchedule;
//   total_quantity: number | null;
//   duration_days: number | null;
//   notes: string | null;
// }

// interface PrescriptionData {
//   prescription_id: string | null;
//   date: string | null;
//   hospital: string | null;
//   patient: {
//     name: string | null;
//     age: number | null;
//     gender: string | null;
//     medical_id: string | null;
//   };
//   diagnosis_text: string | null;
//   medications: Medication[];
//   vitals: {
//     bp: string | null;
//     pulse: number | null;
//     temperature: number | null;
//   } | null;
//   doctor: {
//     name: string | null;
//   };
// }

// export async function POST(request: NextRequest) {
//   try {
//     const formData = await request.formData();
//     const file = formData.get('image') as File;

//     if (!file) {
//       return NextResponse.json(
//         { error: 'No image file provided' },
//         { status: 400 }
//       );
//     }

//     console.log(`📤 Testing OCR for: ${file.name} (${file.size} bytes)`);

//     // Convert file to buffer
//     const arrayBuffer = await file.arrayBuffer();
//     const buffer = Buffer.from(arrayBuffer);

//     // Send to OCR service
//     const ocrServiceUrl = process.env.OCR_SERVICE_URL || 'http://ocr-service:8002';

//     const ocrFormData = new FormData();
//     const blob = new Blob([buffer], { type: file.type });
//     ocrFormData.append('file', blob, file.name);

//     console.log(`📤 Sending to OCR service: ${ocrServiceUrl}/ocr`);

//     const ocrResponse = await fetch(`${ocrServiceUrl}/ocr`, {
//       method: 'POST',
//       body: ocrFormData,
//     });

//     if (!ocrResponse.ok) {
//       throw new Error(`OCR service error: ${ocrResponse.status}`);
//     }

//     const ocrData = await ocrResponse.json();
//     console.log('📥 OCR Response received');

//     // Extract structured data from OCR response
//     const structuredData = ocrData.structured_data || {};
//     const rawText = ocrData.raw_text || ocrData.full_text || ocrData.text || '';

//     // Use AI to parse and structure the raw OCR text (this is the main enhancement)
//     let aiEnhanced = false;
//     let aiError: string | null = null;
//     let prescription: PrescriptionData;
//     let reminders: any[] = [];

//     try {
//       const aiServiceUrl = process.env.LLM_SERVICE_URL || process.env.AI_SERVICE_URL || 'http://ai-llm-service:8001';
//       console.log(`🤖 Sending to AI service: ${aiServiceUrl}/parse-prescription`);

//       const aiResponse = await fetch(`${aiServiceUrl}/parse-prescription`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           raw_text: rawText,
//           language: ocrData.primary_language || 'en'
//         }),
//         signal: AbortSignal.timeout(90000) // 90 second timeout for AI parsing
//       });

//       if (aiResponse.ok) {
//         const aiResult = await aiResponse.json();
//         if (aiResult.success && aiResult.ai_parsed && aiResult.prescription) {
//           prescription = aiResult.prescription;
//           reminders = aiResult.reminders || [];
//           aiEnhanced = true;
//           console.log(`✨ AI parsed prescription with ${prescription.medications.length} medications`);
//         } else {
//           console.log('ℹ️ AI could not parse, falling back to local extraction');
//           prescription = buildStructuredPrescription(structuredData, rawText);
//           reminders = generateReminders(prescription.medications);
//         }
//       } else {
//         console.warn(`⚠️ AI service returned ${aiResponse.status}, falling back to local extraction`);
//         prescription = buildStructuredPrescription(structuredData, rawText);
//         reminders = generateReminders(prescription.medications);
//       }
//     } catch (aiErr: any) {
//       aiError = aiErr.message;
//       console.warn('⚠️ AI service unavailable, falling back to local extraction:', aiErr.message);
//       // Fallback to local extraction
//       prescription = buildStructuredPrescription(structuredData, rawText);
//       reminders = generateReminders(prescription.medications);
//     }

//     // Return comprehensive structured result
//     return NextResponse.json({
//       success: true,
//       file: {
//         name: file.name,
//         size: file.size,
//         type: file.type
//       },
//       // Raw OCR info
//       ocr: {
//         raw_text: rawText,
//         confidence: ocrData.overall_confidence || ocrData.confidence || 0,
//         primary_language: ocrData.primary_language || 'unknown',
//         ai_enhanced: aiEnhanced,
//         ai_error: aiError
//       },
//       // Structured prescription data (main output)
//       prescription: prescription,
//       // Generated reminders
//       reminders: reminders,
//       // Summary message
//       message: `OCR completed. Detected ${prescription.medications.length} medications ready for reminder setup.${aiEnhanced ? ' (AI Enhanced)' : ' (OCR Only)'}`
//     });

//   } catch (error: any) {
//     console.error('❌ OCR Test Error:', error);

//     return NextResponse.json(
//       {
//         error: 'OCR test failed',
//         details: error.message,
//         stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
//       },
//       { status: 500 }
//     );
//   }
// }

// /**
//  * Build structured prescription from OCR data
//  * Follows the Cambodian prescription format with medication table
//  */
// function buildStructuredPrescription(structuredData: any, rawText: string): PrescriptionData {
//   // Extract header info
//   const prescription: PrescriptionData = {
//     prescription_id: structuredData.prescription_number || extractPrescriptionId(rawText),
//     date: structuredData.date || extractDate(rawText),
//     hospital: structuredData.hospital_name || extractHospital(rawText),
//     patient: {
//       name: structuredData.patient_name || null,
//       age: structuredData.patient_age || extractAge(rawText),
//       gender: structuredData.patient_gender || null,
//       medical_id: structuredData.patient_id || null,
//     },
//     diagnosis_text: structuredData.diagnosis || extractDiagnosis(rawText),
//     medications: [],
//     vitals: extractVitals(rawText),
//     doctor: {
//       name: structuredData.doctor_name || null,
//     }
//   };

//   // Process medications from structured data or raw text
//   const rawMedications = structuredData.medications || [];

//   if (rawMedications.length > 0) {
//     prescription.medications = rawMedications.map((med: any) => ({
//       name: med.name || med.original_name || 'Unknown',
//       strength: med.strength || null,
//       form: med.form || 'tablet',
//       schedule: parseSchedule(med.dosage_schedule),
//       total_quantity: med.quantity || null,
//       duration_days: calculateDurationDays(med.quantity, med.dosage_schedule),
//       notes: med.instructions || null,
//     }));
//   } else {
//     // Fallback: extract from raw text
//     prescription.medications = extractMedicationsFromText(rawText);
//   }

//   return prescription;
// }

// /**
//  * Parse dosage schedule from various formats
//  */
// function parseSchedule(schedule: any): DosageSchedule {
//   if (!schedule) {
//     return { morning: 0, noon: 0, evening: 0, night: 0 };
//   }

//   return {
//     morning: Number(schedule.morning) || 0,
//     noon: Number(schedule.noon) || 0,
//     evening: Number(schedule.evening) || Number(schedule.afternoon) || 0,
//     night: Number(schedule.night) || 0,
//   };
// }

// /**
//  * Calculate duration in days from quantity and schedule
//  */
// function calculateDurationDays(quantity: number | null, schedule: any): number | null {
//   if (!quantity || !schedule) return null;

//   const dailyDose =
//     (Number(schedule.morning) || 0) +
//     (Number(schedule.noon) || 0) +
//     (Number(schedule.evening) || Number(schedule.afternoon) || 0) +
//     (Number(schedule.night) || 0);

//   if (dailyDose === 0) return null;
//   return Math.ceil(quantity / dailyDose);
// }

// /**
//  * Extract prescription ID from raw text
//  */
// function extractPrescriptionId(text: string): string | null {
//   // Patterns: HAKF1354164, P25000720, etc.
//   const patterns = [
//     /\b([A-Z]+\d{6,})\b/,
//     /\b(P\d{8})\b/,
//     /prescription[:\s#]*([A-Z0-9]+)/i,
//   ];

//   for (const pattern of patterns) {
//     const match = text.match(pattern);
//     if (match) return match[1];
//   }
//   return null;
// }

// /**
//  * Extract date from raw text
//  */
// function extractDate(text: string): string | null {
//   // Patterns: 15/06/2025, 05/01/2026, 2025-06-15
//   const patterns = [
//     /(\d{2}\/\d{2}\/\d{4})/,
//     /(\d{4}-\d{2}-\d{2})/,
//     /(\d{2}-\d{2}-\d{4})/,
//   ];

//   for (const pattern of patterns) {
//     const match = text.match(pattern);
//     if (match) {
//       // Normalize to ISO format if DD/MM/YYYY
//       const dateStr = match[1];
//       if (dateStr.includes('/')) {
//         const parts = dateStr.split('/');
//         if (parts.length === 3) {
//           return `${parts[2]}-${parts[1]}-${parts[0]}`;
//         }
//       }
//       return dateStr;
//     }
//   }
//   return null;
// }

// /**
//  * Extract hospital name from raw text
//  */
// function extractHospital(text: string): string | null {
//   const patterns = [
//     /(khmer[- ]soviet[- ]friendship[- ]hospital)/i,
//     /([A-Za-z\s]+ hospital)/i,
//     /([A-Za-z\s]+ polyclinic)/i,
//     /([A-Za-z\s]+ clinic)/i,
//   ];

//   for (const pattern of patterns) {
//     const match = text.match(pattern);
//     if (match) return match[1].trim();
//   }
//   return null;
// }

// /**
//  * Extract age from raw text
//  */
// function extractAge(text: string): number | null {
//   const match = text.match(/age[:\s]*(\d{1,3})|(\d{1,3})\s*(?:years?|yrs?|ឆ្នាំ)/i);
//   if (match) {
//     return parseInt(match[1] || match[2], 10);
//   }
//   return null;
// }

// /**
//  * Extract diagnosis from raw text (stored as text only, never interpreted)
//  */
// function extractDiagnosis(text: string): string | null {
//   const patterns = [
//     /diagnosis[:\s]*([^\n]+)/i,
//     /dx[:\s]*([^\n]+)/i,
//     /\bt\s*:\s*([^\n]+)/i, // "t : Chronic Cystitis"
//   ];

//   for (const pattern of patterns) {
//     const match = text.match(pattern);
//     if (match) return match[1].trim();
//   }
//   return null;
// }

// /**
//  * Extract vitals from raw text (if present)
//  */
// function extractVitals(text: string): { bp: string | null; pulse: number | null; temperature: number | null } | null {
//   const bpMatch = text.match(/(?:TA|BP)[:\s]*(\d{2,3}\/\d{2,3})/i);
//   const pulseMatch = text.match(/(?:pulse|P)[:\s]*(\d{2,3})(?:\/min)?/i);
//   const tempMatch = text.match(/(?:temp|temperature|T)[:\s]*(\d{2}(?:\.\d)?)/i);

//   if (bpMatch || pulseMatch || tempMatch) {
//     return {
//       bp: bpMatch ? bpMatch[1] : null,
//       pulse: pulseMatch ? parseInt(pulseMatch[1], 10) : null,
//       temperature: tempMatch ? parseFloat(tempMatch[1]) : null,
//     };
//   }
//   return null;
// }

// /**
//  * Extract medications from raw text when structured data is not available
//  */
// function extractMedicationsFromText(text: string): Medication[] {
//   const medications: Medication[] = [];
//   const lines = text.split('\n').filter(line => line.trim());

//   // Pattern: "Medicine Name 500mg" with possible schedule numbers
//   const medPattern = /^(\d+)?\s*([A-Za-z][A-Za-z\s]*?)\s+(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|amp|tablet|cap)/i;

//   for (let i = 0; i < lines.length; i++) {
//     const line = lines[i];
//     const match = line.match(medPattern);

//     if (match) {
//       // Look for schedule numbers in the same or next line
//       // Format: "1 - 1 -" or "1 0 1 0" (morning noon evening night)
//       const schedulePattern = /(\d|[-–])\s+(\d|[-–])\s+(\d|[-–])\s*(\d|[-–])?/;
//       const contextText = lines.slice(i, Math.min(i + 2, lines.length)).join(' ');
//       const scheduleMatch = contextText.match(schedulePattern);

//       const schedule: DosageSchedule = { morning: 0, noon: 0, evening: 0, night: 0 };

//       if (scheduleMatch) {
//         schedule.morning = scheduleMatch[1] !== '-' && scheduleMatch[1] !== '–' ? parseInt(scheduleMatch[1], 10) : 0;
//         schedule.noon = scheduleMatch[2] !== '-' && scheduleMatch[2] !== '–' ? parseInt(scheduleMatch[2], 10) : 0;
//         schedule.evening = scheduleMatch[3] !== '-' && scheduleMatch[3] !== '–' ? parseInt(scheduleMatch[3], 10) : 0;
//         schedule.night = scheduleMatch[4] && scheduleMatch[4] !== '-' && scheduleMatch[4] !== '–' ? parseInt(scheduleMatch[4], 10) : 0;
//       }

//       // Extract quantity (e.g., "14 tablets", "21 days")
//       const qtyMatch = contextText.match(/(\d+)\s*(?:tablets?|days?|jours?|គ្រាប់)/i);
//       const quantity = qtyMatch ? parseInt(qtyMatch[1], 10) : null;

//       medications.push({
//         name: match[2].trim(),
//         strength: `${match[3]}${match[4]}`,
//         form: 'tablet',
//         schedule,
//         total_quantity: quantity,
//         duration_days: calculateDurationDays(quantity, schedule),
//         notes: null,
//       });
//     }
//   }

//   return medications;
// }

// /**
//  * Generate reminders from medication schedule
//  * Time slots based on Cambodian prescription format:
//  * - Morning (ព្រឹក): 06:00-08:00
//  * - Noon (ថ្ងៃ): 11:00-12:00
//  * - Evening (ល្ងាច): 17:00-18:00
//  * - Night (យប់): 20:00-22:00
//  */
// interface Reminder {
//   medication_name: string;
//   strength: string | null;
//   time: string;
//   time_slot: string;
//   dose: number;
//   message_en: string;
//   message_kh: string;
// }

// function generateReminders(medications: Medication[]): Reminder[] {
//   const reminders: Reminder[] = [];

//   const timeSlots = {
//     morning: { time: '07:00', slot: 'morning', kh: 'ព្រឹក' },
//     noon: { time: '11:30', slot: 'noon', kh: 'ថ្ងៃ' },
//     evening: { time: '17:30', slot: 'evening', kh: 'ល្ងាច' },
//     night: { time: '21:00', slot: 'night', kh: 'យប់' },
//   };

//   for (const med of medications) {
//     const { schedule } = med;

//     // Generate reminder for each non-zero dose
//     for (const [slot, config] of Object.entries(timeSlots)) {
//       const dose = schedule[slot as keyof DosageSchedule];
//       if (dose && dose > 0) {
//         const strengthText = med.strength ? ` ${med.strength}` : '';
//         reminders.push({
//           medication_name: med.name,
//           strength: med.strength,
//           time: config.time,
//           time_slot: config.slot,
//           dose,
//           message_en: `Take ${dose} ${med.form}${dose > 1 ? 's' : ''} of ${med.name}${strengthText}`,
//           message_kh: `សូមទទួលថ្នាំ ${med.name}${strengthText} ចំនួន ${dose} គ្រាប់ ពេល${config.kh}`,
//         });
//       }
//     }
//   }

//   // Sort by time
//   reminders.sort((a, b) => a.time.localeCompare(b.time));

//   return reminders;
// }
