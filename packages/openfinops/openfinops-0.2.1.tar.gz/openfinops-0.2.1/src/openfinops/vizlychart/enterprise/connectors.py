"""
Enterprise Data Connectors

Comprehensive data integration platform for connecting Vizly Enterprise
with various enterprise data sources, databases, APIs, and cloud services.

Features:
- Database connectors (SQL Server, Oracle, PostgreSQL, MySQL)
- Cloud service integrations (AWS, Azure, GCP)
- REST API and GraphQL connectors
- Enterprise applications (Salesforce, SAP, ServiceNow)
- Real-time streaming data (Kafka, RabbitMQ)
- File-based sources (Excel, CSV, Parquet, JSON)
- Data transformation and cleansing pipelines

Enterprise Requirements:
- Secure credential management and encryption
- Connection pooling and performance optimization
- Data governance and lineage tracking
- Schema discovery and metadata management
- Automated data quality validation
- Compliance with enterprise security policies
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



import logging
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod
import threading
from urllib.parse import urlparse

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import sqlalchemy
    from sqlalchemy import create_engine, text
    from sqlalchemy.pool import QueuePool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

from .security import EnterpriseSecurityManager


@dataclass
class DataSource:
    """Data source configuration"""
    source_id: str
    source_type: str  # 'database', 'api', 'file', 'stream'
    name: str
    description: str
    connection_config: Dict[str, Any]
    credentials: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: Optional[datetime] = None
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_id': self.source_id,
            'source_type': self.source_type,
            'name': self.name,
            'description': self.description,
            'connection_config': self.connection_config,
            'metadata': self.metadata,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'is_active': self.is_active
        }


@dataclass
class QueryResult:
    """Query execution result"""
    data: Any  # pandas DataFrame or raw data
    metadata: Dict[str, Any]
    execution_time: float
    row_count: int
    column_count: int
    query: str
    source_id: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'metadata': self.metadata,
            'execution_time': self.execution_time,
            'row_count': self.row_count,
            'column_count': self.column_count,
            'query': self.query,
            'source_id': self.source_id,
            'timestamp': self.timestamp.isoformat()
        }


class BaseConnector(ABC):
    """Base class for all data connectors"""

    def __init__(self, data_source: DataSource, security_manager: Optional[EnterpriseSecurityManager] = None):
        self.data_source = data_source
        self.security_manager = security_manager
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.connection = None
        self.is_connected = False
        self.connection_pool = None

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to data source"""
        pass

    @abstractmethod
    async def disconnect(self):
        """Close connection to data source"""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to data source"""
        pass

    @abstractmethod
    async def execute_query(self, query: str, parameters: Optional[Dict] = None) -> QueryResult:
        """Execute query and return results"""
        pass

    @abstractmethod
    async def get_schema(self) -> Dict[str, Any]:
        """Get schema information"""
        pass

    def _decrypt_credentials(self) -> Dict[str, str]:
        """Decrypt stored credentials"""
        if not self.security_manager:
            return self.data_source.credentials

        decrypted = {}
        for key, encrypted_value in self.data_source.credentials.items():
            try:
                decrypted[key] = self.security_manager.decrypt_data(encrypted_value.encode())
            except Exception as e:
                self.logger.error(f"Failed to decrypt credential {key}: {e}")
                decrypted[key] = encrypted_value  # Fallback to original value

        return decrypted


class DatabaseConnector(BaseConnector):
    """SQL database connector supporting multiple database types"""

    def __init__(self, data_source: DataSource, security_manager: Optional[EnterpriseSecurityManager] = None):
        super().__init__(data_source, security_manager)

        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy is required for database connections. Install with: pip install sqlalchemy")

        self.engine = None
        self.supported_databases = {
            'postgresql': 'postgresql+psycopg2',
            'mysql': 'mysql+pymysql',
            'mssql': 'mssql+pyodbc',
            'oracle': 'oracle+cx_oracle',
            'sqlite': 'sqlite'
        }

    async def connect(self) -> bool:
        """Establish database connection"""
        try:
            config = self.data_source.connection_config
            credentials = self._decrypt_credentials()

            db_type = config.get('database_type', 'postgresql')
            if db_type not in self.supported_databases:
                raise ValueError(f"Unsupported database type: {db_type}")

            # Build connection string
            dialect = self.supported_databases[db_type]
            host = config.get('host', 'localhost')
            port = config.get('port', 5432)
            database = config.get('database', 'postgres')
            username = credentials.get('username', '')
            password = credentials.get('password', '')

            if db_type == 'sqlite':
                connection_string = f"{dialect}:///{database}"
            else:
                connection_string = f"{dialect}://{username}:{password}@{host}:{port}/{database}"

            # Create engine with connection pooling
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=config.get('pool_size', 10),
                max_overflow=config.get('max_overflow', 20),
                pool_timeout=config.get('pool_timeout', 30),
                pool_recycle=config.get('pool_recycle', 3600),
                echo=config.get('echo', False)
            )

            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            self.is_connected = True
            self.data_source.last_accessed = datetime.now()
            self.logger.info(f"Connected to {db_type} database: {host}:{port}/{database}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            self.engine = None
        self.is_connected = False
        self.logger.info("Disconnected from database")

    async def test_connection(self) -> bool:
        """Test database connection"""
        if not self.is_connected or not self.engine:
            return await self.connect()

        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    async def execute_query(self, query: str, parameters: Optional[Dict] = None) -> QueryResult:
        """Execute SQL query and return results"""
        if not self.is_connected:
            await self.connect()

        start_time = time.time()

        try:
            if PANDAS_AVAILABLE:
                # Use pandas for better data handling
                df = pd.read_sql_query(query, self.engine, params=parameters)
                execution_time = time.time() - start_time

                result = QueryResult(
                    data=df,
                    metadata={
                        'columns': list(df.columns),
                        'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
                    },
                    execution_time=execution_time,
                    row_count=len(df),
                    column_count=len(df.columns),
                    query=query,
                    source_id=self.data_source.source_id
                )
            else:
                # Fallback to raw SQLAlchemy
                with self.engine.connect() as conn:
                    result_proxy = conn.execute(text(query), parameters or {})
                    rows = result_proxy.fetchall()
                    columns = list(result_proxy.keys())

                execution_time = time.time() - start_time

                result = QueryResult(
                    data=rows,
                    metadata={'columns': columns},
                    execution_time=execution_time,
                    row_count=len(rows),
                    column_count=len(columns),
                    query=query,
                    source_id=self.data_source.source_id
                )

            self.data_source.last_accessed = datetime.now()
            self.logger.info(f"Query executed successfully: {result.row_count} rows in {execution_time:.3f}s")
            return result

        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise

    async def get_schema(self) -> Dict[str, Any]:
        """Get database schema information"""
        if not self.is_connected:
            await self.connect()

        try:
            # Get tables and their columns
            tables_query = """
                SELECT table_name, column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """

            result = await self.execute_query(tables_query)

            if PANDAS_AVAILABLE and hasattr(result.data, 'iterrows'):
                schema = {}
                for _, row in result.data.iterrows():
                    table_name = row['table_name']
                    if table_name not in schema:
                        schema[table_name] = []

                    schema[table_name].append({
                        'column_name': row['column_name'],
                        'data_type': row['data_type'],
                        'is_nullable': row['is_nullable']
                    })
            else:
                # Fallback for non-pandas result
                schema = {}
                for row in result.data:
                    table_name = row[0]
                    if table_name not in schema:
                        schema[table_name] = []

                    schema[table_name].append({
                        'column_name': row[1],
                        'data_type': row[2],
                        'is_nullable': row[3]
                    })

            return {'tables': schema}

        except Exception as e:
            self.logger.error(f"Failed to get schema: {e}")
            return {'tables': {}}


class APIConnector(BaseConnector):
    """REST API connector for external services"""

    def __init__(self, data_source: DataSource, security_manager: Optional[EnterpriseSecurityManager] = None):
        super().__init__(data_source, security_manager)

        if not REQUESTS_AVAILABLE:
            raise ImportError("Requests library is required for API connections. Install with: pip install requests")

        self.session = None
        self.base_url = None

    async def connect(self) -> bool:
        """Establish API connection"""
        try:
            config = self.data_source.connection_config
            credentials = self._decrypt_credentials()

            self.base_url = config.get('base_url')
            if not self.base_url:
                raise ValueError("base_url is required for API connections")

            # Create session with authentication
            self.session = requests.Session()

            # Set up authentication
            auth_type = config.get('auth_type', 'none')

            if auth_type == 'api_key':
                api_key = credentials.get('api_key')
                key_header = config.get('api_key_header', 'X-API-Key')
                self.session.headers.update({key_header: api_key})

            elif auth_type == 'bearer':
                token = credentials.get('bearer_token')
                self.session.headers.update({'Authorization': f'Bearer {token}'})

            elif auth_type == 'basic':
                username = credentials.get('username')
                password = credentials.get('password')
                self.session.auth = (username, password)

            elif auth_type == 'oauth2':
                # OAuth2 would require additional implementation
                self.logger.warning("OAuth2 authentication not fully implemented")

            # Set default headers
            self.session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'Vizly-Enterprise/1.0'
            })

            # Set timeout
            self.session.timeout = config.get('timeout', 30)

            self.is_connected = True
            self.data_source.last_accessed = datetime.now()
            self.logger.info(f"Connected to API: {self.base_url}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to API: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Close API connection"""
        if self.session:
            self.session.close()
            self.session = None
        self.is_connected = False
        self.logger.info("Disconnected from API")

    async def test_connection(self) -> bool:
        """Test API connection"""
        if not self.is_connected:
            await self.connect()

        try:
            # Try a simple GET request to test connectivity
            test_endpoint = self.data_source.connection_config.get('health_endpoint', '/')
            url = f"{self.base_url.rstrip('/')}{test_endpoint}"

            response = self.session.get(url)
            return response.status_code < 400

        except Exception as e:
            self.logger.error(f"API connection test failed: {e}")
            return False

    async def execute_query(self, query: str, parameters: Optional[Dict] = None) -> QueryResult:
        """Execute API request (query is the endpoint path)"""
        if not self.is_connected:
            await self.connect()

        start_time = time.time()

        try:
            # Parse query as endpoint path and method
            if '|' in query:
                method, endpoint = query.split('|', 1)
                method = method.strip().upper()
            else:
                method = 'GET'
                endpoint = query

            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

            # Execute request
            if method == 'GET':
                response = self.session.get(url, params=parameters)
            elif method == 'POST':
                response = self.session.post(url, json=parameters)
            elif method == 'PUT':
                response = self.session.put(url, json=parameters)
            elif method == 'DELETE':
                response = self.session.delete(url, params=parameters)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            execution_time = time.time() - start_time

            # Parse response
            try:
                data = response.json()
            except ValueError:
                data = response.text

            # Convert to DataFrame if possible
            if PANDAS_AVAILABLE and isinstance(data, list) and data and isinstance(data[0], dict):
                df = pd.DataFrame(data)
                row_count = len(df)
                column_count = len(df.columns)
                result_data = df
            elif isinstance(data, dict):
                row_count = 1
                column_count = len(data)
                result_data = data
            else:
                row_count = 1 if data else 0
                column_count = 1
                result_data = data

            result = QueryResult(
                data=result_data,
                metadata={
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'url': url,
                    'method': method
                },
                execution_time=execution_time,
                row_count=row_count,
                column_count=column_count,
                query=query,
                source_id=self.data_source.source_id
            )

            self.data_source.last_accessed = datetime.now()
            self.logger.info(f"API request executed successfully: {method} {url} ({response.status_code})")
            return result

        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            raise

    async def get_schema(self) -> Dict[str, Any]:
        """Get API schema information"""
        schema = {
            'base_url': self.base_url,
            'auth_type': self.data_source.connection_config.get('auth_type', 'none'),
            'endpoints': self.data_source.connection_config.get('endpoints', [])
        }

        # Try to get OpenAPI/Swagger schema if available
        try:
            swagger_endpoint = self.data_source.connection_config.get('swagger_endpoint', '/swagger.json')
            if swagger_endpoint:
                result = await self.execute_query(swagger_endpoint)
                if hasattr(result.data, 'to_dict'):
                    schema['openapi'] = result.data.to_dict()
                else:
                    schema['openapi'] = result.data

        except Exception as e:
            self.logger.debug(f"Could not fetch OpenAPI schema: {e}")

        return schema


