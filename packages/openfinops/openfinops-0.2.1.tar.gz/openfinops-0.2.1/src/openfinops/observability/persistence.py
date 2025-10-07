"""
Persistence Layer for Telemetry Data
====================================

Provides pluggable storage backends for long-term telemetry data retention
and historical analysis. Supports in-memory (default), SQLite, PostgreSQL,
and TimescaleDB for time-series optimization.

Features:
- Pluggable storage backends
- Automatic schema initialization
- Data retention policies
- Query optimization for time-series data
- Batch insertion for performance
- Connection pooling
"""

# Copyright (c) 2025 Infinidatum
# Author: Duraimurugan Rajamanickam
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import time
import json
import sqlite3
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import asdict
from collections import deque
from enum import Enum


class StorageBackend(Enum):
    """Available storage backends"""
    IN_MEMORY = "in_memory"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    TIMESCALEDB = "timescaledb"


class PersistenceConfig:
    """Configuration for persistence layer"""

    def __init__(
        self,
        backend: StorageBackend = StorageBackend.IN_MEMORY,
        connection_string: Optional[str] = None,
        retention_days: int = 90,
        batch_size: int = 100,
        batch_interval_seconds: float = 60.0,
        enable_compression: bool = False,
        max_memory_entries: int = 10000
    ):
        self.backend = backend
        self.connection_string = connection_string or self._default_connection_string(backend)
        self.retention_days = retention_days
        self.batch_size = batch_size
        self.batch_interval_seconds = batch_interval_seconds
        self.enable_compression = enable_compression
        self.max_memory_entries = max_memory_entries

    def _default_connection_string(self, backend: StorageBackend) -> str:
        """Get default connection string for backend"""
        if backend == StorageBackend.SQLITE:
            return "sqlite:///openfinops_telemetry.db"
        elif backend == StorageBackend.POSTGRESQL:
            return "postgresql://localhost:5432/openfinops"
        elif backend == StorageBackend.TIMESCALEDB:
            return "postgresql://localhost:5432/openfinops"
        return ""


class BasePersistenceBackend(ABC):
    """Abstract base class for persistence backends"""

    def __init__(self, config: PersistenceConfig):
        self.config = config
        self.write_buffer: Dict[str, List[Dict[str, Any]]] = {
            'system_metrics': [],
            'service_metrics': [],
            'cost_entries': [],
            'alerts': []
        }
        self.buffer_lock = threading.Lock()
        self.flush_thread = None
        self.running = False

    @abstractmethod
    def initialize_schema(self):
        """Initialize database schema"""
        pass

    @abstractmethod
    def store_system_metric(self, metric: Dict[str, Any]):
        """Store a system metric"""
        pass

    @abstractmethod
    def store_service_metric(self, metric: Dict[str, Any]):
        """Store a service metric"""
        pass

    @abstractmethod
    def store_cost_entry(self, entry: Dict[str, Any]):
        """Store a cost entry"""
        pass

    @abstractmethod
    def store_alert(self, alert: Dict[str, Any]):
        """Store an alert"""
        pass

    @abstractmethod
    def query_system_metrics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        cluster_id: Optional[str] = None,
        node_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query system metrics"""
        pass

    @abstractmethod
    def query_cost_entries(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        category: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query cost entries"""
        pass

    @abstractmethod
    def cleanup_old_data(self):
        """Remove data older than retention period"""
        pass

    @abstractmethod
    def close(self):
        """Close database connections"""
        pass

    def start_auto_flush(self):
        """Start automatic buffer flushing"""
        self.running = True
        self.flush_thread = threading.Thread(target=self._auto_flush_loop, daemon=True)
        self.flush_thread.start()

    def stop_auto_flush(self):
        """Stop automatic buffer flushing"""
        self.running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5)
        self.flush_buffer()

    def _auto_flush_loop(self):
        """Automatic flush loop"""
        while self.running:
            time.sleep(self.config.batch_interval_seconds)
            self.flush_buffer()

    @abstractmethod
    def flush_buffer(self):
        """Flush buffered writes to storage"""
        pass


