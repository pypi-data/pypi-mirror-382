"""
Resource management for multi-tenant environments.

This module provides comprehensive resource management capabilities including
resource allocation, monitoring, and enforcement for multi-tenant systems.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from evolvishub_outlook_ingestor.core.exceptions import TenantError

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that can be managed."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    CONNECTIONS = "connections"
    REQUESTS = "requests"


@dataclass
class ResourceLimit:
    """Resource limit definition."""
    resource_type: ResourceType
    limit: float
    unit: str
    period: Optional[str] = None  # For rate limits


@dataclass
class ResourceUsage:
    """Current resource usage."""
    resource_type: ResourceType
    current: float
    limit: float
    unit: str
    utilization_percent: float


class ResourceManager:
    """
    Manages resources for multi-tenant environments.
    
    Provides comprehensive resource management including:
    - Resource allocation and limits
    - Usage monitoring and tracking
    - Enforcement and throttling
    - Resource optimization
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the resource manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.tenant_limits: Dict[str, Dict[ResourceType, ResourceLimit]] = {}
        self.current_usage: Dict[str, Dict[ResourceType, float]] = {}
        
    async def initialize(self) -> None:
        """Initialize the resource manager."""
        logger.info("Initializing ResourceManager")
        
    async def set_tenant_limits(self, tenant_id: str, limits: List[ResourceLimit]) -> None:
        """
        Set resource limits for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            limits: List of resource limits
        """
        try:
            if tenant_id not in self.tenant_limits:
                self.tenant_limits[tenant_id] = {}
            
            for limit in limits:
                self.tenant_limits[tenant_id][limit.resource_type] = limit
            
            logger.info(f"Set {len(limits)} resource limits for tenant {tenant_id}")
            
        except Exception as e:
            logger.error(f"Error setting tenant limits: {e}")
            raise TenantError(f"Failed to set tenant limits: {e}")
    
    async def check_resource_availability(
        self, 
        tenant_id: str, 
        resource_type: ResourceType, 
        requested_amount: float
    ) -> bool:
        """
        Check if requested resource amount is available.
        
        Args:
            tenant_id: Tenant identifier
            resource_type: Type of resource
            requested_amount: Amount of resource requested
            
        Returns:
            True if resource is available
        """
        try:
            # Get tenant limits
            tenant_limits = self.tenant_limits.get(tenant_id, {})
            limit = tenant_limits.get(resource_type)
            
            if not limit:
                # No limit set, allow
                return True
            
            # Get current usage
            current_usage = self.current_usage.get(tenant_id, {}).get(resource_type, 0.0)
            
            # Check if request would exceed limit
            return (current_usage + requested_amount) <= limit.limit
            
        except Exception as e:
            logger.error(f"Error checking resource availability: {e}")
            return False
    
    async def allocate_resource(
        self, 
        tenant_id: str, 
        resource_type: ResourceType, 
        amount: float
    ) -> bool:
        """
        Allocate resource to a tenant.
        
        Args:
            tenant_id: Tenant identifier
            resource_type: Type of resource
            amount: Amount to allocate
            
        Returns:
            True if allocation successful
        """
        try:
            # Check availability first
            if not await self.check_resource_availability(tenant_id, resource_type, amount):
                return False
            
            # Initialize usage tracking if needed
            if tenant_id not in self.current_usage:
                self.current_usage[tenant_id] = {}
            
            # Allocate resource
            current = self.current_usage[tenant_id].get(resource_type, 0.0)
            self.current_usage[tenant_id][resource_type] = current + amount
            
            logger.debug(f"Allocated {amount} {resource_type.value} to tenant {tenant_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error allocating resource: {e}")
            return False
    
    async def release_resource(
        self, 
        tenant_id: str, 
        resource_type: ResourceType, 
        amount: float
    ) -> bool:
        """
        Release resource from a tenant.
        
        Args:
            tenant_id: Tenant identifier
            resource_type: Type of resource
            amount: Amount to release
            
        Returns:
            True if release successful
        """
        try:
            if tenant_id not in self.current_usage:
                return False
            
            current = self.current_usage[tenant_id].get(resource_type, 0.0)
            new_usage = max(0.0, current - amount)
            self.current_usage[tenant_id][resource_type] = new_usage
            
            logger.debug(f"Released {amount} {resource_type.value} from tenant {tenant_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error releasing resource: {e}")
            return False
    
    async def get_tenant_usage(self, tenant_id: str) -> List[ResourceUsage]:
        """
        Get current resource usage for a tenant.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            List of resource usage information
        """
        try:
            usage_list = []
            
            tenant_limits = self.tenant_limits.get(tenant_id, {})
            current_usage = self.current_usage.get(tenant_id, {})
            
            for resource_type, limit in tenant_limits.items():
                current = current_usage.get(resource_type, 0.0)
                utilization = (current / limit.limit * 100) if limit.limit > 0 else 0.0
                
                usage = ResourceUsage(
                    resource_type=resource_type,
                    current=current,
                    limit=limit.limit,
                    unit=limit.unit,
                    utilization_percent=utilization
                )
                
                usage_list.append(usage)
            
            return usage_list
            
        except Exception as e:
            logger.error(f"Error getting tenant usage: {e}")
            return []


# Alias for backward compatibility
TenantResourceManager = ResourceManager
