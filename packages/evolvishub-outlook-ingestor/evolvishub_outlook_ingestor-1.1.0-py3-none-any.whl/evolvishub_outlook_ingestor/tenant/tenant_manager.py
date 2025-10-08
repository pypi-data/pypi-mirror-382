"""
Multi-tenant management service for enterprise deployments.

This module provides comprehensive multi-tenancy capabilities including
tenant isolation, resource management, and configuration management.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum

from evolvishub_outlook_ingestor.core.interfaces import ITenantManager, service_registry
from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import TenantError, PermissionError


class TenantStatus(Enum):
    """Tenant status options."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
    PENDING = "pending"


class ResourceType(Enum):
    """Types of resources that can be managed per tenant."""
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    API_CALLS = "api_calls"
    CONCURRENT_CONNECTIONS = "concurrent_connections"
    EMAIL_PROCESSING = "email_processing"


@dataclass
class TenantConfig:
    """Tenant configuration and metadata."""
    tenant_id: str
    name: str
    status: TenantStatus
    created_at: datetime
    updated_at: datetime
    settings: Dict[str, Any]
    resource_limits: Dict[str, int]
    permissions: Set[str]
    metadata: Dict[str, Any]


@dataclass
class ResourceUsage:
    """Resource usage tracking for a tenant."""
    tenant_id: str
    resource_type: ResourceType
    current_usage: int
    limit: int
    period_start: datetime
    period_end: datetime
    usage_history: List[Dict[str, Any]]


