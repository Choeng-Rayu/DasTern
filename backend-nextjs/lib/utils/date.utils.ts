/**
 * Converts a date string from 'DD-MM-YYYY' or 'YYYY-MM-DD' to 'YYYY-MM-DD' for PostgreSQL.
 */
export function toPostgresDate(dateStr: string): string {
  // If already in YYYY-MM-DD, return as is
  if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
  // Convert from DD-MM-YYYY to YYYY-MM-DD
  const [day, month, year] = dateStr.split('-');
  return `${year}-${month}-${day}`;
}