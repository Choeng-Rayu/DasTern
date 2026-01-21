/**
 * API Route: Test Database Connection
 * GET /api/health
 */

import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    // Test database connection
    const result = await query('SELECT NOW() as time, version() as version');
    
    // Test OCR service
    const ocrServiceUrl = process.env.OCR_SERVICE_URL || 'http://ocr-service:8000';
    let ocrStatus = 'unavailable';
    try {
      const ocrResponse = await fetch(`${ocrServiceUrl}/health`, { signal: AbortSignal.timeout(5000) });
      if (ocrResponse.ok) ocrStatus = 'available';
    } catch (e) {
      ocrStatus = 'unavailable';
    }

    // Test AI service
    const aiServiceUrl = process.env.AI_SERVICE_URL || 'http://ai-llm-service:8001';
    let aiStatus = 'unavailable';
    try {
      const aiResponse = await fetch(`${aiServiceUrl}/health`, { signal: AbortSignal.timeout(5000) });
      if (aiResponse.ok) aiStatus = 'available';
    } catch (e) {
      aiStatus = 'unavailable';
    }

    return NextResponse.json({
      status: 'healthy',
      timestamp: result.rows[0].time,
      database: 'connected',
      services: {
        ocr: ocrStatus,
        ai: aiStatus
      }
    });
  } catch (error: any) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        error: error.message
      },
      { status: 500 }
    );
  }
}
