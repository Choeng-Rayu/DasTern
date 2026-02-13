import { NextRequest, NextResponse } from 'next/server';
import { query } from '@/lib/db';
import { withDoctorAuth } from '@/lib/middleware/auth';

export const GET = withDoctorAuth(async (req, auth) => {
  const { searchParams } = new URL(req.url);
  const q = searchParams.get('query') || '';
  if (!q) return NextResponse.json([], { status: 200 });

  const result = await query(
    `SELECT id, first_name, last_name, email FROM users
     WHERE (first_name ILIKE $1 OR last_name ILIKE $1 OR email ILIKE $1)
     AND role = 'patient'
     LIMIT 10`,
    [`%${q}%`]
  );
  return NextResponse.json(result.rows, { status: 200 });
});