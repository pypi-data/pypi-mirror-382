#!/usr/bin/env python3
"""
Large-Scale Attachment Processing Example for Evolvishub Outlook Ingestor.

This example demonstrates high-performance attachment processing for enterprise
environments with large volumes of email attachments, featuring:

- Batch processing with concurrent workers
- Multi-tier storage strategy (hot/warm/cold)
- Automatic lifecycle management
- Performance monitoring and optimization
- Deduplication across large datasets

Requirements:
    pip install evolvishub-outlook-ingestor[all]
"""

import asyncio
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

from evolvishub_outlook_ingestor.protocols.microsoft_graph import GraphAPIAdapter
from evolvishub_outlook_ingestor.connectors.postgresql_connector import PostgreSQLConnector
from evolvishub_outlook_ingestor.connectors.minio_connector import MinIOConnector
from evolvishub_outlook_ingestor.connectors.aws_s3_connector import AWSS3Connector
from evolvishub_outlook_ingestor.processors.enhanced_attachment_processor import (
    EnhancedAttachmentProcessor,
    StorageStrategy,
    CompressionType
)
from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.utils.monitoring import MetricsCollector, HealthChecker


class LargeScaleAttachmentProcessor:
    """
    Large-scale attachment processor with enterprise features.
    
    Features:
    - Multi-tier storage (hot/warm/cold)
    - Concurrent processing with worker pools
    - Performance monitoring and metrics
    - Automatic lifecycle management
    - Deduplication and compression
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize large-scale processor."""
        self.config = config
        self.storage_backends = {}
        self.processors = {}
        self.metrics = MetricsCollector("large_scale_processor")
        self.health_checker = HealthChecker("attachment_processor")
        
        # Performance settings
        self.max_concurrent_workers = config.get("max_concurrent_workers", 10)
        self.batch_size = config.get("batch_size", 50)
        self.processing_timeout = config.get("processing_timeout", 300)  # 5 minutes
        
        # Storage tiers
        self.hot_storage_threshold = config.get("hot_storage_threshold", 30)  # days
        self.warm_storage_threshold = config.get("warm_storage_threshold", 90)  # days
        self.cold_storage_threshold = config.get("cold_storage_threshold", 365)  # days
    
    async def initialize(self):
        """Initialize all components."""
        print("🚀 Initializing large-scale attachment processor...")
        
        # Setup storage tiers
        await self._setup_storage_tiers()
        
        # Setup processors for different tiers
        await self._setup_processors()
        
        # Initialize monitoring
        await self._setup_monitoring()
        
        print("✅ Large-scale processor initialized")
    
    async def _setup_storage_tiers(self):
        """Setup multi-tier storage architecture."""
        print("🗄️  Setting up storage tiers...")
        
        # Hot tier: MinIO for frequently accessed files
        hot_config = {
            "endpoint_url": os.getenv("MINIO_HOT_ENDPOINT", "localhost:9000"),
            "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            "bucket_name": "attachments-hot",
            "use_ssl": False,
        }
        
        hot_storage = MinIOConnector("hot_tier", hot_config)
        await hot_storage.initialize()
        self.storage_backends["hot"] = hot_storage
        print("   ✅ Hot tier (MinIO) initialized")
        
        # Warm tier: AWS S3 Standard-IA for less frequently accessed files
        if os.getenv("AWS_ACCESS_KEY_ID"):
            warm_config = {
                "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "bucket_name": "attachments-warm",
                "region": os.getenv("AWS_REGION", "us-east-1"),
            }
            
            warm_storage = AWSS3Connector("warm_tier", warm_config)
            await warm_storage.initialize()
            
            # Set lifecycle policy for automatic transition to IA
            await warm_storage.set_lifecycle_policy(transition_days=30)
            
            self.storage_backends["warm"] = warm_storage
            print("   ✅ Warm tier (AWS S3 IA) initialized")
        
        # Cold tier: AWS S3 Glacier for archival
        if os.getenv("AWS_ACCESS_KEY_ID"):
            cold_config = {
                "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                "bucket_name": "attachments-cold",
                "region": os.getenv("AWS_REGION", "us-east-1"),
            }
            
            cold_storage = AWSS3Connector("cold_tier", cold_config)
            await cold_storage.initialize()
            self.storage_backends["cold"] = cold_storage
            print("   ✅ Cold tier (AWS S3 Glacier) initialized")
    
    async def _setup_processors(self):
        """Setup processors for different storage tiers."""
        print("⚙️  Setting up tier-specific processors...")
        
        # Hot tier processor (fast access, minimal compression)
        hot_config = {
            "storage_strategy": "hybrid",
            "size_threshold": 512 * 1024,  # 512KB
            "enable_compression": False,  # Fast access priority
            "enable_deduplication": True,
            "default_storage_backend": "hot",
            "storage_rules": [
                {
                    "name": "recent_large_files",
                    "condition": "size > 512*1024",
                    "strategy": "storage_only",
                    "storage_backend": "hot",
                }
            ]
        }
        
        hot_processor = EnhancedAttachmentProcessor("hot_processor", hot_config)
        await hot_processor.add_storage_backend("hot", self.storage_backends["hot"])
        self.processors["hot"] = hot_processor
        
        # Warm tier processor (balanced performance/storage)
        if "warm" in self.storage_backends:
            warm_config = {
                "storage_strategy": "storage_only",
                "enable_compression": True,
                "enable_deduplication": True,
                "default_storage_backend": "warm",
                "storage_rules": [
                    {
                        "name": "warm_files",
                        "condition": "size > 1024*1024",
                        "strategy": "storage_only",
                        "storage_backend": "warm",
                        "compress": True,
                    }
                ]
            }
            
            warm_processor = EnhancedAttachmentProcessor("warm_processor", warm_config)
            await warm_processor.add_storage_backend("warm", self.storage_backends["warm"])
            self.processors["warm"] = warm_processor
        
        # Cold tier processor (maximum compression)
        if "cold" in self.storage_backends:
            cold_config = {
                "storage_strategy": "storage_only",
                "enable_compression": True,
                "enable_deduplication": True,
                "default_storage_backend": "cold",
                "storage_rules": [
                    {
                        "name": "archive_files",
                        "condition": "True",  # All files
                        "strategy": "storage_only",
                        "storage_backend": "cold",
                        "compress": True,
                        "compression_type": "gzip"
                    }
                ]
            }
            
            cold_processor = EnhancedAttachmentProcessor("cold_processor", cold_config)
            await cold_processor.add_storage_backend("cold", self.storage_backends["cold"])
            self.processors["cold"] = cold_processor
        
        print(f"   ✅ {len(self.processors)} tier processors configured")
    
    async def _setup_monitoring(self):
        """Setup monitoring and health checks."""
        print("📊 Setting up monitoring...")
        
        # Add health checks for each storage backend
        for name, backend in self.storage_backends.items():
            self.health_checker.add_check(
                f"storage_{name}",
                lambda b=backend: b.get_status()["is_connected"]
            )
        
        # Add processor health checks
        for name, processor in self.processors.items():
            self.health_checker.add_check(
                f"processor_{name}",
                lambda p=processor: len(p.storage_backends) > 0
            )
        
        print("   ✅ Monitoring configured")
    
    def _determine_storage_tier(self, email: EmailMessage) -> str:
        """
        Determine appropriate storage tier based on email age and characteristics.
        
        Args:
            email: Email message to analyze
            
        Returns:
            Storage tier name ('hot', 'warm', or 'cold')
        """
        # Calculate email age
        email_age = (datetime.utcnow() - email.received_date).days
        
        # Determine tier based on age and importance
        if email_age <= self.hot_storage_threshold:
            return "hot"
        elif email_age <= self.warm_storage_threshold and "warm" in self.processors:
            return "warm"
        elif "cold" in self.processors:
            return "cold"
        else:
            # Fallback to available tier
            return list(self.processors.keys())[0]
    
    async def process_email_batch(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """
        Process a batch of emails with attachments.
        
        Args:
            emails: List of emails to process
            
        Returns:
            Processing statistics
        """
        start_time = time.time()
        
        # Group emails by storage tier
        tier_groups = {"hot": [], "warm": [], "cold": []}
        
        for email in emails:
            if email.has_attachments:
                tier = self._determine_storage_tier(email)
                tier_groups[tier].append(email)
        
        # Process each tier concurrently
        tasks = []
        for tier, tier_emails in tier_groups.items():
            if tier_emails and tier in self.processors:
                task = self._process_tier_batch(tier, tier_emails)
                tasks.append(task)
        
        # Wait for all tiers to complete
        tier_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        total_processed = 0
        total_attachments = 0
        total_size_saved = 0
        errors = []
        
        for result in tier_results:
            if isinstance(result, Exception):
                errors.append(str(result))
            else:
                total_processed += result["processed_count"]
                total_attachments += result["attachment_count"]
                total_size_saved += result["size_saved"]
        
        processing_time = time.time() - start_time
        
        # Update metrics
        self.metrics.increment_counter("emails_processed", len(emails))
        self.metrics.increment_counter("attachments_processed", total_attachments)
        self.metrics.record_gauge("processing_time_seconds", processing_time)
        self.metrics.record_gauge("size_saved_bytes", total_size_saved)
        
        return {
            "emails_processed": len(emails),
            "attachments_processed": total_attachments,
            "total_processed": total_processed,
            "size_saved_bytes": total_size_saved,
            "processing_time_seconds": processing_time,
            "throughput_emails_per_second": len(emails) / processing_time,
            "errors": errors,
            "tier_distribution": {
                tier: len(emails) for tier, emails in tier_groups.items() if emails
            }
        }
    
    async def _process_tier_batch(self, tier: str, emails: List[EmailMessage]) -> Dict[str, Any]:
        """Process a batch of emails for a specific storage tier."""
        processor = self.processors[tier]
        
        processed_count = 0
        attachment_count = 0
        size_saved = 0
        
        # Process emails concurrently within the tier
        semaphore = asyncio.Semaphore(self.max_concurrent_workers)
        
        async def process_single_email(email):
            async with semaphore:
                try:
                    result = await processor.process(email)
                    if result.status.value == "success":
                        metadata = result.metadata
                        return {
                            "processed": metadata["processed_count"],
                            "attachments": metadata["attachment_count"],
                            "size_saved": sum(
                                info.get("original_size", 0) - info.get("stored_size", 0)
                                for info in metadata.get("storage_infos", [])
                            )
                        }
                except Exception as e:
                    print(f"Error processing email {email.id}: {e}")
                    return {"processed": 0, "attachments": 0, "size_saved": 0}
        
        # Process all emails in the tier
        tasks = [process_single_email(email) for email in emails]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate tier results
        for result in results:
            if isinstance(result, dict):
                processed_count += result["processed"]
                attachment_count += result["attachments"]
                size_saved += result["size_saved"]
        
        return {
            "tier": tier,
            "processed_count": processed_count,
            "attachment_count": attachment_count,
            "size_saved": size_saved
        }
    
    async def run_lifecycle_management(self):
        """Run lifecycle management to move files between tiers."""
        print("🔄 Running lifecycle management...")
        
        # This would typically query the database for files to migrate
        # For demo purposes, we'll just show the concept
        
        migrations = {
            "hot_to_warm": 0,
            "warm_to_cold": 0,
        }
        
        # Move files from hot to warm tier (older than threshold)
        if "warm" in self.storage_backends:
            # Query for files older than hot_storage_threshold
            # Move them to warm tier
            migrations["hot_to_warm"] = 0  # Would be actual count
        
        # Move files from warm to cold tier
        if "cold" in self.storage_backends:
            # Query for files older than warm_storage_threshold
            # Move them to cold tier
            migrations["warm_to_cold"] = 0  # Would be actual count
        
        print(f"   📦 Lifecycle migrations: {migrations}")
        return migrations
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        # Get metrics from all components
        metrics = self.metrics.get_all_metrics()
        health_status = await self.health_checker.check_all()
        
        # Get storage backend statistics
        storage_stats = {}
        for name, backend in self.storage_backends.items():
            try:
                if hasattr(backend, 'get_bucket_info'):
                    storage_stats[name] = await backend.get_bucket_info()
                else:
                    storage_stats[name] = backend.get_status()
            except Exception as e:
                storage_stats[name] = {"error": str(e)}
        
        # Get processor statistics
        processor_stats = {}
        for name, processor in self.processors.items():
            processor_stats[name] = processor.get_status()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "health_status": health_status,
            "storage_statistics": storage_stats,
            "processor_statistics": processor_stats,
            "configuration": {
                "max_concurrent_workers": self.max_concurrent_workers,
                "batch_size": self.batch_size,
                "storage_tiers": list(self.storage_backends.keys()),
            }
        }
    
    async def cleanup(self):
        """Cleanup all resources."""
        print("🧹 Cleaning up large-scale processor...")
        
        # Cleanup processors
        for processor in self.processors.values():
            try:
                # Processors don't have explicit cleanup, but storage backends do
                pass
            except Exception as e:
                print(f"Error cleaning up processor: {e}")
        
        # Cleanup storage backends
        for backend in self.storage_backends.values():
            try:
                await backend.cleanup()
            except Exception as e:
                print(f"Error cleaning up storage backend: {e}")
        
        print("✅ Cleanup completed")


