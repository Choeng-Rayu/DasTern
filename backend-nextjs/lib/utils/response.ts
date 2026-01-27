import { NextResponse } from 'next/server';

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
  errors?: Record<string, string>;
  meta?: {
    next_step?: string;
    required_fields?: string[];
    [key: string]: any;
  };
}

export function successResponse<T>(
  data: T,
  message?: string,
  meta?: ApiResponse['meta'],
  status: number = 200
): NextResponse<ApiResponse<T>> {
  return NextResponse.json(
    {
      success: true,
      message,
      data,
      meta
    },
    { status }
  );
}

export function errorResponse(
  error: string,
  status: number = 400,
  errors?: Record<string, string>
): NextResponse<ApiResponse> {
  return NextResponse.json(
    {
      success: false,
      error,
      errors
    },
    { status }
  );
}

export function validationError(
  errors: Record<string, string>
): NextResponse<ApiResponse> {
  return NextResponse.json(
    {
      success: false,
      error: 'Validation failed',
      errors
    },
    { status: 400 }
  );
}