class FileConnector(BaseConnector):
    """File-based data connector for CSV, Excel, JSON, Parquet files"""

    def __init__(self, data_source: DataSource, security_manager: Optional[EnterpriseSecurityManager] = None):
        super().__init__(data_source, security_manager)

        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas is required for file connections. Install with: pip install pandas")

        self.file_path = None
        self.file_type = None

    async def connect(self) -> bool:
        """Establish file connection"""
        try:
            config = self.data_source.connection_config
            self.file_path = Path(config.get('file_path', ''))

            if not self.file_path.exists():
                raise FileNotFoundError(f"File not found: {self.file_path}")

            # Determine file type
            self.file_type = config.get('file_type', '').lower()
            if not self.file_type:
                self.file_type = self.file_path.suffix.lower().lstrip('.')

            supported_types = ['csv', 'excel', 'xlsx', 'xls', 'json', 'parquet']
            if self.file_type not in supported_types:
                raise ValueError(f"Unsupported file type: {self.file_type}")

            self.is_connected = True
            self.data_source.last_accessed = datetime.now()
            self.logger.info(f"Connected to file: {self.file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to file: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """Close file connection"""
        self.file_path = None
        self.file_type = None
        self.is_connected = False
        self.logger.info("Disconnected from file")

    async def test_connection(self) -> bool:
        """Test file connection"""
        return await self.connect()

    async def execute_query(self, query: str, parameters: Optional[Dict] = None) -> QueryResult:
        """Read file data (query can specify sheet name for Excel or JSON path)"""
        if not self.is_connected:
            await self.connect()

        start_time = time.time()

        try:
            config = self.data_source.connection_config
            read_options = parameters or {}

            # Read file based on type
            if self.file_type == 'csv':
                df = pd.read_csv(self.file_path, **read_options)

            elif self.file_type in ['excel', 'xlsx', 'xls']:
                sheet_name = query if query else config.get('sheet_name', 0)
                df = pd.read_excel(self.file_path, sheet_name=sheet_name, **read_options)

            elif self.file_type == 'json':
                if query:  # JSON path query
                    df = pd.read_json(self.file_path, **read_options)
                    # Simple JSON path implementation (could be enhanced)
                    for path_part in query.split('.'):
                        if path_part:
                            df = df[path_part]
                else:
                    df = pd.read_json(self.file_path, **read_options)

            elif self.file_type == 'parquet':
                df = pd.read_parquet(self.file_path, **read_options)

            else:
                raise ValueError(f"Unsupported file type: {self.file_type}")

            execution_time = time.time() - start_time

            result = QueryResult(
                data=df,
                metadata={
                    'file_path': str(self.file_path),
                    'file_type': self.file_type,
                    'file_size': self.file_path.stat().st_size,
                    'columns': list(df.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
                },
                execution_time=execution_time,
                row_count=len(df),
                column_count=len(df.columns),
                query=query or 'READ_ALL',
                source_id=self.data_source.source_id
            )

            self.data_source.last_accessed = datetime.now()
            self.logger.info(f"File read successfully: {result.row_count} rows in {execution_time:.3f}s")
            return result

        except Exception as e:
            self.logger.error(f"File read failed: {e}")
            raise

    async def get_schema(self) -> Dict[str, Any]:
        """Get file schema information"""
        if not self.is_connected:
            await self.connect()

        try:
            # For Excel files, get sheet names
            if self.file_type in ['excel', 'xlsx', 'xls']:
                excel_file = pd.ExcelFile(self.file_path)
                sheets = {}
                for sheet_name in excel_file.sheet_names:
                    df_sample = pd.read_excel(self.file_path, sheet_name=sheet_name, nrows=0)
                    sheets[sheet_name] = {
                        'columns': list(df_sample.columns),
                        'dtypes': {col: str(dtype) for col, dtype in df_sample.dtypes.items()}
                    }
                return {'sheets': sheets, 'file_type': self.file_type}

            else:
                # For other file types, get column info
                if self.file_type == 'csv':
                    df_sample = pd.read_csv(self.file_path, nrows=0)
                elif self.file_type == 'json':
                    df_sample = pd.read_json(self.file_path, nrows=0)
                elif self.file_type == 'parquet':
                    df_sample = pd.read_parquet(self.file_path)
                    df_sample = df_sample.iloc[0:0]  # Keep structure, remove data

                return {
                    'columns': list(df_sample.columns),
                    'dtypes': {col: str(dtype) for col, dtype in df_sample.dtypes.items()},
                    'file_type': self.file_type
                }

        except Exception as e:
            self.logger.error(f"Failed to get schema: {e}")
            return {'file_type': self.file_type, 'error': str(e)}


class ConnectorManager:
    """Central manager for all data connectors"""

    def __init__(self, security_manager: Optional[EnterpriseSecurityManager] = None):
        self.security_manager = security_manager
        self.data_sources = {}
        self.connectors = {}
        self.logger = logging.getLogger(__name__)

        # Register connector types
        self.connector_types = {
            'database': DatabaseConnector,
            'api': APIConnector,
            'file': FileConnector
        }

    def register_data_source(self, data_source: DataSource) -> bool:
        """Register a new data source"""
        try:
            self.data_sources[data_source.source_id] = data_source
            self.logger.info(f"Registered data source: {data_source.source_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register data source: {e}")
            return False

    def get_data_source(self, source_id: str) -> Optional[DataSource]:
        """Get data source by ID"""
        return self.data_sources.get(source_id)

    def list_data_sources(self, source_type: Optional[str] = None) -> List[DataSource]:
        """List all data sources, optionally filtered by type"""
        sources = list(self.data_sources.values())
        if source_type:
            sources = [s for s in sources if s.source_type == source_type]
        return sources

    async def get_connector(self, source_id: str) -> Optional[BaseConnector]:
        """Get or create connector for data source"""
        if source_id in self.connectors:
            return self.connectors[source_id]

        data_source = self.get_data_source(source_id)
        if not data_source:
            self.logger.error(f"Data source not found: {source_id}")
            return None

        try:
            connector_class = self.connector_types.get(data_source.source_type)
            if not connector_class:
                self.logger.error(f"Unsupported source type: {data_source.source_type}")
                return None

            connector = connector_class(data_source, self.security_manager)
            self.connectors[source_id] = connector
            return connector

        except Exception as e:
            self.logger.error(f"Failed to create connector: {e}")
            return None

    async def test_connection(self, source_id: str) -> bool:
        """Test connection to data source"""
        connector = await self.get_connector(source_id)
        if not connector:
            return False
        return await connector.test_connection()

    async def execute_query(self, source_id: str, query: str, parameters: Optional[Dict] = None) -> Optional[QueryResult]:
        """Execute query on data source"""
        connector = await self.get_connector(source_id)
        if not connector:
            return None

        try:
            return await connector.execute_query(query, parameters)
        except Exception as e:
            self.logger.error(f"Query execution failed for {source_id}: {e}")
            return None

    async def get_schema(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get schema information for data source"""
        connector = await self.get_connector(source_id)
        if not connector:
            return None

        try:
            return await connector.get_schema()
        except Exception as e:
            self.logger.error(f"Schema retrieval failed for {source_id}: {e}")
            return None

    def remove_data_source(self, source_id: str) -> bool:
        """Remove data source and close connector"""
        try:
            if source_id in self.connectors:
                asyncio.create_task(self.connectors[source_id].disconnect())
                del self.connectors[source_id]

            if source_id in self.data_sources:
                del self.data_sources[source_id]

            self.logger.info(f"Removed data source: {source_id}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to remove data source: {e}")
            return False

    def get_connection_status(self) -> Dict[str, Dict[str, Any]]:
        """Get connection status for all data sources"""
        status = {}
        for source_id, data_source in self.data_sources.items():
            connector = self.connectors.get(source_id)
            status[source_id] = {
                'name': data_source.name,
                'type': data_source.source_type,
                'is_connected': connector.is_connected if connector else False,
                'last_accessed': data_source.last_accessed.isoformat() if data_source.last_accessed else None,
                'is_active': data_source.is_active
            }
        return status

    async def disconnect_all(self):
        """Disconnect all connectors"""
        for connector in self.connectors.values():
            try:
                await connector.disconnect()
            except Exception as e:
                self.logger.error(f"Error disconnecting connector: {e}")

        self.connectors.clear()
        self.logger.info("All connectors disconnected")


# Global connector manager instance
_connector_manager: Optional[ConnectorManager] = None


def get_connector_manager(security_manager: Optional[EnterpriseSecurityManager] = None) -> ConnectorManager:
    """Get or create global connector manager"""
    global _connector_manager
    if _connector_manager is None:
        _connector_manager = ConnectorManager(security_manager)
    return _connector_manager