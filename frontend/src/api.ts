import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
  timeout: 30000,
});

export type Connection = {
  engine: string;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
};

export async function testConnection(connection: Connection) {
  const { data } = await api.post("/connections/test", connection);
  return data;
}

export async function discoverSchemas(connection: Connection) {
  const { data } = await api.post("/discovery/schemas", connection);
  return data;
}

export async function discoverTables(connection: Connection, schema: string) {
  const { data } = await api.post(
    `/discovery/tables?schema=${encodeURIComponent(schema)}`,
    connection
  );
  return data;
}

export async function discoverColumns(
  connection: Connection,
  schema: string,
  table: string
) {
  const { data } = await api.post(
    `/discovery/columns?schema=${encodeURIComponent(schema)}&table=${encodeURIComponent(table)}`,
    connection
  );
  return data;
}

export async function createDependencyPlan(
  connection: Connection,
  sourceSchema: string,
  targetSchema: string
) {
  const { data } = await api.post("/migrations/plan/dependencies", {
    source: connection,
    source_schema: sourceSchema,
    target_schema: targetSchema,
  });
  return data;
}

export async function startMigration(payload: {
  source: Connection;
  target: Connection;
  source_schema: string;
  target_schema: string;
  tables: string[];
  batch_size: number;
  max_workers: number;
}) {
  const { data } = await api.post("/migrations/run", payload);
  return data;
}

export async function getMigration(jobId: number) {
  const { data } = await api.get(`/migrations/${jobId}`);
  return data;
}

export async function getMigrationEvents(jobId: number) {
  const { data } = await api.get(`/audit/${jobId}/events`);
  return data;
}
