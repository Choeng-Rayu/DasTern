/**
 * API Route: Upload and Process Prescription Image with OCR
 * POST /api/prescriptions/upload
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import axios from 'axios';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('image') as File;
    const patientId = formData.get('patient_id') as string;

    if (!file) {
      return NextResponse.json(
        { error: 'No image file provided' },
        { status: 400 }
      );
    }

    // Convert file to buffer for forwarding to OCR service
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // Step 1: Create prescription record in database
    const prescriptionResult = await query(
      `INSERT INTO prescriptions (patient_id, original_image_url, status, created_at, updated_at)
       VALUES ($1, $2, $3, NOW(), NOW())
       RETURNING id`,
      [patientId || '00000000-0000-0000-0000-000000000000', `uploads/${file.name}`, 'processing']
    );

    const prescriptionId = prescriptionResult.rows[0].id;

    // Step 2: Send image to OCR service
    const ocrServiceUrl = process.env.OCR_SERVICE_URL || 'http://ocr-service:8000';
    
    const ocrFormData = new FormData();
    const blob = new Blob([buffer], { type: file.type });
    ocrFormData.append('file', blob, file.name);

    console.log(`📤 Sending image to OCR service: ${ocrServiceUrl}/process`);

    const ocrResponse = await axios.post(
      `${ocrServiceUrl}/process`,
      ocrFormData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout
      }
    );

    const ocrData = ocrResponse.data;
    console.log('📥 OCR Response:', ocrData);

    // Step 3: Update prescription with OCR results
    const rawText = ocrData.full_text || ocrData.text || ocrData.raw_text || '';
    await query(
      `UPDATE prescriptions 
       SET ocr_raw_text = $1, 
           ocr_confidence_score = $2,
           ocr_language_detected = $3,
           status = $4,
           processing_completed_at = NOW(),
           updated_at = NOW()
       WHERE id = $5`,
      [
        rawText,
        ocrData.overall_confidence || ocrData.confidence || 0,
        ocrData.language || 'en',
        'completed',
        prescriptionId
      ]
    );

    // Step 4: Check if AI service is available for enhancement
    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://ai-llm-service:8001';
    let aiEnhanced = false;
    let correctedText = rawText;

    try {
      // Only call AI service if there's text to correct
      if (rawText && rawText.trim()) {
        console.log(`🤖 Sending to AI service for correction: ${aiServiceUrl}/correct-ocr`);
        
        const aiResponse = await axios.post(
          `${aiServiceUrl}/correct-ocr`,
          {
            text: rawText,
            language: ocrData.language || 'en'
          },
          { timeout: 30000 }
        );

        if (aiResponse.data.corrected_text) {
          correctedText = aiResponse.data.corrected_text;
          aiEnhanced = true;

          // Update with AI-corrected text
          await query(
            `UPDATE prescriptions 
             SET ocr_corrected_text = $1,
                 ai_confidence_score = $2,
                 updated_at = NOW()
             WHERE id = $3`,
            [correctedText, aiResponse.data.confidence || 0, prescriptionId]
          );
        }
      } else {
        console.log('⚠️ No text extracted from OCR, skipping AI correction');
      }
    } catch (aiError) {
      console.warn('⚠️ AI enhancement not available, using raw OCR text:', aiError);
    }

    // Step 5: Extract medications from text (simple parsing for MVP)
    const medications = extractMedications(correctedText);

    // Step 6: Save medications to database and create reminders
    const medicationIds = [];
    for (const med of medications) {
      const medResult = await query(
        `INSERT INTO medications 
         (prescription_id, name, strength, dosage, frequency, duration, instructions, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
         RETURNING id`,
        [
          prescriptionId,
          med.name,
          med.strength,
          med.dosage,
          med.frequency,
          med.duration,
          med.instructions || 'Take as prescribed'
        ]
      );
      
      const medicationId = medResult.rows[0].id;
      medicationIds.push({ id: medicationId, ...med });
    }

    // Step 7: Auto-generate reminders for each medication
    const reminders = [];
    for (const med of medicationIds) {
      const reminderTimes = generateReminderTimes(med.timing || {});
      const durationDays = extractDurationDays(med.duration);
      
      const reminderResult = await query(
        `INSERT INTO medication_reminders 
         (medication_id, patient_id, reminder_times, start_date, end_date, days_of_week, is_active, created_at, updated_at)
         VALUES ($1, $2, $3, CURRENT_DATE, CURRENT_DATE + INTERVAL '${durationDays} days', $4, $5, NOW(), NOW())
         RETURNING id`,
        [
          med.id,
          patientId || '00000000-0000-0000-0000-000000000000',
          JSON.stringify(reminderTimes),
          JSON.stringify([1, 2, 3, 4, 5, 6, 7]), // All days
          true
        ]
      );
      
      reminders.push({
        reminder_id: reminderResult.rows[0].id,
        medication_name: med.name,
        reminder_times: reminderTimes,
        duration_days: durationDays
      });
    }

    // Return complete response
    return NextResponse.json({
      success: true,
      prescription_id: prescriptionId,
      ocr_text: correctedText,
      ocr_confidence: ocrData.confidence || 0,
      ai_enhanced: aiEnhanced,
      medications: medications,
      reminders: reminders,
      message: `Prescription processed successfully. Created ${medications.length} medications and ${reminders.length} reminders.`
    });

  } catch (error: any) {
    console.error('❌ Error processing prescription:', error);
    
    return NextResponse.json(
      {
        error: 'Failed to process prescription',
        details: error.message,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}

/**
 * Enhanced medication extraction for Khmer prescriptions
 * Handles the specific table format with timing columns
 */
