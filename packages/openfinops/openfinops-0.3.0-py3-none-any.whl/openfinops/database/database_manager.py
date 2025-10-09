"""
Database Manager for OpenFinOps
============================

Universal database abstraction layer supporting multiple RDBMS:
- SQLite (default, embedded)
- PostgreSQL
- MySQL/MariaDB
- Oracle Database
- Microsoft SQL Server
- Any SQLAlchemy-compatible database

Features:
- Automatic schema creation and migration
- Connection pooling and failover
- Performance optimization per database type
- Transaction management
- Query optimization
- Database-specific data type handling
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



import os
import time
import json
import logging
from typing import Dict, List, Any, Optional, Union
from contextlib import contextmanager
from urllib.parse import urlparse

from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.dialects import postgresql, mysql, oracle, mssql, sqlite


class DatabaseConfig:
    """Database configuration for different RDBMS types"""

    # Supported database types
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    ORACLE = "oracle"
    MSSQL = "mssql"

    @classmethod
    def get_connection_string(cls, config: Dict[str, Any]) -> str:
        """Generate connection string based on database type and configuration"""
        db_type = config.get("type", cls.SQLITE).lower()

        if db_type == cls.SQLITE:
            db_path = config.get("path", "openfinops.db")
            return f"sqlite:///{db_path}"

        elif db_type in [cls.POSTGRESQL, "postgres"]:
            host = config.get("host", "localhost")
            port = config.get("port", 5432)
            database = config.get("database", "openfinops")
            username = config.get("username", "openfinops")
            password = config.get("password", "")

            if password:
                return f"postgresql://{username}:{password}@{host}:{port}/{database}"
            else:
                return f"postgresql://{username}@{host}:{port}/{database}"

        elif db_type in [cls.MYSQL, cls.MARIADB]:
            host = config.get("host", "localhost")
            port = config.get("port", 3306)
            database = config.get("database", "openfinops")
            username = config.get("username", "openfinops")
            password = config.get("password", "")
            charset = config.get("charset", "utf8mb4")

            if password:
                return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset={charset}"
            else:
                return f"mysql+pymysql://{username}@{host}:{port}/{database}?charset={charset}"

        elif db_type == cls.ORACLE:
            host = config.get("host", "localhost")
            port = config.get("port", 1521)
            service_name = config.get("service_name", "XE")
            username = config.get("username", "openfinops")
            password = config.get("password", "")

            if password:
                return f"oracle+cx_oracle://{username}:{password}@{host}:{port}/?service_name={service_name}"
            else:
                return f"oracle+cx_oracle://{username}@{host}:{port}/?service_name={service_name}"

        elif db_type == cls.MSSQL:
            host = config.get("host", "localhost")
            port = config.get("port", 1433)
            database = config.get("database", "openfinops")
            username = config.get("username", "openfinops")
            password = config.get("password", "")
            driver = config.get("driver", "ODBC Driver 17 for SQL Server")

            if password:
                return f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver={driver}"
            else:
                return f"mssql+pyodbc://{username}@{host}:{port}/{database}?driver={driver}"

        else:
            # Custom connection string
            return config.get("connection_string", "sqlite:///openfinops.db")

    @classmethod
    def get_engine_options(cls, db_type: str) -> Dict[str, Any]:
        """Get database-specific engine options for optimization"""
        db_type = db_type.lower()

        base_options = {
            "echo": False,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # 1 hour
        }

        if db_type == cls.SQLITE:
            return {
                **base_options,
                "poolclass": NullPool,  # SQLite doesn't support connection pooling
                "connect_args": {
                    "check_same_thread": False,
                    "timeout": 30
                }
            }

        elif db_type in [cls.POSTGRESQL, "postgres"]:
            return {
                **base_options,
                "poolclass": QueuePool,
                "pool_size": 10,
                "max_overflow": 20,
                "connect_args": {
                    "connect_timeout": 30,
                    "application_name": "OpenFinOps"
                }
            }

        elif db_type in [cls.MYSQL, cls.MARIADB]:
            return {
                **base_options,
                "poolclass": QueuePool,
                "pool_size": 10,
                "max_overflow": 20,
                "connect_args": {
                    "connect_timeout": 30,
                    "charset": "utf8mb4"
                }
            }

        elif db_type == cls.ORACLE:
            return {
                **base_options,
                "poolclass": QueuePool,
                "pool_size": 5,
                "max_overflow": 10,
                "connect_args": {
                    "threaded": True
                }
            }

        elif db_type == cls.MSSQL:
            return {
                **base_options,
                "poolclass": QueuePool,
                "pool_size": 10,
                "max_overflow": 20,
                "connect_args": {
                    "timeout": 30
                }
            }

        return base_options


# SQLAlchemy Base
Base = declarative_base()


class TelemetryData(Base):
    """Telemetry data table"""
    __tablename__ = "telemetry_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    metrics = Column(Text)  # JSON string
    events = Column(Text)   # JSON string
    agent_health = Column(Text)  # JSON string
    created_at = Column(DateTime, default=time.time)


class AgentRegistration(Base):
    """Agent registration table"""
    __tablename__ = "agent_registrations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(255), unique=True, nullable=False, index=True)
    agent_type = Column(String(100), nullable=False)
    hostname = Column(String(255))
    cloud_provider = Column(String(100))
    region = Column(String(100))
    capabilities = Column(Text)  # JSON string
    status = Column(String(50), default="active")
    last_heartbeat = Column(DateTime)
    registration_time = Column(DateTime, nullable=False)
    metadata = Column(Text)  # JSON string


class FinancialMetrics(Base):
    """Financial metrics table"""
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    currency = Column(String(10))
    source = Column(String(100))
    timestamp = Column(DateTime, nullable=False, index=True)
    metadata = Column(Text)  # JSON string


class InfrastructureMetrics(Base):
    """Infrastructure metrics table"""
    __tablename__ = "infrastructure_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=False)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    cloud_provider = Column(String(100))
    region = Column(String(100))
    timestamp = Column(DateTime, nullable=False, index=True)
    metadata = Column(Text)  # JSON string


class CostAnalytics(Base):
    """Cost analytics table"""
    __tablename__ = "cost_analytics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cost_category = Column(String(100), nullable=False)
    cost_amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    cloud_provider = Column(String(100))
    service_name = Column(String(255))
    resource_id = Column(String(255))
    billing_period = Column(String(20))  # YYYY-MM format
    timestamp = Column(DateTime, nullable=False, index=True)
    metadata = Column(Text)  # JSON string


class UserSessions(Base):
    """User sessions table"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), nullable=False)
    role = Column(String(100), nullable=False)
    login_time = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, nullable=False)
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    status = Column(String(20), default="active")


