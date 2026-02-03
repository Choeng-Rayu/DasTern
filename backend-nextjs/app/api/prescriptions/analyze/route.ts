/**
 * API Route: Analyze Prescription Image (No Database Storage)
 * POST /api/prescriptions/analyze
 * 
 * Flow:
 * 1. Upload image
 * 2. OCR processing
 * 3. AI enhancement + reminder generation
 * 4. Return analysis results only
 */

import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

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

    // Convert file to buffer for forwarding to OCR service
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    // Step 1: Send image to OCR service
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
    console.log('OCR Data:', JSON.stringify(ocrData, null, 2));

    // Step 2: Send OCR data to AI service for enhancement and reminder generation
    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://ai-llm-service:8001';
    let aiResult: any = null;

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
            base_date: new Date().toISOString().split('T')[0]
          },
          { timeout: 60000 }
        );

        aiResult = aiResponse.data;
        
        console.log(`✅ AI enhancement complete.`);
        console.log('AI Result:', JSON.stringify(aiResult, null, 2));
      }
    } catch (aiError) {
      console.warn('⚠️ AI enhancement failed:', aiError);
      // Return OCR data only if AI fails
      return NextResponse.json({
        success: true,
        analysis_type: 'ocr_only',
        ocr_data: ocrData,
        ocr_text: ocrData.full_text || ocrData.text || ocrData.raw_text || '',
        ocr_confidence: ocrData.overall_confidence || ocrData.confidence || 0,
        ai_enhanced: false,
        error: 'AI enhancement failed'
      });
    }

    // Step 3: Build analysis report
    const analysisReport = buildAnalysisReport(ocrData, aiResult);

    // Return complete analysis (no database storage)
    return NextResponse.json({
      success: true,
      analysis_type: aiResult?.success ? 'full_ai_enhanced' : 'partial',
      ocr_data: {
        raw_text: ocrData.full_text || ocrData.text || ocrData.raw_text || '',
        confidence: ocrData.overall_confidence || ocrData.confidence || 0,
        language: ocrData.language || 'unknown',
        processing_time: ocrData.processing_time || 0
      },
      ai_enhancement: aiResult?.success ? {
        prescription: aiResult.prescription,
        reminders: aiResult.reminders,
        metadata: aiResult.metadata,
        validation: aiResult.validation
      } : null,
      analysis: analysisReport,
      summary: {
        total_medications: aiResult?.prescription?.medications?.length || 0,
        total_reminders: aiResult?.reminders?.length || 0,
        confidence_score: aiResult?.metadata?.confidence_score || 0,
        languages_detected: [ocrData.language || 'en'],
        time_slots_found: extractTimeSlots(aiResult),
        duration_days: extractDurationInfo(aiResult)
      }
    });

  } catch (error: any) {
    console.error('❌ Error analyzing prescription:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to analyze prescription',
        details: error.message,
        stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
      },
      { status: 500 }
    );
  }
}

/**
 * Build detailed analysis report
 */
function buildAnalysisReport(ocrData: any, aiResult: any) {
  const report: any = {
    extraction_quality: {},
    medications_analysis: [],
    reminders_breakdown: [],
    recommendations: [],
    issues: []
  };

  // OCR Quality Analysis
  const ocrConfidence = ocrData.overall_confidence || ocrData.confidence || 0;
  report.extraction_quality = {
    ocr_confidence: ocrConfidence,
    ocr_quality: ocrConfidence > 0.8 ? 'high' : ocrConfidence > 0.5 ? 'medium' : 'low',
    text_length: (ocrData.full_text || ocrData.text || '').length,
    language_detected: ocrData.language || 'unknown'
  };

  // AI Enhancement Analysis
  if (aiResult?.success) {
    const aiConfidence = aiResult.metadata?.confidence_score || 0;
    report.extraction_quality.ai_confidence = aiConfidence;
    report.extraction_quality.ai_quality = aiConfidence > 0.8 ? 'high' : aiConfidence > 0.5 ? 'medium' : 'low';
    
    // Validate medications
    const medications = aiResult.prescription?.medications || [];
    for (let i = 0; i < medications.length; i++) {
      const med = medications[i];
      const medAnalysis: any = {
        index: i + 1,
        name: med.name,
        dosage: med.dosage,
        quantity: med.quantity,
        schedule: med.schedule,
        issues: []
      };

      // Check for issues
      if (!med.name || med.name === 'Unknown Medication') {
        medAnalysis.issues.push('Medication name unclear or not detected');
        report.issues.push(`Medication ${i + 1}: Name not properly extracted`);
      }

      if (!med.dosage) {
        medAnalysis.issues.push('Dosage information missing');
      }

      if (!med.schedule || !med.schedule.times || med.schedule.times.length === 0) {
        medAnalysis.issues.push('No timing information found');
        report.issues.push(`Medication ${i + 1}: No reminder times detected`);
      }

      report.medications_analysis.push(medAnalysis);
    }

    // Reminders Analysis
    const reminders = aiResult.reminders || [];
    const timeSlotCounts: Record<string, number> = {};
    
    for (const reminder of reminders) {
      const slot = reminder.time_slot;
      timeSlotCounts[slot] = (timeSlotCounts[slot] || 0) + 1;
      
      report.reminders_breakdown.push({
        medication: reminder.medication_name,
        time_slot: slot,
        scheduled_time: reminder.scheduled_time,
        dose: reminder.dose_amount,
        duration: `${reminder.start_date} to ${reminder.end_date}`,
        notification_preview: reminder.notification_body
      });
    }

    report.time_slot_distribution = timeSlotCounts;

    // Generate recommendations
    if (medications.length === 0) {
      report.recommendations.push('No medications detected. Try uploading a clearer image.');
    } else {
      report.recommendations.push(`Successfully detected ${medications.length} medications`);
      
      if (ocrConfidence < 0.7) {
        report.recommendations.push('OCR confidence is low. Consider manual review of extracted data.');
      }

      if (aiConfidence < 0.7) {
        report.recommendations.push('AI extraction confidence is moderate. Verify medication names and dosages.');
      }

      const totalReminders = reminders.length;
      report.recommendations.push(`Generated ${totalReminders} medication reminders`);
      
      // Check for complex schedules
      const complexMeds = medications.filter((m: any) => 
        m.schedule?.times?.length > 2
      );
      if (complexMeds.length > 0) {
        report.recommendations.push(`${complexMeds.length} medications have complex schedules (3+ times daily). Ensure patient understands timing.`);
      }
    }
  } else {
    report.issues.push('AI enhancement failed - using raw OCR data only');
    report.recommendations.push('Please try again or manually enter prescription data');
  }

  return report;
}

/**
 * Extract time slots from AI result
 */
function extractTimeSlots(aiResult: any): string[] {
  if (!aiResult?.prescription?.medications) return [];
  
  const slots = new Set<string>();
  for (const med of aiResult.prescription.medications) {
    if (med.schedule?.times) {
      med.schedule.times.forEach((t: string) => slots.add(t));
    }
  }
  
  return Array.from(slots);
}

/**
 * Extract duration information
 */
function extractDurationInfo(aiResult: any): any {
  if (!aiResult?.prescription?.medications) return null;
  
  const durations = aiResult.prescription.medications
    .map((m: any) => m.duration_days)
    .filter((d: any) => d != null);
  
  if (durations.length === 0) return null;
  
  return {
    min_days: Math.min(...durations),
    max_days: Math.max(...durations),
    average_days: durations.reduce((a: number, b: number) => a + b, 0) / durations.length,
    all_durations: durations
  };
}
