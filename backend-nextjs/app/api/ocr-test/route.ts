/**
 * API Route: OCR Test - Process images without database storage
 * POST /api/ocr-test
 * 
 * This endpoint focuses only on OCR testing and returns results formatted for reminder generation.
 * No database operations are performed.
 */

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('image') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No image file provided' },
        { status: 400 }
      );
    }

    console.log(`📤 Testing OCR for: ${file.name} (${file.size} bytes)`);

    // Convert file to buffer
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // Send to OCR service
    const ocrServiceUrl = process.env.OCR_SERVICE_URL || 'http://ocr-service:8002';
    
    const ocrFormData = new FormData();
    const blob = new Blob([buffer], { type: file.type });
    ocrFormData.append('file', blob, file.name);

    console.log(`📤 Sending to OCR service: ${ocrServiceUrl}/ocr`);

    const ocrResponse = await fetch(`${ocrServiceUrl}/ocr`, {
      method: 'POST',
      body: ocrFormData,
    });

    if (!ocrResponse.ok) {
      throw new Error(`OCR service error: ${ocrResponse.status}`);
    }

    const ocrData = await ocrResponse.json();
    console.log('📥 OCR Response received');

    const rawText = ocrData.full_text || ocrData.text || ocrData.raw_text || '';
    
    // Try AI enhancement (optional)
    let aiEnhanced = false;
    let correctedText = rawText;
    let aiError = null;

    try {
      if (rawText && rawText.trim()) {
        const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://ai-llm-service:8001';
        console.log(`🤖 Sending to AI service: ${aiServiceUrl}/correct-ocr`);
        
        const aiResponse = await fetch(`${aiServiceUrl}/correct-ocr`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            text: rawText,
            language: ocrData.language || 'en'
          }),
        });

        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          if (aiData.corrected_text) {
            correctedText = aiData.corrected_text;
            aiEnhanced = true;
            console.log('✨ AI correction applied');
          }
        }
      }
    } catch (aiErr: any) {
      aiError = aiErr.message;
      console.warn('⚠️ AI service unavailable:', aiErr.message);
    }

    // Parse medications and format for reminder generation
    const medications = extractMedicationsForReminders(correctedText);

    // Return results in reminder-ready format
    return NextResponse.json({
      success: true,
      file: {
        name: file.name,
        size: file.size,
        type: file.type
      },
      ocr: {
        raw_text: rawText,
        corrected_text: correctedText,
        confidence: ocrData.overall_confidence || ocrData.confidence || 0,
        language: ocrData.language || 'unknown',
        ai_enhanced: aiEnhanced,
        ai_error: aiError
      },
      medications: medications,
      reminders_preview: medications.map(med => ({
        medication_name: med.name,
        dosage: med.dosage,
        frequency: med.frequency,
        times_per_day: med.times_per_day,
        suggested_times: med.suggested_reminder_times,
        duration: med.duration,
        instructions: med.instructions
      })),
      message: `OCR completed. Detected ${medications.length} medications ready for reminder setup.`
    });

  } catch (error: any) {
    console.error('❌ OCR Test Error:', error);
    
    return NextResponse.json(
      {
        error: 'OCR test failed',
        details: error.message,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}

/**
 * Extract medications from text and format for reminder generation
 */
function extractMedicationsForReminders(text: string) {
  const medications = [];
  const lines = text.split('\n').filter(line => line.trim());
  
  // Enhanced patterns for medication extraction
  const medPatterns = {
    // Pattern: "Medicine Name 500mg"
    nameStrength: /([A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|units?)/i,
    // Pattern: "Take 2 times a day" or "3x daily"
    frequency: /(once|twice|three|1|2|3|4)\s*(?:times?\s*(?:per|a|\/)\s*day|x\s*daily|daily)/i,
    // Pattern: "for 7 days" or "5 days"
    duration: /(?:for\s+)?(\d+)\s*(?:days?|weeks?|months?)/i,
    // Pattern: "before/after meal" or "morning/evening"
    timing: /(before|after)\s*(?:meal|food|breakfast|lunch|dinner)|morning|evening|night|bedtime/i
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const nameMatch = line.match(medPatterns.nameStrength);
    
    if (nameMatch) {
      const medication: any = {
        name: nameMatch[1].trim(),
        strength: nameMatch[2],
        unit: nameMatch[3],
        dosage: `${nameMatch[2]}${nameMatch[3]}`,
        frequency: 'As prescribed',
        times_per_day: 1,
        duration: '7 days',
        timing: 'with meal',
        instructions: line.trim(),
        suggested_reminder_times: ['08:00', '20:00']
      };

      // Check next few lines for frequency/duration info
      const contextLines = lines.slice(i, Math.min(i + 3, lines.length)).join(' ');
      
      const freqMatch = contextLines.match(medPatterns.frequency);
      if (freqMatch) {
        const freq = freqMatch[1].toLowerCase();
        if (freq === 'once' || freq === '1') {
          medication.times_per_day = 1;
          medication.frequency = 'Once daily';
          medication.suggested_reminder_times = ['08:00'];
        } else if (freq === 'twice' || freq === '2') {
          medication.times_per_day = 2;
          medication.frequency = 'Twice daily';
          medication.suggested_reminder_times = ['08:00', '20:00'];
        } else if (freq === 'three' || freq === '3') {
          medication.times_per_day = 3;
          medication.frequency = 'Three times daily';
          medication.suggested_reminder_times = ['08:00', '14:00', '20:00'];
        } else if (freq === '4') {
          medication.times_per_day = 4;
          medication.frequency = 'Four times daily';
          medication.suggested_reminder_times = ['08:00', '12:00', '16:00', '20:00'];
        }
      }

      const durMatch = contextLines.match(medPatterns.duration);
      if (durMatch) {
        medication.duration = durMatch[0].trim();
      }

      const timingMatch = contextLines.match(medPatterns.timing);
      if (timingMatch) {
        medication.timing = timingMatch[0].trim();
      }

      medications.push(medication);
    }
  }

  return medications;
}
