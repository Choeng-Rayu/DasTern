/**
 * API Route: Upload and Process Prescription Image with Enhanced AI Processing
 * POST /api/prescriptions/upload
 * 
 * Enhanced flow:
 * 1. Upload image
 * 2. OCR processing
 * 3. AI enhancement + reminder generation
 * 4. Save to database with structured data
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
    console.log(`📝 Created prescription record: ${prescriptionId}`);

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
        timeout: 60000,
      }
    );

    const ocrData = ocrResponse.data;
    console.log('📥 OCR Response received');

    // Step 3: Send OCR data to AI service for enhancement and reminder generation
    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://ai-llm-service:8001';
    let aiResult: any = null;
    let aiEnhanced = false;

    try {
      const rawText = ocrData.full_text || ocrData.text || ocrData.raw_text || '';
      
      if (rawText && rawText.trim()) {
        console.log(`🤖 Sending to AI service for enhancement and reminder generation`);
        
        const aiResponse = await axios.post(
          `${aiServiceUrl}/api/v1/prescription/enhance-and-generate-reminders`,
          {
            ocr_data: {
              raw_text: rawText,
              full_text: rawText,
              text: rawText,
              ...ocrData
            },
            base_date: new Date().toISOString().split('T')[0],
            patient_id: patientId
          },
          { timeout: 60000 }
        );

        aiResult = aiResponse.data;
        aiEnhanced = aiResult.success && aiResult.ai_enhanced;
        
        console.log(`✅ AI enhancement complete. Generated ${aiResult.metadata?.total_reminders || 0} reminders`);
      }
    } catch (aiError) {
      console.warn('⚠️ AI enhancement failed, using fallback parsing:', aiError);
    }

    // Step 4: Update prescription with OCR and AI results
    const rawText = ocrData.full_text || ocrData.text || ocrData.raw_text || '';
    const structuredData = aiResult?.prescription || null;
    
    await query(
      `UPDATE prescriptions 
       SET ocr_raw_text = $1, 
           ocr_corrected_text = $2,
           ocr_structured_data = $3,
           ocr_confidence_score = $4,
           ocr_language_detected = $5,
           ai_confidence_score = $6,
           hospital_name = $7,
           patient_name_on_doc = $8,
           patient_age = $9,
           patient_gender = $10,
           diagnosis = $11,
           department = $12,
           prescribing_doctor_name = $13,
           prescription_date = $14,
           status = $15,
           processing_completed_at = NOW(),
           updated_at = NOW()
       WHERE id = $16`,
      [
        rawText,
        aiResult?.prescription?.patient_info ? JSON.stringify(aiResult.prescription) : null,
        structuredData,
        ocrData.overall_confidence || ocrData.confidence || 0,
        ocrData.language || 'en',
        aiResult?.metadata?.confidence_score || 0,
        structuredData?.medical_info?.hospital_name || null,
        structuredData?.patient_info?.name || null,
        structuredData?.patient_info?.age || null,
        structuredData?.patient_info?.gender || null,
        structuredData?.medical_info?.diagnosis || null,
        structuredData?.medical_info?.department || null,
        structuredData?.medical_info?.doctor || null,
        structuredData?.medical_info?.date ? new Date(structuredData.medical_info.date) : null,
        aiResult?.success ? 'ai_processed' : 'ocr_completed',
        prescriptionId
      ]
    );

    // Step 5: Create medication records from AI results or fallback
    const medications: any[] = [];
    const medicationIds: any[] = [];
    
    if (aiResult?.success && aiResult.prescription?.medications) {
      // Use AI-extracted medications
      for (let i = 0; i < aiResult.prescription.medications.length; i++) {
        const med = aiResult.prescription.medications[i];
        
        const medResult = await query(
          `INSERT INTO medications 
           (prescription_id, sequence_number, name, strength, quantity, quantity_unit, 
            dosage_schedule, duration_days, instructions, form, created_at, updated_at)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW())
           RETURNING id`,
          [
            prescriptionId,
            i + 1,
            med.name,
            med.dosage || null,
            med.quantity || null,
            med.unit || 'tablet',
            JSON.stringify(med.schedule || {}),
            med.duration_days || null,
            med.instructions || null,
            'tablet'
          ]
        );
        
        medications.push(med);
        medicationIds.push({ id: medResult.rows[0].id, ...med });
      }
    } else {
      // Fallback: extract medications using simple parsing
      const fallbackMeds = extractMedications(rawText);
      
      for (let i = 0; i < fallbackMeds.length; i++) {
        const med = fallbackMeds[i];
        
        const medResult = await query(
          `INSERT INTO medications 
           (prescription_id, sequence_number, name, strength, quantity, 
            dosage_schedule, duration_days, instructions, created_at, updated_at)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
           RETURNING id`,
          [
            prescriptionId,
            i + 1,
            med.name,
            med.strength,
            med.quantity || null,
            JSON.stringify(med.schedule || {}),
            med.duration_days || 7,
            med.instructions || 'Take as prescribed'
          ]
        );
        
        medications.push(med);
        medicationIds.push({ id: medResult.rows[0].id, ...med });
      }
    }

    // Step 6: Create reminders from AI-generated reminders or fallback
    const reminders: any[] = [];
    
    if (aiResult?.success && aiResult.reminders && aiResult.reminders.length > 0) {
      // Use AI-generated reminders
      for (const reminder of aiResult.reminders) {
        // Find matching medication
        const medIndex = medications.findIndex(m => m.name === reminder.medication_name);
        const medicationId = medIndex >= 0 ? medicationIds[medIndex].id : null;
        
        if (medicationId) {
          const reminderResult = await query(
            `INSERT INTO medication_reminders 
             (medication_id, prescription_id, patient_id, time_slot, scheduled_time,
              dose_amount, dose_unit, start_date, end_date, days_of_week, 
              advance_notification_minutes, snooze_duration_minutes, is_active, created_at, updated_at)
             VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, TRUE, NOW(), NOW())
             RETURNING id`,
            [
              medicationId,
              prescriptionId,
              patientId || '00000000-0000-0000-0000-000000000000',
              reminder.time_slot,
              reminder.scheduled_time,
              reminder.dose_amount,
              reminder.dose_unit || 'tablet',
              reminder.start_date,
              reminder.end_date,
              reminder.days_of_week || [1, 2, 3, 4, 5, 6, 7],
              reminder.advance_notification_minutes || 15,
              reminder.snooze_duration_minutes || 10
            ]
          );
          
          reminders.push({
            reminder_id: reminderResult.rows[0].id,
            medication_name: reminder.medication_name,
            time_slot: reminder.time_slot,
            scheduled_time: reminder.scheduled_time,
            dose_amount: reminder.dose_amount,
            notification_title: reminder.notification_title,
            notification_body: reminder.notification_body
          });
        }
      }
    } else {
      // Fallback: generate reminders from medication schedules
      for (const med of medicationIds) {
        const schedule = med.schedule || {};
        const times = schedule.times || ['morning'];
        const times24h = schedule.times_24h || ['08:00'];
        const durationDays = med.duration_days || 7;
        
        for (let i = 0; i < times.length; i++) {
          const timeSlot = times[i];
          const scheduledTime = times24h[i] || '08:00';
          
          const reminderResult = await query(
            `INSERT INTO medication_reminders 
             (medication_id, prescription_id, patient_id, time_slot, scheduled_time,
              dose_amount, start_date, end_date, days_of_week, is_active, created_at, updated_at)
             VALUES ($1, $2, $3, $4, $5, $6, CURRENT_DATE, CURRENT_DATE + INTERVAL '${durationDays} days', $7, TRUE, NOW(), NOW())
             RETURNING id`,
            [
              med.id,
              prescriptionId,
              patientId || '00000000-0000-0000-0000-000000000000',
              timeSlot,
              scheduledTime,
              1,
              [1, 2, 3, 4, 5, 6, 7]
            ]
          );
          
          reminders.push({
            reminder_id: reminderResult.rows[0].id,
            medication_name: med.name,
            time_slot: timeSlot,
            scheduled_time: scheduledTime,
            dose_amount: 1
          });
        }
      }
    }

    // Step 7: Mark prescription as completed
    await query(
      `UPDATE prescriptions SET status = $1, updated_at = NOW() WHERE id = $2`,
      ['completed', prescriptionId]
    );

    // Return complete response
    return NextResponse.json({
      success: true,
      prescription_id: prescriptionId,
      patient_id: patientId,
      ocr_confidence: ocrData.overall_confidence || ocrData.confidence || 0,
      ai_enhanced: aiEnhanced,
      ai_confidence: aiResult?.metadata?.confidence_score || 0,
      medications_count: medications.length,
      reminders_count: reminders.length,
      prescription: aiResult?.prescription || null,
      reminders: reminders,
      metadata: {
        language_detected: ocrData.language || 'en',
        processing_method: aiEnhanced ? 'ai_enhanced' : 'ocr_fallback',
        validation: aiResult?.validation || null
      },
      message: `Prescription processed successfully. Created ${medications.length} medications and ${reminders.length} reminders.`
    });

  } catch (error: any) {
    console.error('❌ Error processing prescription:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to process prescription',
        details: error.message,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}

/**
 * Fallback medication extraction when AI enhancement fails
 */
