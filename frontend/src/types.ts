export type Connection = {
  engine: string;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
};

export type MigrationJob = {
  id: number;
  name: string;
  status: string;
  total_tables: number;
  completed_tables: number;
  total_rows: number;
  migrated_rows: number;
  error_count: number;
  error_message?: string | null;
};

export type AuditEvent = {
  id: number;
  event_type: string;
  table_name?: string | null;
  message: string;
  created_at: string;
};
