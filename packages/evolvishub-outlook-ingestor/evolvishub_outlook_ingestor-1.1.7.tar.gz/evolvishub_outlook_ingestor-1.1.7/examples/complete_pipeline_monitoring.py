#!/usr/bin/env python3
"""
Complete Pipeline with Monitoring and Error Handling

This example demonstrates a production-ready email processing pipeline with
comprehensive monitoring, error handling, alerting, and performance optimization.
It showcases all the advanced features of the Evolvishub Outlook Ingestor.

Requirements:
- All dependencies from previous examples
- Optional: Redis for caching (can be disabled)
- Optional: Slack webhook for notifications (can be disabled)

Usage:
    python complete_pipeline_monitoring.py
"""

import asyncio
import os
import json
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from evolvishub_outlook_ingestor.protocols.microsoft_graph import GraphAPIAdapter
from evolvishub_outlook_ingestor.connectors.postgresql_connector import PostgreSQLConnector
from evolvishub_outlook_ingestor.processors.email_processor import EmailProcessor
from evolvishub_outlook_ingestor.processors.attachment_processor import AttachmentProcessor
from evolvishub_outlook_ingestor.core.data_models import EmailMessage, ProcessingResult, ProcessingStatus
from evolvishub_outlook_ingestor.utils.security import SecureCredentialManager, CredentialMasker

# Import monitoring and optimization modules
import sys
sys.path.append('../monitoring')
sys.path.append('../optimization')

from monitoring.metrics import SystemMonitor, AlertSeverity, Alert
from optimization.performance import (
    BatchProcessor, 
    AsyncLRUCache, 
    get_performance_profiler,
    profile_performance
)


