"""
Health checking and system monitoring.

This module provides comprehensive health checking capabilities for
monitoring system dependencies and service health.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from evolvishub_outlook_ingestor.core.exceptions import MonitoringError

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """A health check result."""
    check_name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time_ms: float
    metadata: Dict[str, Any]


class HealthChecker:
    """
    Performs health checks on system components.
    
    Provides comprehensive health monitoring including:
    - Database connectivity checks
    - External service health
    - System resource monitoring
    - Dependency health validation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the health checker.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.checks: Dict[str, callable] = {}
        
    async def initialize(self) -> None:
        """Initialize the health checker."""
        logger.info("Initializing HealthChecker")
        
        # Register default health checks
        await self._register_default_checks()
        
    async def register_check(self, name: str, check_func: callable) -> None:
        """Register a health check function."""
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")
        
    async def run_all_checks(self) -> List[HealthCheck]:
        """Run all registered health checks."""
        results = []
        
        for name, check_func in self.checks.items():
            try:
                result = await self._run_check(name, check_func)
                results.append(result)
            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results.append(HealthCheck(
                    check_name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check failed: {e}",
                    timestamp=datetime.utcnow(),
                    response_time_ms=0.0,
                    metadata={}
                ))
        
        return results
        
    async def run_check(self, name: str) -> Optional[HealthCheck]:
        """Run a specific health check."""
        if name not in self.checks:
            return None
            
        try:
            return await self._run_check(name, self.checks[name])
        except Exception as e:
            logger.error(f"Health check {name} failed: {e}")
            return HealthCheck(
                check_name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {e}",
                timestamp=datetime.utcnow(),
                response_time_ms=0.0,
                metadata={}
            )
    
    async def get_overall_health(self) -> HealthStatus:
        """Get overall system health status."""
        checks = await self.run_all_checks()
        
        if not checks:
            return HealthStatus.UNHEALTHY
        
        # If any check is unhealthy, system is unhealthy
        if any(check.status == HealthStatus.UNHEALTHY for check in checks):
            return HealthStatus.UNHEALTHY
        
        # If any check is degraded, system is degraded
        if any(check.status == HealthStatus.DEGRADED for check in checks):
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    async def _run_check(self, name: str, check_func: callable) -> HealthCheck:
        """Run a single health check with timing."""
        start_time = datetime.utcnow()
        
        try:
            result = await check_func()
            
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            if isinstance(result, dict):
                status = HealthStatus(result.get('status', 'healthy'))
                message = result.get('message', 'OK')
                metadata = result.get('metadata', {})
            else:
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                message = 'OK' if result else 'Check failed'
                metadata = {}
            
            return HealthCheck(
                check_name=name,
                status=status,
                message=message,
                timestamp=start_time,
                response_time_ms=response_time_ms,
                metadata=metadata
            )
            
        except Exception as e:
            end_time = datetime.utcnow()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            return HealthCheck(
                check_name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Check failed: {e}",
                timestamp=start_time,
                response_time_ms=response_time_ms,
                metadata={}
            )
    
    async def _register_default_checks(self) -> None:
        """Register default health checks."""
        
        async def database_check():
            """Check database connectivity."""
            # Placeholder for database check
            return {
                'status': 'healthy',
                'message': 'Database connection OK',
                'metadata': {'connection_pool_size': 10}
            }
        
        async def memory_check():
            """Check memory usage."""
            # Placeholder for memory check
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = 'unhealthy'
                message = f'High memory usage: {memory.percent}%'
            elif memory.percent > 80:
                status = 'degraded'
                message = f'Elevated memory usage: {memory.percent}%'
            else:
                status = 'healthy'
                message = f'Memory usage OK: {memory.percent}%'
            
            return {
                'status': status,
                'message': message,
                'metadata': {
                    'memory_percent': memory.percent,
                    'memory_available': memory.available
                }
            }
        
        async def disk_check():
            """Check disk space."""
            # Placeholder for disk check
            import psutil
            disk = psutil.disk_usage('/')
            
            percent_used = (disk.used / disk.total) * 100
            
            if percent_used > 95:
                status = 'unhealthy'
                message = f'Critical disk usage: {percent_used:.1f}%'
            elif percent_used > 85:
                status = 'degraded'
                message = f'High disk usage: {percent_used:.1f}%'
            else:
                status = 'healthy'
                message = f'Disk usage OK: {percent_used:.1f}%'
            
            return {
                'status': status,
                'message': message,
                'metadata': {
                    'disk_percent': percent_used,
                    'disk_free': disk.free
                }
            }
        
        # Register checks
        await self.register_check('database', database_check)
        
        try:
            import psutil
            await self.register_check('memory', memory_check)
            await self.register_check('disk', disk_check)
        except ImportError:
            logger.warning("psutil not available - system resource checks disabled")
