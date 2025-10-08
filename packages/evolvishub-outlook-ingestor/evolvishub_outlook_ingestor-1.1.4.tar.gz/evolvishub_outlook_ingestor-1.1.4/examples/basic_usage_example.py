#!/usr/bin/env python3
"""
Basic usage example for Evolvishub Outlook Ingestor.

This example demonstrates the fundamental usage patterns of the library:
- Configuration setup
- Basic email ingestion
- Error handling
- Progress monitoring

Run this example with:
    python examples/basic_usage_example.py
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the library to the path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from evolvishub_outlook_ingestor import OutlookIngestor
from evolvishub_outlook_ingestor.core.config import Settings, get_settings
from evolvishub_outlook_ingestor.core.data_models import BatchProcessingConfig
from evolvishub_outlook_ingestor.core.exceptions import OutlookIngestorError
from evolvishub_outlook_ingestor.core.logging import setup_logging, set_correlation_id


async def basic_example():
    """Basic email ingestion example."""
    print("🚀 Basic Outlook Ingestor Example")
    print("=" * 50)
    
    # Setup logging
    setup_logging(
        log_level="INFO",
        log_format="text",
        enable_console=True,
        enable_correlation_id=True,
    )
    
    # Set correlation ID for this operation
    correlation_id = set_correlation_id("basic_example_001")
    print(f"📋 Correlation ID: {correlation_id}")
    
    try:
        # Load configuration
        print("\n📁 Loading configuration...")
        settings = get_settings()
        
        # Override some settings for the example
        settings.environment = "development"
        settings.debug = True
        
        # Configure database (using mock settings for example)
        settings.database.host = "localhost"
        settings.database.port = 5432
        settings.database.database = "outlook_example"
        settings.database.username = "example_user"
        
        # Configure processing
        settings.processing.batch_size = 100
        settings.processing.max_workers = 2
        settings.processing.timeout_seconds = 60
        
        print(f"✅ Configuration loaded for environment: {settings.environment}")
        
        # Initialize ingestor
        print("\n🔧 Initializing Outlook Ingestor...")
        
        # Note: In a real implementation, you would provide actual protocol adapters,
        # database connectors, and processors. For this example, we'll show the structure.
        ingestor = OutlookIngestor(
            settings=settings,
            # protocol_adapters={"graph_api": GraphAPIAdapter(...)},
            # database_connectors={"postgresql": PostgreSQLConnector(...)},
            # processors={"email": EmailProcessor(...)},
        )
        
        print("✅ Ingestor initialized successfully")
        
        # Example 1: Basic email processing
        print("\n📧 Example 1: Basic Email Processing")
        print("-" * 40)
        
        try:
            # This would normally process real emails
            # For the example, we'll simulate the call
            print("📥 Processing emails from Inbox...")
            
            # Simulated processing result
            from evolvishub_outlook_ingestor.core.data_models import ProcessingResult, ProcessingStatus
            from uuid import uuid4
            
            result = ProcessingResult(
                operation_id=uuid4(),
                correlation_id=correlation_id,
                status=ProcessingStatus.COMPLETED,
                start_time=datetime.utcnow() - timedelta(seconds=30),
                end_time=datetime.utcnow(),
                total_items=150,
                successful_items=145,
                failed_items=5,
                skipped_items=0,
            )
            result.calculate_duration()
            result.calculate_rate()
            
            print(f"✅ Processing completed!")
            print(f"   📊 Total emails: {result.total_items}")
            print(f"   ✅ Successful: {result.successful_items}")
            print(f"   ❌ Failed: {result.failed_items}")
            print(f"   ⏱️  Duration: {result.duration_seconds:.2f} seconds")
            print(f"   🚀 Rate: {result.items_per_second:.2f} emails/second")
            
        except OutlookIngestorError as e:
            print(f"❌ Email processing failed: {e}")
            print(f"   Error code: {e.error_code}")
            if e.context:
                print(f"   Context: {e.context}")
        
        # Example 2: Batch processing with progress tracking
        print("\n📦 Example 2: Batch Processing")
        print("-" * 40)
        
        def progress_callback(processed: int, total: int, rate: float):
            """Progress callback function."""
            percentage = (processed / total) * 100 if total > 0 else 0
            print(f"   📈 Progress: {processed}/{total} ({percentage:.1f}%) - {rate:.2f} emails/sec")
        
        batch_config = BatchProcessingConfig(
            batch_size=50,
            max_workers=4,
            timeout_seconds=120,
            enable_progress_tracking=True,
            progress_callback=progress_callback,
        )
        
        print("📥 Processing emails in batches...")
        print("   Batch size: 50 emails")
        print("   Max workers: 4")
        
        # Simulate batch processing
        total_emails = 200
        batch_size = 50
        
        for i in range(0, total_emails, batch_size):
            processed = min(i + batch_size, total_emails)
            rate = 15.5  # Simulated rate
            progress_callback(processed, total_emails, rate)
            await asyncio.sleep(0.1)  # Simulate processing time
        
        print("✅ Batch processing completed!")
        
        # Example 3: Error handling and retry
        print("\n🔄 Example 3: Error Handling and Retry")
        print("-" * 40)
        
        print("🔧 Demonstrating retry mechanism...")
        
        # Simulate a function that fails a few times then succeeds
        attempt_count = 0
        
        async def flaky_operation():
            nonlocal attempt_count
            attempt_count += 1
            
            if attempt_count < 3:
                print(f"   ❌ Attempt {attempt_count} failed (simulated)")
                raise ConnectionError("Simulated connection error")
            else:
                print(f"   ✅ Attempt {attempt_count} succeeded!")
                return "Success"
        
        # Apply retry logic (simplified for example)
        max_retries = 3
        for retry in range(max_retries):
            try:
                result = await flaky_operation()
                print(f"✅ Operation succeeded: {result}")
                break
            except Exception as e:
                if retry < max_retries - 1:
                    print(f"   🔄 Retrying in 1 second...")
                    await asyncio.sleep(1)
                else:
                    print(f"❌ Operation failed after {max_retries} attempts: {e}")
        
        # Example 4: Configuration examples
        print("\n⚙️  Example 4: Configuration Examples")
        print("-" * 40)
        
        print("📋 Current configuration:")
        print(f"   App: {settings.app_name} v{settings.app_version}")
        print(f"   Environment: {settings.environment}")
        print(f"   Debug mode: {settings.debug}")
        print(f"   Database host: {settings.database.host}")
        print(f"   Database port: {settings.database.port}")
        print(f"   Batch size: {settings.processing.batch_size}")
        print(f"   Max workers: {settings.processing.max_workers}")
        print(f"   Log level: {settings.logging.level}")
        print(f"   Log format: {settings.logging.format}")
        
        # Show how to override configuration
        print("\n🔧 Configuration override example:")
        settings.processing.batch_size = 500
        settings.processing.max_workers = 8
        print(f"   Updated batch size: {settings.processing.batch_size}")
        print(f"   Updated max workers: {settings.processing.max_workers}")
        
        print("\n🎉 All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Example failed with error: {e}")
        logging.exception("Example execution failed")
        return 1
    
    return 0


async def main():
    """Main function."""
    try:
        exit_code = await basic_example()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Example interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logging.exception("Unexpected error in main")
        sys.exit(1)


if __name__ == "__main__":
    # Run the example
    print("Starting Evolvishub Outlook Ingestor Basic Example...")
    asyncio.run(main())
