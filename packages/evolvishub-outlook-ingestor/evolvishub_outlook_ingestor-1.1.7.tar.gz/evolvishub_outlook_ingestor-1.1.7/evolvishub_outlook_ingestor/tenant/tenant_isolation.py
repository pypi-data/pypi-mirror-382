"""
Tenant isolation and security mechanisms.

This module provides comprehensive tenant isolation capabilities including
data segregation, resource isolation, and security boundaries.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import hashlib

from evolvishub_outlook_ingestor.core.exceptions import TenantError

logger = logging.getLogger(__name__)


class IsolationLevel(Enum):
    """Tenant isolation levels."""
    SHARED = "shared"
    SCHEMA = "schema"
    DATABASE = "database"
    INSTANCE = "instance"


@dataclass
class TenantContext:
    """Tenant execution context."""
    tenant_id: str
    isolation_level: IsolationLevel
    resource_limits: Dict[str, Any]
    permissions: Set[str]
    metadata: Dict[str, Any]


class TenantIsolationManager:
    """
    Manages tenant isolation and security boundaries.
    
    Provides comprehensive isolation including:
    - Data segregation strategies
    - Resource isolation and limits
    - Security boundary enforcement
    - Cross-tenant access prevention
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the tenant isolation manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.tenant_contexts: Dict[str, TenantContext] = {}
        self.active_sessions: Dict[str, str] = {}  # session_id -> tenant_id
        
    async def initialize(self) -> None:
        """Initialize the tenant isolation manager."""
        logger.info("Initializing TenantIsolationManager")
        
    async def create_tenant_context(
        self, 
        tenant_id: str, 
        isolation_level: IsolationLevel,
        resource_limits: Optional[Dict[str, Any]] = None,
        permissions: Optional[Set[str]] = None
    ) -> TenantContext:
        """
        Create a tenant context.
        
        Args:
            tenant_id: Unique tenant identifier
            isolation_level: Level of isolation required
            resource_limits: Resource limits for the tenant
            permissions: Set of permissions for the tenant
            
        Returns:
            Tenant context
        """
        try:
            context = TenantContext(
                tenant_id=tenant_id,
                isolation_level=isolation_level,
                resource_limits=resource_limits or {},
                permissions=permissions or set(),
                metadata={}
            )
            
            self.tenant_contexts[tenant_id] = context
            
            logger.info(f"Created tenant context for {tenant_id} with {isolation_level.value} isolation")
            
            return context
            
        except Exception as e:
            logger.error(f"Error creating tenant context: {e}")
            raise TenantError(f"Failed to create tenant context: {e}")
    
    async def get_tenant_context(self, tenant_id: str) -> Optional[TenantContext]:
        """Get tenant context by ID."""
        return self.tenant_contexts.get(tenant_id)
    
    async def validate_tenant_access(self, tenant_id: str, resource: str, operation: str) -> bool:
        """
        Validate tenant access to a resource.
        
        Args:
            tenant_id: Tenant identifier
            resource: Resource being accessed
            operation: Operation being performed
            
        Returns:
            True if access is allowed
        """
        try:
            context = await self.get_tenant_context(tenant_id)
            if not context:
                logger.warning(f"No context found for tenant {tenant_id}")
                return False
            
            # Check permissions
            required_permission = f"{resource}:{operation}"
            if required_permission not in context.permissions and "*" not in context.permissions:
                logger.warning(f"Tenant {tenant_id} lacks permission for {required_permission}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating tenant access: {e}")
            return False
    
    async def get_isolated_resource_name(self, tenant_id: str, resource_name: str) -> str:
        """
        Get isolated resource name based on tenant isolation level.
        
        Args:
            tenant_id: Tenant identifier
            resource_name: Base resource name
            
        Returns:
            Isolated resource name
        """
        try:
            context = await self.get_tenant_context(tenant_id)
            if not context:
                raise TenantError(f"No context found for tenant {tenant_id}")
            
            if context.isolation_level == IsolationLevel.SHARED:
                # Shared resources with tenant prefix
                return f"shared_{resource_name}"
            
            elif context.isolation_level == IsolationLevel.SCHEMA:
                # Schema-level isolation
                tenant_hash = hashlib.md5(tenant_id.encode()).hexdigest()[:8]
                return f"tenant_{tenant_hash}_{resource_name}"
            
            elif context.isolation_level == IsolationLevel.DATABASE:
                # Database-level isolation
                tenant_hash = hashlib.md5(tenant_id.encode()).hexdigest()[:8]
                return f"db_tenant_{tenant_hash}_{resource_name}"
            
            elif context.isolation_level == IsolationLevel.INSTANCE:
                # Instance-level isolation
                return f"instance_{tenant_id}_{resource_name}"
            
            else:
                raise TenantError(f"Unknown isolation level: {context.isolation_level}")
                
        except Exception as e:
            logger.error(f"Error getting isolated resource name: {e}")
            raise TenantError(f"Failed to get isolated resource name: {e}")
    
    async def check_resource_limits(self, tenant_id: str, resource_type: str, current_usage: float) -> bool:
        """
        Check if tenant is within resource limits.
        
        Args:
            tenant_id: Tenant identifier
            resource_type: Type of resource (cpu, memory, storage, etc.)
            current_usage: Current usage amount
            
        Returns:
            True if within limits
        """
        try:
            context = await self.get_tenant_context(tenant_id)
            if not context:
                return False
            
            limit = context.resource_limits.get(resource_type)
            if limit is None:
                # No limit set, allow
                return True
            
            return current_usage <= limit
            
        except Exception as e:
            logger.error(f"Error checking resource limits: {e}")
            return False
    
    async def create_session(self, tenant_id: str) -> str:
        """
        Create a tenant session.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Session ID
        """
        try:
            # Validate tenant exists
            context = await self.get_tenant_context(tenant_id)
            if not context:
                raise TenantError(f"Tenant {tenant_id} not found")
            
            # Generate session ID
            session_data = f"{tenant_id}:{asyncio.get_event_loop().time()}"
            session_id = hashlib.sha256(session_data.encode()).hexdigest()
            
            self.active_sessions[session_id] = tenant_id
            
            logger.info(f"Created session {session_id} for tenant {tenant_id}")
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise TenantError(f"Failed to create session: {e}")
    
    async def get_tenant_from_session(self, session_id: str) -> Optional[str]:
        """Get tenant ID from session ID."""
        return self.active_sessions.get(session_id)
    
    async def close_session(self, session_id: str) -> bool:
        """
        Close a tenant session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if session was closed
        """
        if session_id in self.active_sessions:
            tenant_id = self.active_sessions[session_id]
            del self.active_sessions[session_id]
            
            logger.info(f"Closed session {session_id} for tenant {tenant_id}")
            
            return True
        
        return False
    
    async def get_tenant_metrics(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get metrics for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Tenant metrics
        """
        try:
            context = await self.get_tenant_context(tenant_id)
            if not context:
                return {}
            
            # Count active sessions
            active_sessions = sum(1 for tid in self.active_sessions.values() if tid == tenant_id)
            
            return {
                'tenant_id': tenant_id,
                'isolation_level': context.isolation_level.value,
                'active_sessions': active_sessions,
                'resource_limits': context.resource_limits,
                'permissions_count': len(context.permissions)
            }
            
        except Exception as e:
            logger.error(f"Error getting tenant metrics: {e}")
            return {}
    
    async def cleanup_expired_sessions(self, max_age_seconds: int = 3600) -> int:
        """
        Clean up expired sessions.
        
        Args:
            max_age_seconds: Maximum session age in seconds
            
        Returns:
            Number of sessions cleaned up
        """
        # This is a simplified implementation
        # In a real system, you'd track session creation times
        cleanup_count = 0
        
        # For now, just return 0 as we don't track session ages
        return cleanup_count


# Alias for backward compatibility
TenantIsolationService = TenantIsolationManager