function extractMedications(text: string) {
  const medications = [];
  const lines = text.split('\n');
  
  // Known medication names from Khmer prescriptions
  const knownMedications = [
    'Calcium', 'Multivitamine', 'Amitriptyline', 'Butylscopolamine',
    'Celcoxx', 'Omeprazole', 'Paracetamol', 'Esome'
  ];

  for (const line of lines) {
    const trimmedLine = line.trim();
    if (!trimmedLine || trimmedLine.length < 10) continue;

    // Look for numbered medication lines (e.g., "1. Calcium amp Tablet...")
    if (/^\d+\./.test(trimmedLine)) {
      const medInfo = parseMedicationLine(trimmedLine, knownMedications);
      if (medInfo) {
        medications.push(medInfo);
      }
    }
  }

  // If no medications found, try fallback parsing
  if (medications.length === 0) {
    for (const medName of knownMedications) {
      if (text.toLowerCase().includes(medName.toLowerCase())) {
        medications.push({
          name: medName,
          strength: null,
          dosage: '1 tablet',
          frequency: 'once daily',
          duration: '7 days',
          timing: { morning: true, noon: false, evening: false, night: false },
          instructions: 'Take as prescribed'
        });
      }
    }
  }

  // Final fallback
  if (medications.length === 0) {
    medications.push({
      name: 'Unknown Medication',
      strength: null,
      dosage: '1 tablet',
      frequency: 'once daily',
      duration: '7 days',
      timing: { morning: true, noon: false, evening: false, night: false },
      instructions: 'Take as prescribed'
    });
  }

  return medications;
}

/**
 * Parse a single medication line from Khmer prescription table
 */
function parseMedicationLine(line: string, knownMedications: string[]) {
  const parts = line.split(/\s+/);
  if (parts.length < 4) return null;

  // Extract medication name
  let medName = null;
  for (const part of parts.slice(1)) { // Skip the number
    if (knownMedications.some(known => known.toLowerCase() === part.toLowerCase())) {
      medName = part;
      break;
    }
  }

  if (!medName) {
    // Try to find any medication-like word
    for (const part of parts.slice(1, 4)) {
      if (/^[A-Za-z]+/.test(part) && part.length > 3) {
        medName = part;
        break;
      }
    }
  }

  if (!medName) return null;

  // Extract strength (e.g., "10mg")
  const strengthMatch = line.match(/(\d+)\s*(mg|ml)/i);
  const strength = strengthMatch ? strengthMatch[0] : null;

  // Extract dosage
  const quantityMatch = line.match(/(\d+)\s*(tablet|ថ្នាំ)/i);
  const dosage = quantityMatch ? `${quantityMatch[1]} tablet` : '1 tablet';

  // Parse timing columns (look for pattern of numbers and dashes)
  const timingPattern = line.match(/[1-9-]\s+[1-9-]\s+[1-9-]\s+[1-9-]/);
  const timing = { morning: false, noon: false, evening: false, night: false };
  
  if (timingPattern) {
    const timingParts = timingPattern[0].split(/\s+/);
    timing.morning = timingParts[0] !== '-' && /\d/.test(timingParts[0]);
    timing.noon = timingParts[1] !== '-' && /\d/.test(timingParts[1]);
    timing.evening = timingParts[2] !== '-' && /\d/.test(timingParts[2]);
    timing.night = timingParts[3] !== '-' && /\d/.test(timingParts[3]);
  } else {
    // Default to morning if no timing found
    timing.morning = true;
  }

  // Convert timing to frequency
  const activeTimes = Object.values(timing).filter(Boolean).length;
  let frequency = 'once daily';
  if (activeTimes === 2) frequency = 'twice daily';
  else if (activeTimes === 3) frequency = 'three times daily';
  else if (activeTimes === 4) frequency = 'four times daily';

  // Extract duration (last number in the line)
  const durationMatch = line.match(/(\d+)\s*$/);
  const duration = durationMatch ? `${durationMatch[1]} days` : '7 days';

  return {
    name: medName,
    strength,
    dosage,
    frequency,
    duration,
    timing,
    instructions: 'Take as prescribed'
  };
}

/**
 * Generate reminder times based on timing information
 */
function generateReminderTimes(timing: any): string[] {
  const times = [];
  
  if (timing.morning) times.push('08:00');
  if (timing.noon) times.push('12:00');
  if (timing.evening) times.push('18:00');
  if (timing.night) times.push('22:00');
  
  // Default to morning if no times specified
  if (times.length === 0) {
    times.push('08:00');
  }
  
  return times;
}

/**
 * Extract duration in days from duration string
 */
function extractDurationDays(duration: string): number {
  if (!duration) return 7;
  
  const match = duration.match(/(\d+)/);
  return match ? parseInt(match[1]) : 7;
}