class DatabaseManager:
    """Universal database manager for multiple RDBMS support"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_type = config.get("type", "sqlite").lower()
        self.connection_string = DatabaseConfig.get_connection_string(config)
        self.engine_options = DatabaseConfig.get_engine_options(self.db_type)

        self.engine = None
        self.SessionLocal = None
        self.metadata = MetaData()

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Initialize database
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            self.logger.info(f"Initializing {self.db_type.upper()} database connection")

            # Create engine with database-specific options
            self.engine = create_engine(
                self.connection_string,
                **self.engine_options
            )

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Test connection
            self._test_connection()

            # Create all tables
            self._create_tables()

            self.logger.info("Database initialized successfully")

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    def _test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                # Database-specific connection test
                if self.db_type == "sqlite":
                    conn.execute(text("SELECT 1"))
                elif self.db_type in ["postgresql", "postgres"]:
                    conn.execute(text("SELECT version()"))
                elif self.db_type in ["mysql", "mariadb"]:
                    conn.execute(text("SELECT @@version"))
                elif self.db_type == "oracle":
                    conn.execute(text("SELECT * FROM dual"))
                elif self.db_type == "mssql":
                    conn.execute(text("SELECT @@version"))
                else:
                    conn.execute(text("SELECT 1"))

                self.logger.info("Database connection test successful")

        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            raise

    def _create_tables(self):
        """Create all database tables"""
        try:
            # Create tables with database-specific optimizations
            Base.metadata.create_all(bind=self.engine)

            # Create database-specific indexes
            self._create_indexes()

            self.logger.info("Database tables created successfully")

        except Exception as e:
            self.logger.error(f"Table creation failed: {e}")
            raise

    def _create_indexes(self):
        """Create database-specific indexes for performance"""
        try:
            with self.engine.connect() as conn:
                # Create performance indexes based on database type
                indexes = self._get_performance_indexes()

                for index_sql in indexes:
                    try:
                        conn.execute(text(index_sql))
                    except Exception as e:
                        # Index might already exist, log warning but continue
                        self.logger.warning(f"Index creation warning: {e}")

                conn.commit()

        except Exception as e:
            self.logger.error(f"Index creation failed: {e}")

    def _get_performance_indexes(self) -> List[str]:
        """Get database-specific performance indexes"""
        indexes = []

        if self.db_type == "postgresql":
            indexes.extend([
                "CREATE INDEX IF NOT EXISTS idx_telemetry_agent_timestamp ON telemetry_data(agent_id, timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_financial_metrics_timestamp ON financial_metrics(timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_infrastructure_metrics_composite ON infrastructure_metrics(cloud_provider, resource_type, timestamp DESC)",
                "CREATE INDEX IF NOT EXISTS idx_cost_analytics_period ON cost_analytics(billing_period, cloud_provider)"
            ])

        elif self.db_type in ["mysql", "mariadb"]:
            indexes.extend([
                "CREATE INDEX idx_telemetry_agent_timestamp ON telemetry_data(agent_id, timestamp DESC)",
                "CREATE INDEX idx_financial_metrics_timestamp ON financial_metrics(timestamp DESC)",
                "CREATE INDEX idx_infrastructure_metrics_composite ON infrastructure_metrics(cloud_provider, resource_type, timestamp DESC)",
                "CREATE INDEX idx_cost_analytics_period ON cost_analytics(billing_period, cloud_provider)"
            ])

        elif self.db_type == "oracle":
            indexes.extend([
                "CREATE INDEX idx_telemetry_agent_timestamp ON telemetry_data(agent_id, timestamp DESC)",
                "CREATE INDEX idx_financial_metrics_timestamp ON financial_metrics(timestamp DESC)",
                "CREATE INDEX idx_infrastructure_metrics_composite ON infrastructure_metrics(cloud_provider, resource_type, timestamp DESC)",
                "CREATE INDEX idx_cost_analytics_period ON cost_analytics(billing_period, cloud_provider)"
            ])

        elif self.db_type == "mssql":
            indexes.extend([
                "CREATE NONCLUSTERED INDEX idx_telemetry_agent_timestamp ON telemetry_data(agent_id, timestamp DESC)",
                "CREATE NONCLUSTERED INDEX idx_financial_metrics_timestamp ON financial_metrics(timestamp DESC)",
                "CREATE NONCLUSTERED INDEX idx_infrastructure_metrics_composite ON infrastructure_metrics(cloud_provider, resource_type, timestamp DESC)",
                "CREATE NONCLUSTERED INDEX idx_cost_analytics_period ON cost_analytics(billing_period, cloud_provider)"
            ])

        return indexes

    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def store_telemetry_data(self, telemetry_data: Dict[str, Any]) -> bool:
        """Store telemetry data in database"""
        try:
            with self.get_session() as session:
                record = TelemetryData(
                    agent_id=telemetry_data["agent_id"],
                    timestamp=telemetry_data["timestamp"],
                    metrics=json.dumps(telemetry_data.get("metrics", {})),
                    events=json.dumps(telemetry_data.get("events", [])),
                    agent_health=json.dumps(telemetry_data.get("agent_health", {}))
                )
                session.add(record)
                return True

        except Exception as e:
            self.logger.error(f"Error storing telemetry data: {e}")
            return False

    def register_agent(self, agent_data: Dict[str, Any]) -> bool:
        """Register or update agent in database"""
        try:
            with self.get_session() as session:
                # Check if agent already exists
                existing = session.query(AgentRegistration).filter_by(
                    agent_id=agent_data["agent_id"]
                ).first()

                if existing:
                    # Update existing agent
                    existing.last_heartbeat = time.time()
                    existing.status = "active"
                    existing.metadata = json.dumps(agent_data)
                else:
                    # Create new agent registration
                    record = AgentRegistration(
                        agent_id=agent_data["agent_id"],
                        agent_type=agent_data.get("agent_type", "unknown"),
                        hostname=agent_data.get("hostname"),
                        cloud_provider=agent_data.get("cloud_provider"),
                        region=agent_data.get("region"),
                        capabilities=json.dumps(agent_data.get("capabilities", [])),
                        registration_time=agent_data.get("registration_time", time.time()),
                        last_heartbeat=time.time(),
                        metadata=json.dumps(agent_data)
                    )
                    session.add(record)

                return True

        except Exception as e:
            self.logger.error(f"Error registering agent: {e}")
            return False

    def get_dashboard_data(self, dashboard_type: str, time_range: int = 3600) -> Dict[str, Any]:
        """Get dashboard data for specific role"""
        try:
            current_time = time.time()
            start_time = current_time - time_range

            with self.get_session() as session:
                # Get recent telemetry data
                telemetry_query = session.query(TelemetryData).filter(
                    TelemetryData.timestamp >= start_time
                ).order_by(TelemetryData.timestamp.desc()).limit(100)

                telemetry_data = []
                for record in telemetry_query:
                    telemetry_data.append({
                        "agent_id": record.agent_id,
                        "timestamp": record.timestamp,
                        "metrics": json.loads(record.metrics) if record.metrics else {},
                        "events": json.loads(record.events) if record.events else [],
                        "agent_health": json.loads(record.agent_health) if record.agent_health else {}
                    })

                # Get active agents
                agents_query = session.query(AgentRegistration).filter(
                    AgentRegistration.status == "active"
                )

                agents = []
                for agent in agents_query:
                    agents.append({
                        "agent_id": agent.agent_id,
                        "agent_type": agent.agent_type,
                        "hostname": agent.hostname,
                        "cloud_provider": agent.cloud_provider,
                        "region": agent.region,
                        "capabilities": json.loads(agent.capabilities) if agent.capabilities else [],
                        "last_heartbeat": agent.last_heartbeat
                    })

                return {
                    "telemetry_data": telemetry_data,
                    "agents": agents,
                    "summary": {
                        "total_agents": len(agents),
                        "active_agents": len([a for a in agents if (current_time - (a["last_heartbeat"] or 0)) < 600]),
                        "data_points": len(telemetry_data)
                    }
                }

        except Exception as e:
            self.logger.error(f"Error getting dashboard data: {e}")
            return {"error": str(e)}

    def cleanup_old_data(self, retention_days: int = 30):
        """Clean up old data based on retention policy"""
        try:
            cutoff_time = time.time() - (retention_days * 24 * 3600)

            with self.get_session() as session:
                # Clean up old telemetry data
                deleted_telemetry = session.query(TelemetryData).filter(
                    TelemetryData.timestamp < cutoff_time
                ).delete()

                # Clean up old financial metrics
                deleted_financial = session.query(FinancialMetrics).filter(
                    FinancialMetrics.timestamp < cutoff_time
                ).delete()

                # Clean up old infrastructure metrics
                deleted_infrastructure = session.query(InfrastructureMetrics).filter(
                    InfrastructureMetrics.timestamp < cutoff_time
                ).delete()

                self.logger.info(
                    f"Cleaned up old data: "
                    f"telemetry={deleted_telemetry}, "
                    f"financial={deleted_financial}, "
                    f"infrastructure={deleted_infrastructure}"
                )

        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")

    def get_health_status(self) -> Dict[str, Any]:
        """Get database health status"""
        try:
            with self.engine.connect() as conn:
                # Test connection
                conn.execute(text("SELECT 1"))

                # Get basic statistics
                with self.get_session() as session:
                    agent_count = session.query(AgentRegistration).count()
                    telemetry_count = session.query(TelemetryData).count()

                    # Get recent activity
                    recent_telemetry = session.query(TelemetryData).filter(
                        TelemetryData.timestamp > (time.time() - 3600)
                    ).count()

                return {
                    "status": "healthy",
                    "database_type": self.db_type,
                    "connection_status": "connected",
                    "statistics": {
                        "total_agents": agent_count,
                        "total_telemetry_records": telemetry_count,
                        "recent_telemetry_count": recent_telemetry
                    },
                    "timestamp": time.time()
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }

    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database connections closed")


def create_database_manager(config: Dict[str, Any]) -> DatabaseManager:
    """Factory function to create database manager"""
    return DatabaseManager(config)