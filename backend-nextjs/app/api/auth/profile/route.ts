// import { NextRequest, NextResponse } from 'next/server';
// import { query } from '@/lib/db';
// import { verifyJwt } from '@/lib/jwt';

// export async function GET(req: NextRequest) {
//   try {
//     const auth = req.headers.get('authorization');
//     if (!auth || !auth.startsWith('Bearer ')) {
//       return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
//     }
//     const token = auth.slice(7);
//     const payload = verifyJwt(token);
//     if (!payload || typeof payload !== 'object' || !('userId' in payload)) {
//       return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
//     }

//     const userRes = await query('SELECT id, telephone, created_at FROM users WHERE id = $1', [payload.userId]);
//     if (userRes.rowCount === 0) {
//       return NextResponse.json({ error: 'User not found' }, { status: 404 });
//     }

//     return NextResponse.json(userRes.rows[0]);
//   } catch (e) {
//     return NextResponse.json({ error: 'Failed to fetch profile' }, { status: 500 });
//   }
// }