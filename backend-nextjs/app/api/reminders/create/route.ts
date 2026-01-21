/**
 * API Route: Create Medication Reminders
 * POST /api/reminders/create
 */

import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const {
      prescription_id,
      patient_id,
      medication_id,
      reminder_times,
      start_date,
      end_date,
      days_of_week
    } = body;

    // Validate required fields
    if (!medication_id || !patient_id || !reminder_times || !start_date) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Create reminder in database
    const result = await query(
      `INSERT INTO medication_reminders 
       (medication_id, patient_id, reminder_times, start_date, end_date, days_of_week, is_active, created_at, updated_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
       RETURNING id`,
      [
        medication_id,
        patient_id,
        reminder_times, // Array of times like ['08:00', '20:00']
        start_date,
        end_date || null,
        days_of_week || [1, 2, 3, 4, 5, 6, 7], // Default: all days
        true
      ]
    );

    const reminderId = result.rows[0].id;

    // Get medication details for response
    const medicationResult = await query(
      `SELECT m.name, m.dosage, m.frequency, m.duration
       FROM medications m
       WHERE m.id = $1`,
      [medication_id]
    );

    const medication = medicationResult.rows[0];

    return NextResponse.json({
      success: true,
      reminder_id: reminderId,
      medication: medication,
      reminder_times: reminder_times,
      start_date: start_date,
      end_date: end_date,
      message: 'Reminder created successfully'
    });

  } catch (error: any) {
    console.error('❌ Error creating reminder:', error);
    
    return NextResponse.json(
      {
        error: 'Failed to create reminder',
        details: error.message
      },
      { status: 500 }
    );
  }
}

/**
 * GET: Fetch reminders for a patient
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const patientId = searchParams.get('patient_id');

    if (!patientId) {
      return NextResponse.json(
        { error: 'patient_id is required' },
        { status: 400 }
      );
    }

    // Fetch all active reminders for the patient
    const result = await query(
      `SELECT 
        mr.id as reminder_id,
        mr.reminder_times,
        mr.start_date,
        mr.end_date,
        mr.days_of_week,
        mr.is_active,
        m.name as medication_name,
        m.dosage,
        m.frequency,
        m.strength,
        p.id as prescription_id,
        p.prescription_date
       FROM medication_reminders mr
       JOIN medications m ON mr.medication_id = m.id
       JOIN prescriptions p ON m.prescription_id = p.id
       WHERE mr.patient_id = $1 AND mr.is_active = true
       ORDER BY mr.created_at DESC`,
      [patientId]
    );

    return NextResponse.json({
      success: true,
      reminders: result.rows
    });

  } catch (error: any) {
    console.error('❌ Error fetching reminders:', error);
    
    return NextResponse.json(
      {
        error: 'Failed to fetch reminders',
        details: error.message
      },
      { status: 500 }
    );
  }
}