class MultiTenantManager(ITenantManager):
    """
    Multi-tenant management service for enterprise deployments.
    
    This service provides comprehensive multi-tenancy capabilities including:
    - Tenant lifecycle management (create, update, suspend, delete)
    - Data isolation and security boundaries
    - Resource quotas and usage tracking
    - Tenant-specific configurations and settings
    - Permission management and access control
    - Cross-tenant analytics and reporting
    
    Example:
        ```python
        tenant_manager = MultiTenantManager({
            'storage_connector': postgresql_connector,
            'enable_resource_tracking': True,
            'default_limits': {
                'storage': 10737418240,  # 10GB
                'api_calls': 100000,     # per day
                'concurrent_connections': 50
            }
        })
        
        await tenant_manager.initialize()
        
        # Create tenant
        tenant_id = await tenant_manager.create_tenant({
            'name': 'Acme Corp',
            'settings': {'timezone': 'UTC'},
            'limits': {'storage': 21474836480}  # 20GB
        })
        
        # Check permissions
        can_access = await tenant_manager.check_permissions(
            tenant_id, 'email_data', 'read'
        )
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.storage_connector = config.get('storage_connector')
        self.enable_resource_tracking = config.get('enable_resource_tracking', True)
        self.enable_cross_tenant_analytics = config.get('enable_cross_tenant_analytics', False)
        self.default_limits = config.get('default_limits', {})
        self.isolation_level = config.get('isolation_level', 'strict')  # strict, moderate, relaxed
        
        # State management
        self.is_initialized = False
        self._tenant_configs: Dict[str, TenantConfig] = {}
        self._resource_usage: Dict[str, Dict[str, ResourceUsage]] = {}
        self._active_sessions: Dict[str, Set[str]] = {}  # tenant_id -> session_ids
        
        # Background tasks
        self._usage_tracker_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            'total_tenants': 0,
            'active_tenants': 0,
            'suspended_tenants': 0,
            'total_resource_violations': 0,
            'cross_tenant_requests': 0
        }
    
    async def initialize(self) -> None:
        """Initialize the multi-tenant manager."""
        if self.is_initialized:
            return
        
        try:
            self.logger.info("Initializing multi-tenant manager")
            
            # Validate storage connector
            if not self.storage_connector:
                raise ValueError("Storage connector is required for tenant management")
            
            # Create tenant management tables
            await self._create_tenant_tables()
            
            # Load existing tenant configurations
            await self._load_tenant_configs()
            
            # Start background tasks
            if self.enable_resource_tracking:
                self._usage_tracker_task = asyncio.create_task(self._track_resource_usage())
            
            self._cleanup_task = asyncio.create_task(self._cleanup_inactive_sessions())
            
            self.is_initialized = True
            self.logger.info(f"Multi-tenant manager initialized with {len(self._tenant_configs)} tenants")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize tenant manager: {str(e)}")
            raise TenantError(f"Tenant manager initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the tenant manager."""
        if not self.is_initialized:
            return
        
        self.logger.info("Shutting down tenant manager")
        
        # Cancel background tasks
        tasks = [self._usage_tracker_task, self._cleanup_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Save current state
        await self._save_tenant_configs()
        
        self.is_initialized = False
        self.logger.info("Tenant manager shutdown complete")
    
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> str:
        """
        Create a new tenant.
        
        Args:
            tenant_data: Tenant configuration data
            
        Returns:
            Created tenant ID
        """
        try:
            tenant_id = f"tenant_{datetime.now(timezone.utc).timestamp()}"
            
            # Merge with default limits
            resource_limits = {**self.default_limits, **tenant_data.get('limits', {})}
            
            # Create tenant configuration
            tenant_config = TenantConfig(
                tenant_id=tenant_id,
                name=tenant_data['name'],
                status=TenantStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                settings=tenant_data.get('settings', {}),
                resource_limits=resource_limits,
                permissions=set(tenant_data.get('permissions', ['read', 'write'])),
                metadata=tenant_data.get('metadata', {})
            )
            
            # Store tenant configuration
            self._tenant_configs[tenant_id] = tenant_config
            await self._save_tenant_config(tenant_config)
            
            # Initialize resource tracking
            if self.enable_resource_tracking:
                await self._initialize_tenant_resources(tenant_id, resource_limits)
            
            # Create tenant-specific database schema/namespace
            await self._create_tenant_schema(tenant_id)
            
            self.stats['total_tenants'] += 1
            self.stats['active_tenants'] += 1
            
            self.logger.info(f"Created tenant: {tenant_id} ({tenant_data['name']})")
            return tenant_id
            
        except Exception as e:
            self.logger.error(f"Failed to create tenant: {str(e)}")
            raise TenantError(f"Tenant creation failed: {str(e)}")
    
    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get configuration for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant configuration dictionary
        """
        if tenant_id not in self._tenant_configs:
            raise TenantError(f"Tenant not found: {tenant_id}")
        
        config = self._tenant_configs[tenant_id]
        return {
            'tenant_id': config.tenant_id,
            'name': config.name,
            'status': config.status.value,
            'created_at': config.created_at.isoformat(),
            'updated_at': config.updated_at.isoformat(),
            'settings': config.settings,
            'resource_limits': config.resource_limits,
            'permissions': list(config.permissions),
            'metadata': config.metadata
        }
    
    async def update_tenant_config(self, tenant_id: str, updates: Dict[str, Any]) -> None:
        """
        Update tenant configuration.
        
        Args:
            tenant_id: Tenant identifier
            updates: Configuration updates
        """
        if tenant_id not in self._tenant_configs:
            raise TenantError(f"Tenant not found: {tenant_id}")
        
        try:
            config = self._tenant_configs[tenant_id]
            
            # Update fields
            if 'name' in updates:
                config.name = updates['name']
            if 'status' in updates:
                config.status = TenantStatus(updates['status'])
            if 'settings' in updates:
                config.settings.update(updates['settings'])
            if 'resource_limits' in updates:
                config.resource_limits.update(updates['resource_limits'])
            if 'permissions' in updates:
                config.permissions = set(updates['permissions'])
            if 'metadata' in updates:
                config.metadata.update(updates['metadata'])
            
            config.updated_at = datetime.now(timezone.utc)
            
            # Save updated configuration
            await self._save_tenant_config(config)
            
            self.logger.info(f"Updated tenant configuration: {tenant_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to update tenant {tenant_id}: {str(e)}")
            raise TenantError(f"Tenant update failed: {str(e)}")
    
    async def isolate_data(self, tenant_id: str, data: Any) -> Any:
        """
        Apply tenant isolation to data.
        
        Args:
            tenant_id: Tenant identifier
            data: Data to isolate
            
        Returns:
            Isolated data with tenant context
        """
        if tenant_id not in self._tenant_configs:
            raise TenantError(f"Tenant not found: {tenant_id}")
        
        try:
            # Add tenant context to data
            if isinstance(data, EmailMessage):
                # Add tenant ID to extended properties
                if not data.extended_properties:
                    data.extended_properties = {}
                data.extended_properties['tenant_id'] = tenant_id
                data.extended_properties['isolation_level'] = self.isolation_level
            
            elif isinstance(data, dict):
                # Add tenant context to dictionary
                data['_tenant_id'] = tenant_id
                data['_isolation_level'] = self.isolation_level
            
            elif isinstance(data, list):
                # Apply isolation to each item in list
                return [await self.isolate_data(tenant_id, item) for item in data]
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to isolate data for tenant {tenant_id}: {str(e)}")
            raise TenantError(f"Data isolation failed: {str(e)}")
    
    async def check_permissions(self, tenant_id: str, resource: str, action: str) -> bool:
        """
        Check tenant permissions for a resource and action.
        
        Args:
            tenant_id: Tenant identifier
            resource: Resource name
            action: Action to check (read, write, delete, etc.)
            
        Returns:
            True if permission is granted, False otherwise
        """
        if tenant_id not in self._tenant_configs:
            return False
        
        config = self._tenant_configs[tenant_id]
        
        # Check tenant status
        if config.status != TenantStatus.ACTIVE:
            return False
        
        # Check resource limits
        if self.enable_resource_tracking:
            if not await self._check_resource_limits(tenant_id, action):
                return False
        
        # Check permissions
        permission_key = f"{resource}:{action}"
        if permission_key in config.permissions:
            return True
        
        # Check wildcard permissions
        wildcard_permissions = [
            f"{resource}:*",
            f"*:{action}",
            "*:*"
        ]
        
        for perm in wildcard_permissions:
            if perm in config.permissions:
                return True
        
        return False
    
    async def get_tenant_usage(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get resource usage for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Resource usage information
        """
        if tenant_id not in self._tenant_configs:
            raise TenantError(f"Tenant not found: {tenant_id}")
        
        if not self.enable_resource_tracking:
            return {'message': 'Resource tracking disabled'}
        
        usage_data = {}
        tenant_usage = self._resource_usage.get(tenant_id, {})
        
        for resource_type, usage in tenant_usage.items():
            usage_data[resource_type] = {
                'current_usage': usage.current_usage,
                'limit': usage.limit,
                'usage_percentage': (usage.current_usage / usage.limit * 100) if usage.limit > 0 else 0,
                'period_start': usage.period_start.isoformat(),
                'period_end': usage.period_end.isoformat()
            }
        
        return usage_data
    
    async def suspend_tenant(self, tenant_id: str, reason: str) -> None:
        """
        Suspend a tenant.
        
        Args:
            tenant_id: Tenant identifier
            reason: Reason for suspension
        """
        if tenant_id not in self._tenant_configs:
            raise TenantError(f"Tenant not found: {tenant_id}")
        
        config = self._tenant_configs[tenant_id]
        config.status = TenantStatus.SUSPENDED
        config.updated_at = datetime.now(timezone.utc)
        config.metadata['suspension_reason'] = reason
        config.metadata['suspended_at'] = datetime.now(timezone.utc).isoformat()
        
        await self._save_tenant_config(config)
        
        # Terminate active sessions
        if tenant_id in self._active_sessions:
            self._active_sessions[tenant_id].clear()
        
        self.stats['active_tenants'] -= 1
        self.stats['suspended_tenants'] += 1
        
        self.logger.warning(f"Suspended tenant {tenant_id}: {reason}")
    
    async def reactivate_tenant(self, tenant_id: str) -> None:
        """
        Reactivate a suspended tenant.
        
        Args:
            tenant_id: Tenant identifier
        """
        if tenant_id not in self._tenant_configs:
            raise TenantError(f"Tenant not found: {tenant_id}")
        
        config = self._tenant_configs[tenant_id]
        if config.status != TenantStatus.SUSPENDED:
            raise TenantError(f"Tenant {tenant_id} is not suspended")
        
        config.status = TenantStatus.ACTIVE
        config.updated_at = datetime.now(timezone.utc)
        config.metadata.pop('suspension_reason', None)
        config.metadata.pop('suspended_at', None)
        config.metadata['reactivated_at'] = datetime.now(timezone.utc).isoformat()
        
        await self._save_tenant_config(config)
        
        self.stats['active_tenants'] += 1
        self.stats['suspended_tenants'] -= 1
        
        self.logger.info(f"Reactivated tenant: {tenant_id}")
    
    async def _create_tenant_tables(self) -> None:
        """Create tenant management tables."""
        if hasattr(self.storage_connector, 'execute'):
            # SQL-based connector
            await self.storage_connector.execute("""
                CREATE TABLE IF NOT EXISTS tenant_configs (
                    tenant_id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    settings JSONB DEFAULT '{}',
                    resource_limits JSONB DEFAULT '{}',
                    permissions JSONB DEFAULT '[]',
                    metadata JSONB DEFAULT '{}'
                )
            """)
            
            await self.storage_connector.execute("""
                CREATE TABLE IF NOT EXISTS tenant_resource_usage (
                    tenant_id VARCHAR(255),
                    resource_type VARCHAR(50),
                    current_usage BIGINT DEFAULT 0,
                    limit_value BIGINT DEFAULT 0,
                    period_start TIMESTAMP WITH TIME ZONE,
                    period_end TIMESTAMP WITH TIME ZONE,
                    usage_history JSONB DEFAULT '[]',
                    PRIMARY KEY (tenant_id, resource_type)
                )
            """)
        
        elif hasattr(self.storage_connector, 'create_index'):
            # MongoDB-based connector
            await self.storage_connector.database.tenant_configs.create_index("tenant_id", unique=True)
            await self.storage_connector.database.tenant_resource_usage.create_index([("tenant_id", 1), ("resource_type", 1)])
    
    async def _load_tenant_configs(self) -> None:
        """Load existing tenant configurations from storage."""
        try:
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based connector
                results = await self.storage_connector.execute("SELECT * FROM tenant_configs")
                for row in results:
                    config = self._row_to_tenant_config(row)
                    self._tenant_configs[config.tenant_id] = config
            
            elif hasattr(self.storage_connector, 'find'):
                # MongoDB-based connector
                cursor = self.storage_connector.database.tenant_configs.find({})
                async for doc in cursor:
                    config = self._doc_to_tenant_config(doc)
                    self._tenant_configs[config.tenant_id] = config
            
            # Update statistics
            self.stats['total_tenants'] = len(self._tenant_configs)
            self.stats['active_tenants'] = sum(1 for c in self._tenant_configs.values() if c.status == TenantStatus.ACTIVE)
            self.stats['suspended_tenants'] = sum(1 for c in self._tenant_configs.values() if c.status == TenantStatus.SUSPENDED)
            
        except Exception as e:
            self.logger.error(f"Failed to load tenant configurations: {str(e)}")
    
    async def _save_tenant_config(self, config: TenantConfig) -> None:
        """Save tenant configuration to storage."""
        try:
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based connector
                await self.storage_connector.execute("""
                    INSERT INTO tenant_configs 
                    (tenant_id, name, status, created_at, updated_at, settings, resource_limits, permissions, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tenant_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        status = EXCLUDED.status,
                        updated_at = EXCLUDED.updated_at,
                        settings = EXCLUDED.settings,
                        resource_limits = EXCLUDED.resource_limits,
                        permissions = EXCLUDED.permissions,
                        metadata = EXCLUDED.metadata
                """, (
                    config.tenant_id, config.name, config.status.value,
                    config.created_at, config.updated_at,
                    config.settings, config.resource_limits,
                    list(config.permissions), config.metadata
                ))
            
            elif hasattr(self.storage_connector, 'replace_one'):
                # MongoDB-based connector
                doc = asdict(config)
                doc['status'] = config.status.value
                doc['permissions'] = list(config.permissions)
                
                await self.storage_connector.database.tenant_configs.replace_one(
                    {'tenant_id': config.tenant_id},
                    doc,
                    upsert=True
                )
        
        except Exception as e:
            self.logger.error(f"Failed to save tenant config {config.tenant_id}: {str(e)}")
    
    async def _save_tenant_configs(self) -> None:
        """Save all tenant configurations."""
        for config in self._tenant_configs.values():
            await self._save_tenant_config(config)
    
    async def _initialize_tenant_resources(self, tenant_id: str, limits: Dict[str, int]) -> None:
        """Initialize resource tracking for a tenant."""
        current_time = datetime.now(timezone.utc)
        period_end = current_time + timedelta(days=1)  # Daily periods
        
        self._resource_usage[tenant_id] = {}
        
        for resource_name, limit in limits.items():
            try:
                resource_type = ResourceType(resource_name)
                usage = ResourceUsage(
                    tenant_id=tenant_id,
                    resource_type=resource_type,
                    current_usage=0,
                    limit=limit,
                    period_start=current_time,
                    period_end=period_end,
                    usage_history=[]
                )
                self._resource_usage[tenant_id][resource_name] = usage
            except ValueError:
                self.logger.warning(f"Unknown resource type: {resource_name}")
    
    async def _create_tenant_schema(self, tenant_id: str) -> None:
        """Create tenant-specific database schema or namespace."""
        try:
            if self.isolation_level == 'strict':
                await self._create_strict_isolation_schema(tenant_id)
            elif self.isolation_level == 'moderate':
                await self._create_moderate_isolation_schema(tenant_id)
            else:  # relaxed
                await self._create_relaxed_isolation_schema(tenant_id)

            self.logger.info(f"Created tenant schema for {tenant_id} with {self.isolation_level} isolation")

        except Exception as e:
            self.logger.error(f"Failed to create tenant schema for {tenant_id}: {str(e)}")
            raise TenantError(f"Schema creation failed: {str(e)}")

    async def _create_strict_isolation_schema(self, tenant_id: str) -> None:
        """Create separate schema/database for strict isolation."""
        if hasattr(self.storage_connector, 'execute'):
            # PostgreSQL: Create separate schema
            schema_name = f"tenant_{tenant_id.replace('-', '_')}"
            await self.storage_connector.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

            # Create tenant-specific tables
            await self.storage_connector.execute(f"""
                CREATE TABLE IF NOT EXISTS {schema_name}.emails (
                    id VARCHAR(255) PRIMARY KEY,
                    message_id VARCHAR(255),
                    subject TEXT,
                    sender_email VARCHAR(255),
                    sender_name VARCHAR(255),
                    body TEXT,
                    received_date TIMESTAMP WITH TIME ZONE,
                    sent_date TIMESTAMP WITH TIME ZONE,
                    folder_id VARCHAR(255),
                    is_read BOOLEAN DEFAULT FALSE,
                    is_flagged BOOLEAN DEFAULT FALSE,
                    importance VARCHAR(20),
                    sensitivity VARCHAR(20),
                    has_attachments BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)

        elif hasattr(self.storage_connector, 'create_collection'):
            # MongoDB: Create separate database
            db_name = f"tenant_{tenant_id.replace('-', '_')}"
            tenant_db = self.storage_connector.client[db_name]
            await tenant_db.create_collection('emails')
            await tenant_db.emails.create_index('message_id')
            await tenant_db.emails.create_index('received_date')

    async def _create_moderate_isolation_schema(self, tenant_id: str) -> None:
        """Create table prefixes or partitioning for moderate isolation."""
        if hasattr(self.storage_connector, 'execute'):
            # PostgreSQL: Create partitioned table
            table_name = f"emails_{tenant_id.replace('-', '_')}"
            await self.storage_connector.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    LIKE emails INCLUDING ALL
                ) INHERITS (emails)
            """)

            # Add check constraint for tenant isolation
            await self.storage_connector.execute(f"""
                ALTER TABLE {table_name}
                ADD CONSTRAINT check_tenant_id
                CHECK (tenant_id = '{tenant_id}')
            """)

        elif hasattr(self.storage_connector, 'create_collection'):
            # MongoDB: Use tenant-prefixed collections
            collection_name = f"emails_{tenant_id.replace('-', '_')}"
            await self.storage_connector.database.create_collection(collection_name)
            await self.storage_connector.database[collection_name].create_index('tenant_id')

    async def _create_relaxed_isolation_schema(self, tenant_id: str) -> None:
        """Create row-level security for relaxed isolation."""
        if hasattr(self.storage_connector, 'execute'):
            # PostgreSQL: Enable row-level security
            await self.storage_connector.execute("ALTER TABLE emails ENABLE ROW LEVEL SECURITY")

            # Create policy for tenant isolation
            policy_name = f"tenant_{tenant_id.replace('-', '_')}_policy"
            await self.storage_connector.execute(f"""
                CREATE POLICY {policy_name} ON emails
                FOR ALL TO tenant_{tenant_id.replace('-', '_')}_role
                USING (tenant_id = '{tenant_id}')
            """)

            # Create tenant-specific role
            role_name = f"tenant_{tenant_id.replace('-', '_')}_role"
            await self.storage_connector.execute(f"CREATE ROLE {role_name}")
            await self.storage_connector.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON emails TO {role_name}")

        # For MongoDB, row-level security is handled at application level through queries
    
    async def _check_resource_limits(self, tenant_id: str, action: str) -> bool:
        """Check if tenant has exceeded resource limits."""
        if tenant_id not in self._resource_usage:
            return True
        
        tenant_usage = self._resource_usage[tenant_id]
        
        # Check relevant resource limits based on action
        if action in ['read', 'write'] and 'api_calls' in tenant_usage:
            usage = tenant_usage['api_calls']
            if usage.current_usage >= usage.limit:
                self.stats['total_resource_violations'] += 1
                return False
        
        return True
    
    async def _track_resource_usage(self) -> None:
        """Background task to track resource usage."""
        while self.is_initialized:
            try:
                # Update resource usage metrics
                # This would integrate with actual usage tracking
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in resource usage tracking: {str(e)}")
                await asyncio.sleep(60)
    
    async def _cleanup_inactive_sessions(self) -> None:
        """Background task to clean up inactive sessions."""
        while self.is_initialized:
            try:
                # Clean up sessions that haven't been active for a while
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                self.logger.error(f"Error in session cleanup: {str(e)}")
                await asyncio.sleep(300)
    
    def _row_to_tenant_config(self, row: tuple) -> TenantConfig:
        """Convert database row to TenantConfig."""
        return TenantConfig(
            tenant_id=row[0],
            name=row[1],
            status=TenantStatus(row[2]),
            created_at=row[3],
            updated_at=row[4],
            settings=row[5] or {},
            resource_limits=row[6] or {},
            permissions=set(row[7] or []),
            metadata=row[8] or {}
        )
    
    def _doc_to_tenant_config(self, doc: Dict[str, Any]) -> TenantConfig:
        """Convert MongoDB document to TenantConfig."""
        return TenantConfig(
            tenant_id=doc['tenant_id'],
            name=doc['name'],
            status=TenantStatus(doc['status']),
            created_at=doc['created_at'],
            updated_at=doc['updated_at'],
            settings=doc.get('settings', {}),
            resource_limits=doc.get('resource_limits', {}),
            permissions=set(doc.get('permissions', [])),
            metadata=doc.get('metadata', {})
        )
    
    async def get_tenant_stats(self) -> Dict[str, Any]:
        """Get tenant management statistics."""
        return {
            **self.stats,
            'is_initialized': self.is_initialized,
            'resource_tracking_enabled': self.enable_resource_tracking,
            'cross_tenant_analytics_enabled': self.enable_cross_tenant_analytics,
            'isolation_level': self.isolation_level
        }