class ProductionEmailPipeline:
    """
    A production-ready email processing pipeline with comprehensive monitoring,
    error handling, performance optimization, and alerting capabilities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the production pipeline.
        
        Args:
            config: Comprehensive configuration dictionary
        """
        self.config = config
        self.system_monitor = SystemMonitor()
        self.performance_profiler = get_performance_profiler()
        
        # Components
        self.protocol = None
        self.connector = None
        self.email_processor = None
        self.attachment_processor = None
        self.batch_processor = None
        self.email_cache = None
        
        # Statistics
        self.pipeline_stats = {
            "emails_processed": 0,
            "errors_handled": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "alerts_triggered": 0,
            "start_time": None,
        }
        
        # Setup monitoring and alerting
        self._setup_monitoring()
        self._setup_alerting()
    
    def _setup_monitoring(self):
        """Setup comprehensive monitoring."""
        # Add custom health checks
        self.system_monitor.health_checker.register_health_check(
            "email_pipeline", self._pipeline_health_check
        )
        
        # Add custom metrics
        self.system_monitor.metrics.set_gauge("pipeline.emails_processed", 0)
        self.system_monitor.metrics.set_gauge("pipeline.error_rate", 0)
        self.system_monitor.metrics.set_gauge("pipeline.cache_hit_rate", 0)
    
    def _setup_alerting(self):
        """Setup alerting rules and notification handlers."""
        # Add pipeline-specific alert rules
        self.system_monitor.alert_manager.add_alert_rule(
            name="high_pipeline_error_rate",
            metric_name="pipeline.error_rate",
            threshold=10.0,  # 10% error rate
            comparison="greater_than",
            severity=AlertSeverity.HIGH,
            component="pipeline",
            description="Email pipeline error rate is above 10%"
        )
        
        self.system_monitor.alert_manager.add_alert_rule(
            name="low_cache_hit_rate",
            metric_name="pipeline.cache_hit_rate",
            threshold=50.0,  # 50% hit rate
            comparison="less_than",
            severity=AlertSeverity.MEDIUM,
            component="pipeline",
            description="Email cache hit rate is below 50%"
        )
        
        # Add notification handlers
        if self.config.get("notifications", {}).get("slack_webhook"):
            self.system_monitor.alert_manager.add_notification_handler(
                self._send_slack_notification
            )
        
        self.system_monitor.alert_manager.add_notification_handler(
            self._log_alert_notification
        )
    
    async def _pipeline_health_check(self) -> Dict[str, Any]:
        """Custom health check for the email pipeline."""
        try:
            # Check if all components are initialized and healthy
            components_healthy = all([
                self.protocol and self.protocol.status.is_connected,
                self.connector and self.connector._is_connected,
                self.email_processor is not None,
                self.attachment_processor is not None,
            ])
            
            return {
                "status": "healthy" if components_healthy else "unhealthy",
                "components_initialized": components_healthy,
                "emails_processed": self.pipeline_stats["emails_processed"],
                "error_rate": self._calculate_error_rate(),
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate."""
        total_operations = self.pipeline_stats["emails_processed"] + self.pipeline_stats["errors_handled"]
        if total_operations == 0:
            return 0.0
        return (self.pipeline_stats["errors_handled"] / total_operations) * 100
    
    async def _send_slack_notification(self, alert: Alert):
        """Send alert notification to Slack."""
        webhook_url = self.config.get("notifications", {}).get("slack_webhook")
        if not webhook_url:
            return
        
        try:
            message = {
                "text": f"🚨 Alert: {alert.title}",
                "attachments": [
                    {
                        "color": "danger" if alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL] else "warning",
                        "fields": [
                            {"title": "Component", "value": alert.component, "short": True},
                            {"title": "Severity", "value": alert.severity.value, "short": True},
                            {"title": "Metric", "value": alert.metric_name, "short": True},
                            {"title": "Value", "value": f"{alert.current_value:.2f}", "short": True},
                            {"title": "Threshold", "value": f"{alert.threshold:.2f}", "short": True},
                            {"title": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "short": True},
                        ],
                        "text": alert.description
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=message) as response:
                    if response.status == 200:
                        print(f"✅ Slack notification sent for alert: {alert.title}")
                    else:
                        print(f"❌ Failed to send Slack notification: {response.status}")
                        
        except Exception as e:
            print(f"❌ Error sending Slack notification: {e}")
    
    async def _log_alert_notification(self, alert: Alert):
        """Log alert notification."""
        severity_emoji = {
            AlertSeverity.LOW: "ℹ️",
            AlertSeverity.MEDIUM: "⚠️",
            AlertSeverity.HIGH: "🚨",
            AlertSeverity.CRITICAL: "💥"
        }
        
        emoji = severity_emoji.get(alert.severity, "🔔")
        print(f"{emoji} ALERT [{alert.severity.value.upper()}]: {alert.title}")
        print(f"   Component: {alert.component}")
        print(f"   Metric: {alert.metric_name} = {alert.current_value:.2f} (threshold: {alert.threshold:.2f})")
        print(f"   Description: {alert.description}")
        print(f"   Time: {alert.timestamp}")
        
        self.pipeline_stats["alerts_triggered"] += 1
    
    async def initialize(self):
        """Initialize all pipeline components."""
        print("🔧 Initializing production pipeline components...")
        
        # Start system monitoring
        await self.system_monitor.start_monitoring(interval=30)  # Check every 30 seconds
        print("✅ System monitoring started")
        
        # Initialize email cache
        cache_config = self.config.get("cache", {})
        self.email_cache = AsyncLRUCache(
            maxsize=cache_config.get("maxsize", 1000),
            ttl=cache_config.get("ttl", 3600)  # 1 hour TTL
        )
        print("✅ Email cache initialized")
        
        # Initialize batch processor
        batch_config = self.config.get("batch_processing", {})
        self.batch_processor = BatchProcessor(
            batch_size=batch_config.get("batch_size", 50),
            max_wait_time=batch_config.get("max_wait_time", 2.0),
            max_concurrent_batches=batch_config.get("max_concurrent", 3)
        )
        print("✅ Batch processor initialized")
        
        # Initialize protocol adapter
        self.protocol = GraphAPIAdapter("production_graph_api", self.config["graph_api"])
        await self.protocol.initialize()
        print("✅ Graph API adapter initialized")
        
        # Initialize database connector
        self.connector = PostgreSQLConnector("production_postgresql", self.config["database"])
        await self.connector.initialize()
        print("✅ PostgreSQL connector initialized")
        
        # Initialize processors
        self.email_processor = EmailProcessor("production_email_processor", self.config["email_processing"])
        self.attachment_processor = AttachmentProcessor("production_attachment_processor", self.config["attachment_processing"])
        print("✅ Email and attachment processors initialized")
        
        self.pipeline_stats["start_time"] = datetime.utcnow()
        print("🚀 Production pipeline initialization completed")
    
    async def cleanup(self):
        """Cleanup all pipeline components."""
        print("🧹 Cleaning up production pipeline...")
        
        # Stop monitoring
        await self.system_monitor.stop_monitoring()
        
        # Cleanup components
        if self.protocol:
            await self.protocol.cleanup()
        if self.connector:
            await self.connector.cleanup()
        if self.email_cache:
            await self.email_cache.clear()
        
        print("✅ Production pipeline cleanup completed")
    
    @profile_performance("email_processing_pipeline")
    async def process_emails_with_monitoring(self, max_emails: int = None) -> Dict[str, Any]:
        """
        Process emails with comprehensive monitoring and error handling.
        
        Args:
            max_emails: Maximum number of emails to process
            
        Returns:
            Processing report with detailed statistics
        """
        print(f"🚀 Starting monitored email processing (max_emails={max_emails})")
        
        try:
            processed_count = 0
            
            # Process emails with streaming and caching
            async for email_batch in self.protocol.fetch_emails_stream(
                folder_filters=["Inbox"],
                batch_size=self.config.get("batch_processing", {}).get("batch_size", 25),
                limit=max_emails,
                include_attachments=True
            ):
                if not email_batch:
                    break
                
                # Process batch with error handling
                await self._process_batch_with_monitoring(email_batch)
                processed_count += len(email_batch)
                
                # Update metrics
                self._update_pipeline_metrics()
                
                # Check alerts
                await self.system_monitor.alert_manager.check_alerts()
                
                if max_emails and processed_count >= max_emails:
                    break
            
            return await self._generate_comprehensive_report()
            
        except Exception as e:
            print(f"❌ Critical error in pipeline: {e}")
            self.pipeline_stats["errors_handled"] += 1
            raise
    
    async def _process_batch_with_monitoring(self, emails: List[EmailMessage]):
        """Process a batch of emails with monitoring and caching."""
        for email in emails:
            try:
                # Check cache first
                cache_key = f"processed_email_{email.id}"
                cached_result = await self.email_cache.get(cache_key)
                
                if cached_result:
                    self.pipeline_stats["cache_hits"] += 1
                    print(f"📋 Cache hit for email {email.id}")
                    continue
                
                self.pipeline_stats["cache_misses"] += 1
                
                # Process email
                processed_email = await self._process_single_email(email)
                
                if processed_email:
                    # Store in database
                    await self.connector.store_email(processed_email)
                    
                    # Cache the result
                    await self.email_cache.put(cache_key, processed_email)
                    
                    self.pipeline_stats["emails_processed"] += 1
                    
                    # Record metrics
                    self.system_monitor.metrics.increment_counter("pipeline.emails_processed")
                
            except Exception as e:
                print(f"❌ Error processing email {email.id}: {e}")
                self.pipeline_stats["errors_handled"] += 1
                self.system_monitor.metrics.increment_counter("pipeline.errors")
    
    async def _process_single_email(self, email: EmailMessage) -> Optional[EmailMessage]:
        """Process a single email through the pipeline."""
        # Email processing
        email_result = ProcessingResult(
            operation_id=f"prod_email_{email.id}",
            correlation_id="production_pipeline",
            status=ProcessingStatus.PROCESSING,
            start_time=datetime.utcnow(),
            total_items=1,
        )
        
        processed_email_result = await self.email_processor._process_data(email, email_result)
        
        if processed_email_result.successful_items == 0:
            return None
        
        processed_email = processed_email_result.results[0]
        
        # Attachment processing
        if processed_email.has_attachments:
            attachment_result = ProcessingResult(
                operation_id=f"prod_attachment_{email.id}",
                correlation_id="production_pipeline",
                status=ProcessingStatus.PROCESSING,
                start_time=datetime.utcnow(),
                total_items=1,
            )
            
            processed_attachment_result = await self.attachment_processor._process_data(
                processed_email, attachment_result
            )
            
            if processed_attachment_result.successful_items > 0:
                processed_email = processed_attachment_result.results[0]
        
        return processed_email
    
    def _update_pipeline_metrics(self):
        """Update pipeline metrics for monitoring."""
        # Calculate rates
        error_rate = self._calculate_error_rate()
        cache_stats = self.email_cache.get_stats()
        
        # Update metrics
        self.system_monitor.metrics.set_gauge("pipeline.error_rate", error_rate)
        self.system_monitor.metrics.set_gauge("pipeline.cache_hit_rate", cache_stats["hit_rate"])
        self.system_monitor.metrics.set_gauge("pipeline.cache_size", cache_stats["size"])
    
    async def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive processing report."""
        # Get system status
        system_status = self.system_monitor.get_status()
        
        # Get performance stats
        performance_stats = self.performance_profiler.get_all_stats()
        
        # Get cache stats
        cache_stats = self.email_cache.get_stats()
        
        # Calculate runtime
        runtime = (datetime.utcnow() - self.pipeline_stats["start_time"]).total_seconds()
        
        report = {
            "pipeline_summary": {
                "emails_processed": self.pipeline_stats["emails_processed"],
                "errors_handled": self.pipeline_stats["errors_handled"],
                "error_rate": self._calculate_error_rate(),
                "alerts_triggered": self.pipeline_stats["alerts_triggered"],
                "runtime_seconds": runtime,
                "processing_rate": self.pipeline_stats["emails_processed"] / runtime if runtime > 0 else 0,
            },
            "cache_performance": cache_stats,
            "system_health": system_status,
            "performance_metrics": performance_stats,
            "active_alerts": len(self.system_monitor.alert_manager.get_active_alerts()),
            "recommendations": self._generate_recommendations(),
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on current metrics."""
        recommendations = []
        
        # Cache performance recommendations
        cache_stats = self.email_cache.get_stats()
        if cache_stats["hit_rate"] < 50:
            recommendations.append("Consider increasing cache size or TTL to improve hit rate")
        
        # Error rate recommendations
        error_rate = self._calculate_error_rate()
        if error_rate > 5:
            recommendations.append("High error rate detected - review error logs and consider retry logic")
        
        # Performance recommendations
        if self.pipeline_stats["emails_processed"] > 0:
            runtime = (datetime.utcnow() - self.pipeline_stats["start_time"]).total_seconds()
            rate = self.pipeline_stats["emails_processed"] / runtime if runtime > 0 else 0
            
            if rate < 10:  # Less than 10 emails per second
                recommendations.append("Consider increasing batch size or concurrent processing")
        
        return recommendations


async def main():
    """Main function demonstrating the complete production pipeline."""
    print("🚀 Starting Complete Production Pipeline Example")
    print("=" * 60)
    
    # Comprehensive configuration
    config = {
        "graph_api": {
            "client_id": os.getenv("GRAPH_CLIENT_ID", "your_client_id_here"),
            "client_secret": os.getenv("GRAPH_CLIENT_SECRET", "your_client_secret_here"),
            "tenant_id": os.getenv("GRAPH_TENANT_ID", "your_tenant_id_here"),
            "rate_limit": 100,
        },
        "database": {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "outlook_ingestor"),
            "username": os.getenv("DB_USER", "ingestor_user"),
            "password": os.getenv("DB_PASSWORD", "your_db_password"),
            "ssl_mode": "prefer",
            "enable_connection_pooling": True,
            "pool_size": 15,
        },
        "email_processing": {
            "normalize_content": True,
            "extract_links": True,
            "validate_addresses": True,
            "html_to_text": True,
            "remove_duplicates": True,
            "duplicate_cache_size": 10000,
        },
        "attachment_processing": {
            "max_attachment_size": 10 * 1024 * 1024,
            "extract_metadata": True,
            "calculate_hashes": True,
        },
        "batch_processing": {
            "batch_size": 30,
            "max_wait_time": 2.0,
            "max_concurrent": 3,
        },
        "cache": {
            "maxsize": 2000,
            "ttl": 3600,  # 1 hour
        },
        "notifications": {
            "slack_webhook": os.getenv("SLACK_WEBHOOK_URL"),  # Optional
        }
    }
    
    # Initialize and run pipeline
    pipeline = ProductionEmailPipeline(config)
    
    try:
        await pipeline.initialize()
        
        # Run the complete pipeline
        report = await pipeline.process_emails_with_monitoring(max_emails=50)
        
        # Display comprehensive report
        print("\n📊 Comprehensive Pipeline Report:")
        print("=" * 50)
        
        print("\nPipeline Summary:")
        for key, value in report["pipeline_summary"].items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        print("\nCache Performance:")
        for key, value in report["cache_performance"].items():
            print(f"  {key}: {value}")
        
        print("\nSystem Health:")
        print(f"  Overall Status: {report['system_health']['health']['status']}")
        print(f"  Active Alerts: {report['active_alerts']}")
        
        if report["recommendations"]:
            print("\nRecommendations:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")
        
        print("\n🎉 Production pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await pipeline.cleanup()


if __name__ == "__main__":
    print("Evolvishub Outlook Ingestor - Complete Production Pipeline")
    print("For more examples, see: https://github.com/evolvisai/metcal")
    print()
    
    asyncio.run(main())
