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

    // Step 6: Save medications to database
    for (const med of medications) {
      await query(
        `INSERT INTO medications 
         (prescription_id, name, strength, dosage, frequency, duration, created_at, updated_at)
         VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())`,
        [
          prescriptionId,
          med.name,
          med.strength,
          med.dosage,
          med.frequency,
          med.duration
        ]
      );
    }

    // Return complete response
    return NextResponse.json({
      success: true,
      prescription_id: prescriptionId,
      ocr_text: correctedText,
      ocr_confidence: ocrData.confidence || 0,
      ai_enhanced: aiEnhanced,
      medications: medications,
      message: 'Prescription processed successfully'
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
 * Simple medication extraction from OCR text
 * This is a basic implementation - can be enhanced with AI/ML
 */
function extractMedications(text: string) {
  const medications = [];
  const lines = text.split('\n');

  // Simple pattern matching for medications
  // Format: MedicationName 500mg - 1 tablet twice daily for 7 days
  const medPattern = /([A-Za-z]+)\s*(\d+\s*mg|ml)?.*?(\d+\s*tablet|capsule|ml)?\s*(once|twice|thrice|[\d]+\s*times)?\s*(daily|weekly|monthly)?.*?(for\s*\d+\s*days)?/i;

  for (const line of lines) {
    const match = line.match(medPattern);
    if (match) {
      medications.push({
        name: match[1],
        strength: match[2] || null,
        dosage: match[3] || null,
        frequency: `${match[4] || 'once'} ${match[5] || 'daily'}`,
        duration: match[6] || null
      });
    }
  }

  // If no medications found, create a placeholder
  if (medications.length === 0) {
    medications.push({
      name: 'Unknown Medication',
      strength: null,
      dosage: '1 tablet',
      frequency: 'twice daily',
      duration: 'for 7 days'
    });
  }

  return medications;
}
