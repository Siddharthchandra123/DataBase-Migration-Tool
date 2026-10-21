import React, { useEffect, useMemo, useState } from "react";
import {
  createDependencyPlan,
  discoverSchemas,
  discoverTables,
  getMigration,
  getMigrationEvents,
  startMigration,
  testConnection,
} from "./api";
import type { AuditEvent, Connection, MigrationJob } from "./types";

const emptyConnection: Connection = {
  engine: "db2",
  host: "",
  port: 50000,
  database: "",
  username: "",
  password: "",
};

function App() {
  const [source, setSource] = useState<Connection>(emptyConnection);
  const [target, setTarget] = useState<Connection>({
    ...emptyConnection,
    engine: "postgresql",
    port: 5432,
  });

  const [sourceSchema, setSourceSchema] = useState("");
  const [targetSchema, setTargetSchema] = useState("public");
  const [schemas, setSchemas] = useState<string[]>([]);
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTables, setSelectedTables] = useState<string[]>([]);
  const [orderedTables, setOrderedTables] = useState<string[]>([]);
  const [job, setJob] = useState<MigrationJob | null>(null);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [batchSize, setBatchSize] = useState(5000);
  const [workers, setWorkers] = useState(2);

  const progress = useMemo(() => {
    if (!job || !job.total_tables) return 0;
    return Math.round((job.completed_tables / job.total_tables) * 100);
  }, [job]);

  useEffect(() => {
    if (!job || ["COMPLETED", "FAILED", "COMPLETED_WITH_ERRORS"].includes(job.status)) {
      return;
    }

    const timer = window.setInterval(async () => {
      try {
        const latest = await getMigration(job.id);
        setJob(latest);
        const audit = await getMigrationEvents(job.id);
        setEvents(audit.events || []);
      } catch {
        // Keep the last known job state.
      }
    }, 2000);

    return () => window.clearInterval(timer);
  }, [job?.id, job?.status]);

  async function handleTest() {
    setLoading(true);
    setMessage("");
    try {
      const result = await testConnection(source);
      setMessage(result.message || "Source connection successful.");
    } catch (error: any) {
      setMessage(error?.response?.data?.detail || "Connection failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDiscover() {
    setLoading(true);
    setMessage("");
    try {
      const result = await discoverSchemas(source);
      setSchemas(result.schemas || []);
      setMessage(`Discovered ${result.schemas?.length || 0} schemas.`);
    } catch (error: any) {
      setMessage(error?.response?.data?.detail || "Discovery failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleTables() {
    if (!sourceSchema) return;
    setLoading(true);
    try {
      const result = await discoverTables(source, sourceSchema);
      setTables(result.tables || []);
      setSelectedTables(result.tables || []);
      setMessage(`Discovered ${result.tables?.length || 0} tables.`);
    } catch (error: any) {
      setMessage(error?.response?.data?.detail || "Table discovery failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handlePlan() {
    if (!sourceSchema) return;
    setLoading(true);
    try {
      const result = await createDependencyPlan(
        source,
        sourceSchema,
        targetSchema
      );
      setOrderedTables(result.execution_order || []);
      setSelectedTables(result.execution_order || []);
      setMessage("Dependency-aware migration plan created.");
    } catch (error: any) {
      setMessage(error?.response?.data?.detail || "Planning failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleStart() {
    if (!sourceSchema || selectedTables.length === 0) return;

    setLoading(true);
    try {
      const result = await startMigration({
        source,
        target,
        source_schema: sourceSchema,
        target_schema: targetSchema,
        tables: selectedTables,
        batch_size: batchSize,
        max_workers: workers,
      });

      setJob({
        id: result.job_id,
        name: `${sourceSchema} → ${targetSchema}`,
        status: result.status,
        total_tables: selectedTables.length,
        completed_tables: 0,
        total_rows: 0,
        migrated_rows: 0,
        error_count: 0,
      });

      setEvents([]);
      setMessage(`Migration job #${result.job_id} started.`);
    } catch (error: any) {
      setMessage(error?.response?.data?.detail || "Migration could not start.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="eyebrow">ENTERPRISE DATA PLATFORM</div>
          <h1>Migration Console</h1>
          <p>Discover, plan, migrate and validate databases.</p>
        </div>
        <div className="health">● API Console</div>
      </header>

      {message && <div className="notice">{message}</div>}

      <section className="grid two">
        <ConnectionCard
          title="Source Database"
          connection={source}
          setConnection={setSource}
          defaultPort={50000}
        />
        <ConnectionCard
          title="Target Database"
          connection={target}
          setConnection={setTarget}
          defaultPort={5432}
        />
      </section>

      <section className="panel">
        <div className="section-title">
          <div>
            <h2>1. Connect & Discover</h2>
            <p>Start with the source DB2 environment.</p>
          </div>
          <div className="actions">
            <button onClick={handleTest} disabled={loading}>
              Test Source
            </button>
            <button onClick={handleDiscover} disabled={loading}>
              Discover Schemas
            </button>
          </div>
        </div>

        <div className="form-row">
          <label>
            Source Schema
            <select
              value={sourceSchema}
              onChange={(e) => setSourceSchema(e.target.value)}
            >
              <option value="">Select schema</option>
              {schemas.map((schema) => (
                <option key={schema}>{schema}</option>
              ))}
            </select>
          </label>

          <label>
            Target Schema
            <input
              value={targetSchema}
              onChange={(e) => setTargetSchema(e.target.value)}
            />
          </label>

          <button onClick={handleTables} disabled={!sourceSchema || loading}>
            Discover Tables
          </button>
        </div>
      </section>

      <section className="panel">
        <div className="section-title">
          <div>
            <h2>2. Select & Plan</h2>
            <p>{selectedTables.length} tables selected.</p>
          </div>
          <button onClick={handlePlan} disabled={!sourceSchema || loading}>
            Build Dependency Plan
          </button>
        </div>

        <div className="table-list">
          {(orderedTables.length ? orderedTables : tables).map((table) => (
            <label className="table-row" key={table}>
              <input
                type="checkbox"
                checked={selectedTables.includes(table)}
                onChange={() =>
                  setSelectedTables((current) =>
                    current.includes(table)
                      ? current.filter((item) => item !== table)
                      : [...current, table]
                  )
                }
              />
              <span>{table}</span>
            </label>
          ))}
          {tables.length === 0 && (
            <div className="empty">Discover tables to populate this list.</div>
          )}
        </div>
      </section>

      <section className="panel">
        <div className="section-title">
          <div>
            <h2>3. Migration Configuration</h2>
            <p>Control batch size and parallel table workers.</p>
          </div>
        </div>

        <div className="form-row">
          <label>
            Batch Size
            <input
              type="number"
              min={100}
              max={100000}
              value={batchSize}
              onChange={(e) => setBatchSize(Number(e.target.value))}
            />
          </label>

          <label>
            Parallel Workers
            <input
              type="number"
              min={1}
              max={16}
              value={workers}
              onChange={(e) => setWorkers(Number(e.target.value))}
            />
          </label>

          <button className="primary" onClick={handleStart} disabled={loading || !selectedTables.length}>
            Start Migration
          </button>
        </div>
      </section>

      {job && (
        <section className="panel">
          <div className="section-title">
            <div>
              <h2>4. Live Migration</h2>
              <p>Job #{job.id} · {job.name}</p>
            </div>
            <strong className={`job-status ${job.status.toLowerCase()}`}>
              {job.status}
            </strong>
          </div>

          <div className="progress">
            <div style={{ width: `${progress}%` }} />
          </div>

          <div className="stats">
            <span><b>{progress}%</b> complete</span>
            <span><b>{job.completed_tables}</b> / {job.total_tables} tables</span>
            <span><b>{job.migrated_rows.toLocaleString()}</b> rows</span>
            <span><b>{job.error_count}</b> errors</span>
          </div>

          <div className="events">
            <h3>Audit Timeline</h3>
            {events.length === 0 ? (
              <div className="empty">Waiting for migration events...</div>
            ) : (
              events.map((event) => (
                <div className="event" key={event.id}>
                  <span>{new Date(event.created_at).toLocaleTimeString()}</span>
                  <b>{event.event_type}</b>
                  <p>{event.message}</p>
                </div>
              ))
            )}
          </div>
        </section>
      )}
    </div>
  );
}

function ConnectionCard({
  title,
  connection,
  setConnection,
  defaultPort,
}: {
  title: string;
  connection: Connection;
  setConnection: React.Dispatch<React.SetStateAction<Connection>>;
  defaultPort: number;
}) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      <p>Database connection parameters</p>

      <div className="form-grid">
        <label>
          Engine
          <select
            value={connection.engine}
            onChange={(e) =>
              setConnection((current) => ({
                ...current,
                engine: e.target.value,
              }))
            }
          >
            <option value="db2">DB2</option>
            <option value="postgresql">PostgreSQL</option>
          </select>
        </label>

        <label>
          Host
          <input
            value={connection.host}
            placeholder="db.example.com"
            onChange={(e) =>
              setConnection((current) => ({
                ...current,
                host: e.target.value,
              }))
            }
          />
        </label>

        <label>
          Port
          <input
            type="number"
            value={connection.port || defaultPort}
            onChange={(e) =>
              setConnection((current) => ({
                ...current,
                port: Number(e.target.value),
              }))
            }
          />
        </label>

        <label>
          Database
          <input
            value={connection.database}
            onChange={(e) =>
              setConnection((current) => ({
                ...current,
                database: e.target.value,
              }))
            }
          />
        </label>

        <label>
          Username
          <input
            value={connection.username}
            onChange={(e) =>
              setConnection((current) => ({
                ...current,
                username: e.target.value,
              }))
            }
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={connection.password}
            onChange={(e) =>
              setConnection((current) => ({
                ...current,
                password: e.target.value,
              }))
            }
          />
        </label>
      </div>
    </section>
  );
}

export default App;