function extractMedications(text: string): any[] {
  const medications = [];
  const lines = text.split('\n');
  
  // Known medication names from Khmer prescriptions
  const knownMedications = [
    'Calcium', 'Multivitamine', 'Amitriptyline', 'Butylscopolamine',
    'Celcoxx', 'Omeprazole', 'Paracetamol', 'Esome', 'Amoxicillin',
    'Metformin', 'Amlodipine', 'Losartan', 'Atorvastatin'
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
          dosage: '1 tablet',
          quantity: 14,
          unit: 'tablet',
          schedule: {
            times: ['morning'],
            times_24h: ['08:00'],
            frequency: 'once_daily'
          },
          duration_days: 7,
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
      quantity: 14,
      unit: 'tablet',
      schedule: {
        times: ['morning'],
        times_24h: ['08:00'],
        frequency: 'once_daily'
      },
      duration_days: 7,
      instructions: 'Take as prescribed'
    });
  }

  return medications;
}

/**
 * Parse a single medication line from Khmer prescription table
 */
function parseMedicationLine(line: string, knownMedications: string[]): any | null {
  const parts = line.split(/\s+/);
  if (parts.length < 4) return null;

  // Extract medication name
  let medName = null;
  for (const part of parts.slice(1)) {
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
  const strengthMatch = line.match(/(\d+)\s*(mg|ml|g)/i);
  const strength = strengthMatch ? strengthMatch[0] : null;

  // Extract quantity
  const quantityMatch = line.match(/(\d+)\s*(tablet|ថ្នាំ|គ្រាប់)/i);
  const quantity = quantityMatch ? parseInt(quantityMatch[1]) : 14;

  // Parse timing columns (look for pattern of numbers and dashes)
  const timingPattern = line.match(/[1-9-]\s+[1-9-]\s+[1-9-]\s+[1-9-]/);
  const times: string[] = [];
  const times24h: string[] = [];
  
  if (timingPattern) {
    const timingParts = timingPattern[0].split(/\s+/);
    const timeSlots = ['morning', 'noon', 'afternoon', 'night'];
    const timeValues = ['08:00', '12:00', '18:00', '21:00'];
    
    for (let i = 0; i < 4; i++) {
      if (timingParts[i] !== '-' && /\d/.test(timingParts[i])) {
        times.push(timeSlots[i]);
        times24h.push(timeValues[i]);
      }
    }
  }
  
  // Default to morning if no timing found
  if (times.length === 0) {
    times.push('morning');
    times24h.push('08:00');
  }

  // Extract duration (last number in the line)
  const durationMatch = line.match(/(\d+)\s*$/);
  const durationDays = durationMatch ? parseInt(durationMatch[1]) : 7;

  return {
    name: medName,
    dosage: strength || '1 tablet',
    quantity: quantity,
    unit: 'tablet',
    schedule: {
      times: times,
      times_24h: times24h,
      frequency: times.length === 1 ? 'once_daily' : 
                 times.length === 2 ? 'twice_daily' : 
                 times.length === 3 ? 'three_times_daily' : 'four_times_daily'
    },
    duration_days: durationDays,
    instructions: 'Take as prescribed'
  };
}