async def main():
    """Main demonstration function."""
    print("🏭 Large-Scale Attachment Processing Demo")
    print("=" * 50)
    
    # Configuration for large-scale processing
    config = {
        "max_concurrent_workers": 20,
        "batch_size": 100,
        "processing_timeout": 600,  # 10 minutes
        "hot_storage_threshold": 7,   # 7 days
        "warm_storage_threshold": 30, # 30 days
        "cold_storage_threshold": 365, # 1 year
    }
    
    # Initialize large-scale processor
    processor = LargeScaleAttachmentProcessor(config)
    
    try:
        await processor.initialize()
        
        # Simulate processing large batches
        print("\n📊 Simulating large-scale processing...")
        
        # This would normally fetch real emails
        # For demo, we'll simulate the processing statistics
        mock_stats = {
            "emails_processed": 1000,
            "attachments_processed": 2500,
            "total_processed": 2500,
            "size_saved_bytes": 500 * 1024 * 1024,  # 500MB saved
            "processing_time_seconds": 120,
            "throughput_emails_per_second": 8.33,
            "errors": [],
            "tier_distribution": {
                "hot": 600,
                "warm": 300,
                "cold": 100
            }
        }
        
        print(f"✅ Processed {mock_stats['emails_processed']} emails")
        print(f"📎 Processed {mock_stats['attachments_processed']} attachments")
        print(f"💾 Saved {mock_stats['size_saved_bytes'] / (1024*1024):.1f} MB through compression/deduplication")
        print(f"⚡ Throughput: {mock_stats['throughput_emails_per_second']:.1f} emails/second")
        
        # Run lifecycle management
        await processor.run_lifecycle_management()
        
        # Generate performance report
        print("\n📈 Generating performance report...")
        report = await processor.get_performance_report()
        
        print("📊 Performance Report:")
        print(f"   Storage Tiers: {len(report['storage_statistics'])}")
        print(f"   Processors: {len(report['processor_statistics'])}")
        print(f"   Health Status: {report['health_status']}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await processor.cleanup()


if __name__ == "__main__":
    print("Evolvishub Outlook Ingestor - Large-Scale Attachment Processing")
    print("==============================================================")
    print()
    print("This demo shows enterprise-grade attachment processing with:")
    print("  - Multi-tier storage (hot/warm/cold)")
    print("  - Concurrent processing with worker pools")
    print("  - Performance monitoring and metrics")
    print("  - Automatic lifecycle management")
    print()
    
    asyncio.run(main())