class InMemoryBackend(BasePersistenceBackend):
    """In-memory storage backend (no persistence)"""

    def __init__(self, config: PersistenceConfig):
        super().__init__(config)
        self.system_metrics = deque(maxlen=config.max_memory_entries)
        self.service_metrics = deque(maxlen=config.max_memory_entries)
        self.cost_entries = deque(maxlen=config.max_memory_entries)
        self.alerts = deque(maxlen=config.max_memory_entries)

    def initialize_schema(self):
        """No schema needed for in-memory"""
        pass

    def store_system_metric(self, metric: Dict[str, Any]):
        self.system_metrics.append(metric)

    def store_service_metric(self, metric: Dict[str, Any]):
        self.service_metrics.append(metric)

    def store_cost_entry(self, entry: Dict[str, Any]):
        self.cost_entries.append(entry)

    def store_alert(self, alert: Dict[str, Any]):
        self.alerts.append(alert)

    def query_system_metrics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        cluster_id: Optional[str] = None,
        node_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        results = list(self.system_metrics)

        if start_time:
            results = [m for m in results if m.get('timestamp', 0) >= start_time]
        if end_time:
            results = [m for m in results if m.get('timestamp', 0) <= end_time]
        if cluster_id:
            results = [m for m in results if m.get('cluster_id') == cluster_id]
        if node_id:
            results = [m for m in results if m.get('node_id') == node_id]

        return results[-limit:]

    def query_cost_entries(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        category: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        results = list(self.cost_entries)

        if start_time:
            results = [e for e in results if e.get('timestamp', 0) >= start_time]
        if end_time:
            results = [e for e in results if e.get('timestamp', 0) <= end_time]
        if category:
            results = [e for e in results if e.get('category') == category]
        if resource_id:
            results = [e for e in results if e.get('resource_id') == resource_id]

        return results[-limit:]

    def cleanup_old_data(self):
        """In-memory storage auto-manages via deque maxlen"""
        pass

    def flush_buffer(self):
        """No buffering needed for in-memory"""
        pass

    def close(self):
        """Nothing to close for in-memory"""
        pass


class SQLiteBackend(BasePersistenceBackend):
    """SQLite storage backend"""

    def __init__(self, config: PersistenceConfig):
        super().__init__(config)
        self.db_path = config.connection_string.replace("sqlite:///", "")
        self.conn = None
        self.initialize_schema()

    def _get_connection(self):
        """Get or create database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def initialize_schema(self):
        """Initialize SQLite schema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                cluster_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                gpu_usage REAL,
                network_io TEXT,
                throughput REAL,
                latency_p50 REAL,
                latency_p95 REAL,
                latency_p99 REAL,
                error_rate REAL,
                cost_per_hour REAL,
                health_status TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp
            ON system_metrics(timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_metrics_cluster
            ON system_metrics(cluster_id, timestamp)
        """)

        # Service metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                service_name TEXT NOT NULL,
                status TEXT,
                uptime REAL,
                request_rate REAL,
                response_time REAL,
                success_rate REAL,
                training_jobs_active INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_service_metrics_timestamp
            ON service_metrics(timestamp)
        """)

        # Cost entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT UNIQUE NOT NULL,
                timestamp REAL NOT NULL,
                resource_id TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                region TEXT,
                tags TEXT,
                description TEXT,
                billing_period TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_entries_timestamp
            ON cost_entries(timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_entries_category
            ON cost_entries(category, timestamp)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_entries_resource
            ON cost_entries(resource_id, timestamp)
        """)

        # Alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                cluster_id TEXT,
                resource_id TEXT,
                value REAL,
                description TEXT,
                acknowledged INTEGER DEFAULT 0,
                resolved INTEGER DEFAULT 0,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_timestamp
            ON alerts(timestamp)
        """)

        conn.commit()

    def store_system_metric(self, metric: Dict[str, Any]):
        """Buffer system metric for batch insertion"""
        with self.buffer_lock:
            self.write_buffer['system_metrics'].append(metric)
            if len(self.write_buffer['system_metrics']) >= self.config.batch_size:
                self._flush_system_metrics()

    def store_service_metric(self, metric: Dict[str, Any]):
        """Buffer service metric for batch insertion"""
        with self.buffer_lock:
            self.write_buffer['service_metrics'].append(metric)
            if len(self.write_buffer['service_metrics']) >= self.config.batch_size:
                self._flush_service_metrics()

    def store_cost_entry(self, entry: Dict[str, Any]):
        """Buffer cost entry for batch insertion"""
        with self.buffer_lock:
            self.write_buffer['cost_entries'].append(entry)
            if len(self.write_buffer['cost_entries']) >= self.config.batch_size:
                self._flush_cost_entries()

    def store_alert(self, alert: Dict[str, Any]):
        """Buffer alert for batch insertion"""
        with self.buffer_lock:
            self.write_buffer['alerts'].append(alert)
            if len(self.write_buffer['alerts']) >= self.config.batch_size:
                self._flush_alerts()

    def flush_buffer(self):
        """Flush all buffered data"""
        with self.buffer_lock:
            self._flush_system_metrics()
            self._flush_service_metrics()
            self._flush_cost_entries()
            self._flush_alerts()

    def _flush_system_metrics(self):
        """Flush system metrics buffer"""
        if not self.write_buffer['system_metrics']:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        for metric in self.write_buffer['system_metrics']:
            cursor.execute("""
                INSERT INTO system_metrics (
                    timestamp, cluster_id, node_id, cpu_usage, memory_usage,
                    disk_usage, gpu_usage, network_io, throughput, latency_p50,
                    latency_p95, latency_p99, error_rate, cost_per_hour,
                    health_status, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.get('timestamp'),
                metric.get('cluster_id', 'default'),
                metric.get('node_id', 'default'),
                metric.get('cpu_usage'),
                metric.get('memory_usage'),
                metric.get('disk_usage'),
                metric.get('gpu_usage'),
                json.dumps(metric.get('network_io')) if metric.get('network_io') else None,
                metric.get('throughput'),
                metric.get('latency_p50'),
                metric.get('latency_p95'),
                metric.get('latency_p99'),
                metric.get('error_rate'),
                metric.get('cost_per_hour'),
                metric.get('health_status'),
                json.dumps({k: v for k, v in metric.items() if k not in [
                    'timestamp', 'cluster_id', 'node_id', 'cpu_usage', 'memory_usage',
                    'disk_usage', 'gpu_usage', 'network_io', 'throughput', 'latency_p50',
                    'latency_p95', 'latency_p99', 'error_rate', 'cost_per_hour', 'health_status'
                ]})
            ))

        conn.commit()
        self.write_buffer['system_metrics'].clear()

    def _flush_service_metrics(self):
        """Flush service metrics buffer"""
        if not self.write_buffer['service_metrics']:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        for metric in self.write_buffer['service_metrics']:
            cursor.execute("""
                INSERT INTO service_metrics (
                    timestamp, service_name, status, uptime, request_rate,
                    response_time, success_rate, training_jobs_active, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.get('timestamp'),
                metric.get('service_name'),
                metric.get('status'),
                metric.get('uptime'),
                metric.get('request_rate'),
                metric.get('response_time'),
                metric.get('success_rate'),
                metric.get('training_jobs_active'),
                json.dumps({k: v for k, v in metric.items() if k not in [
                    'timestamp', 'service_name', 'status', 'uptime', 'request_rate',
                    'response_time', 'success_rate', 'training_jobs_active'
                ]})
            ))

        conn.commit()
        self.write_buffer['service_metrics'].clear()

    def _flush_cost_entries(self):
        """Flush cost entries buffer"""
        if not self.write_buffer['cost_entries']:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        for entry in self.write_buffer['cost_entries']:
            try:
                cursor.execute("""
                    INSERT INTO cost_entries (
                        entry_id, timestamp, resource_id, category, amount,
                        currency, region, tags, description, billing_period
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.get('entry_id'),
                    entry.get('timestamp'),
                    entry.get('resource_id'),
                    entry.get('category'),
                    entry.get('amount'),
                    entry.get('currency', 'USD'),
                    entry.get('region'),
                    json.dumps(entry.get('tags', {})),
                    entry.get('description', ''),
                    entry.get('billing_period', '')
                ))
            except sqlite3.IntegrityError:
                # Skip duplicate entries
                pass

        conn.commit()
        self.write_buffer['cost_entries'].clear()

    def _flush_alerts(self):
        """Flush alerts buffer"""
        if not self.write_buffer['alerts']:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        for alert in self.write_buffer['alerts']:
            cursor.execute("""
                INSERT INTO alerts (
                    timestamp, alert_type, severity, cluster_id, resource_id,
                    value, description, acknowledged, resolved, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.get('timestamp'),
                alert.get('type'),
                alert.get('severity'),
                alert.get('cluster_id'),
                alert.get('resource_id'),
                alert.get('value'),
                alert.get('description'),
                1 if alert.get('acknowledged') else 0,
                1 if alert.get('resolved') else 0,
                json.dumps({k: v for k, v in alert.items() if k not in [
                    'timestamp', 'type', 'severity', 'cluster_id', 'resource_id',
                    'value', 'description', 'acknowledged', 'resolved'
                ]})
            ))

        conn.commit()
        self.write_buffer['alerts'].clear()

    def query_system_metrics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        cluster_id: Optional[str] = None,
        node_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM system_metrics WHERE 1=1"
        params = []

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        if cluster_id:
            query += " AND cluster_id = ?"
            params.append(cluster_id)
        if node_id:
            query += " AND node_id = ?"
            params.append(node_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def query_cost_entries(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        category: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM cost_entries WHERE 1=1"
        params = []

        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time)
        if category:
            query += " AND category = ?"
            params.append(category)
        if resource_id:
            query += " AND resource_id = ?"
            params.append(resource_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def cleanup_old_data(self):
        """Remove data older than retention period"""
        cutoff_time = time.time() - (self.config.retention_days * 24 * 3600)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM system_metrics WHERE timestamp < ?", (cutoff_time,))
        cursor.execute("DELETE FROM service_metrics WHERE timestamp < ?", (cutoff_time,))
        cursor.execute("DELETE FROM cost_entries WHERE timestamp < ?", (cutoff_time,))
        cursor.execute("DELETE FROM alerts WHERE timestamp < ?", (cutoff_time,))

        conn.commit()

    def close(self):
        """Close database connection"""
        self.flush_buffer()
        if self.conn:
            self.conn.close()
            self.conn = None


class PostgreSQLBackend(BasePersistenceBackend):
    """PostgreSQL storage backend"""

    def __init__(self, config: PersistenceConfig):
        super().__init__(config)
        try:
            import psycopg2
            import psycopg2.extras
            self.psycopg2 = psycopg2
            self.conn = None
            self.initialize_schema()
        except ImportError:
            raise ImportError(
                "psycopg2 is required for PostgreSQL backend. "
                "Install with: pip install psycopg2-binary"
            )

    def _get_connection(self):
        """Get or create database connection"""
        if self.conn is None or self.conn.closed:
            self.conn = self.psycopg2.connect(self.config.connection_string)
        return self.conn

    def initialize_schema(self):
        """Initialize PostgreSQL schema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # System metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id SERIAL PRIMARY KEY,
                timestamp DOUBLE PRECISION NOT NULL,
                cluster_id TEXT NOT NULL,
                node_id TEXT NOT NULL,
                cpu_usage REAL,
                memory_usage REAL,
                disk_usage REAL,
                gpu_usage REAL,
                network_io JSONB,
                throughput REAL,
                latency_p50 REAL,
                latency_p95 REAL,
                latency_p99 REAL,
                error_rate REAL,
                cost_per_hour REAL,
                health_status TEXT,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp
            ON system_metrics(timestamp DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_system_metrics_cluster
            ON system_metrics(cluster_id, timestamp DESC)
        """)

        # Cost entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_entries (
                id SERIAL PRIMARY KEY,
                entry_id TEXT UNIQUE NOT NULL,
                timestamp DOUBLE PRECISION NOT NULL,
                resource_id TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT DEFAULT 'USD',
                region TEXT,
                tags JSONB,
                description TEXT,
                billing_period TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_entries_timestamp
            ON cost_entries(timestamp DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_entries_category
            ON cost_entries(category, timestamp DESC)
        """)

        conn.commit()

    def store_system_metric(self, metric: Dict[str, Any]):
        """Buffer system metric"""
        with self.buffer_lock:
            self.write_buffer['system_metrics'].append(metric)
            if len(self.write_buffer['system_metrics']) >= self.config.batch_size:
                self._flush_system_metrics()

    def store_service_metric(self, metric: Dict[str, Any]):
        """Buffer service metric"""
        with self.buffer_lock:
            self.write_buffer['service_metrics'].append(metric)

    def store_cost_entry(self, entry: Dict[str, Any]):
        """Buffer cost entry"""
        with self.buffer_lock:
            self.write_buffer['cost_entries'].append(entry)
            if len(self.write_buffer['cost_entries']) >= self.config.batch_size:
                self._flush_cost_entries()

    def store_alert(self, alert: Dict[str, Any]):
        """Buffer alert"""
        with self.buffer_lock:
            self.write_buffer['alerts'].append(alert)

    def flush_buffer(self):
        """Flush all buffers"""
        with self.buffer_lock:
            self._flush_system_metrics()
            self._flush_cost_entries()

    def _flush_system_metrics(self):
        """Flush system metrics to PostgreSQL"""
        if not self.write_buffer['system_metrics']:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        self.psycopg2.extras.execute_batch(cursor, """
            INSERT INTO system_metrics (
                timestamp, cluster_id, node_id, cpu_usage, memory_usage,
                disk_usage, gpu_usage, throughput, latency_p95, error_rate,
                cost_per_hour, health_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [
            (
                m.get('timestamp'),
                m.get('cluster_id', 'default'),
                m.get('node_id', 'default'),
                m.get('cpu_usage'),
                m.get('memory_usage'),
                m.get('disk_usage'),
                m.get('gpu_usage'),
                m.get('throughput'),
                m.get('latency_p95'),
                m.get('error_rate'),
                m.get('cost_per_hour'),
                m.get('health_status')
            )
            for m in self.write_buffer['system_metrics']
        ])

        conn.commit()
        self.write_buffer['system_metrics'].clear()

    def _flush_cost_entries(self):
        """Flush cost entries to PostgreSQL"""
        if not self.write_buffer['cost_entries']:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        for entry in self.write_buffer['cost_entries']:
            try:
                cursor.execute("""
                    INSERT INTO cost_entries (
                        entry_id, timestamp, resource_id, category, amount,
                        currency, region, tags
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (entry_id) DO NOTHING
                """, (
                    entry.get('entry_id'),
                    entry.get('timestamp'),
                    entry.get('resource_id'),
                    entry.get('category'),
                    entry.get('amount'),
                    entry.get('currency', 'USD'),
                    entry.get('region'),
                    self.psycopg2.extras.Json(entry.get('tags', {}))
                ))
            except Exception:
                pass

        conn.commit()
        self.write_buffer['cost_entries'].clear()

    def query_system_metrics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        cluster_id: Optional[str] = None,
        node_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=self.psycopg2.extras.RealDictCursor)

        query = "SELECT * FROM system_metrics WHERE 1=1"
        params = []

        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)
        if cluster_id:
            query += " AND cluster_id = %s"
            params.append(cluster_id)
        if node_id:
            query += " AND node_id = %s"
            params.append(node_id)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def query_cost_entries(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        category: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=self.psycopg2.extras.RealDictCursor)

        query = "SELECT * FROM cost_entries WHERE 1=1"
        params = []

        if start_time:
            query += " AND timestamp >= %s"
            params.append(start_time)
        if end_time:
            query += " AND timestamp <= %s"
            params.append(end_time)
        if category:
            query += " AND category = %s"
            params.append(category)
        if resource_id:
            query += " AND resource_id = %s"
            params.append(resource_id)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def cleanup_old_data(self):
        """Remove data older than retention period"""
        cutoff_time = time.time() - (self.config.retention_days * 24 * 3600)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM system_metrics WHERE timestamp < %s", (cutoff_time,))
        cursor.execute("DELETE FROM cost_entries WHERE timestamp < %s", (cutoff_time,))

        conn.commit()

    def close(self):
        """Close database connection"""
        self.flush_buffer()
        if self.conn and not self.conn.closed:
            self.conn.close()


class TimescaleDBBackend(PostgreSQLBackend):
    """TimescaleDB backend (optimized for time-series)"""

    def initialize_schema(self):
        """Initialize TimescaleDB schema with hypertables"""
        super().initialize_schema()

        conn = self._get_connection()
        cursor = conn.cursor()

        # Convert to hypertables for time-series optimization
        try:
            cursor.execute("""
                SELECT create_hypertable('system_metrics', 'timestamp',
                    if_not_exists => TRUE,
                    migrate_data => TRUE
                )
            """)

            cursor.execute("""
                SELECT create_hypertable('cost_entries', 'timestamp',
                    if_not_exists => TRUE,
                    migrate_data => TRUE
                )
            """)

            # Add compression policy (compress data older than 7 days)
            cursor.execute("""
                SELECT add_compression_policy('system_metrics',
                    INTERVAL '7 days',
                    if_not_exists => TRUE
                )
            """)

            cursor.execute("""
                SELECT add_compression_policy('cost_entries',
                    INTERVAL '7 days',
                    if_not_exists => TRUE
                )
            """)

            conn.commit()
        except Exception as e:
            # TimescaleDB extension might not be installed
            conn.rollback()


def create_persistence_backend(config: PersistenceConfig) -> BasePersistenceBackend:
    """Factory function to create appropriate persistence backend"""
    if config.backend == StorageBackend.IN_MEMORY:
        return InMemoryBackend(config)
    elif config.backend == StorageBackend.SQLITE:
        return SQLiteBackend(config)
    elif config.backend == StorageBackend.POSTGRESQL:
        return PostgreSQLBackend(config)
    elif config.backend == StorageBackend.TIMESCALEDB:
        return TimescaleDBBackend(config)
    else:
        raise ValueError(f"Unsupported storage backend: {config.backend}")
