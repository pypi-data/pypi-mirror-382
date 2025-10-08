#!/usr/bin/env python3
"""
Batch Processing with PostgreSQL Storage

This example demonstrates how to set up batch email processing with PostgreSQL storage
using the Evolvishub Outlook Ingestor. It shows how to efficiently process large volumes
of emails and store them in a PostgreSQL database with proper error handling and monitoring.

Requirements:
- PostgreSQL database server
- Database credentials and connection details
- Microsoft Graph API credentials (or other email source)

Usage:
    python batch_processing_postgresql.py
"""

import asyncio
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

from evolvishub_outlook_ingestor.protocols.microsoft_graph import GraphAPIAdapter
from evolvishub_outlook_ingestor.connectors.postgresql_connector import PostgreSQLConnector
from evolvishub_outlook_ingestor.processors.email_processor import EmailProcessor
from evolvishub_outlook_ingestor.processors.attachment_processor import AttachmentProcessor
from evolvishub_outlook_ingestor.core.data_models import EmailMessage, ProcessingResult, ProcessingStatus
from evolvishub_outlook_ingestor.utils.security import SecureCredentialManager, CredentialMasker


class BatchEmailProcessor:
    """
    A comprehensive batch email processor that demonstrates production-ready
    email ingestion, processing, and storage patterns.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the batch processor with configuration.
        
        Args:
            config: Configuration dictionary containing database, API, and processing settings
        """
        self.config = config
        self.protocol = None
        self.connector = None
        self.email_processor = None
        self.attachment_processor = None
        self.stats = {
            "emails_fetched": 0,
            "emails_processed": 0,
            "emails_stored": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None,
        }
    
    async def initialize(self):
        """Initialize all components."""
        print("🔧 Initializing batch processor components...")
        
        # Initialize protocol adapter
        self.protocol = GraphAPIAdapter("batch_graph_api", self.config["graph_api"])
        await self.protocol.initialize()
        print("✅ Graph API adapter initialized")
        
        # Initialize database connector
        self.connector = PostgreSQLConnector("batch_postgresql", self.config["database"])
        await self.connector.initialize()
        print("✅ PostgreSQL connector initialized")
        
        # Initialize processors
        self.email_processor = EmailProcessor("batch_email_processor", self.config["email_processing"])
        self.attachment_processor = AttachmentProcessor("batch_attachment_processor", self.config["attachment_processing"])
        print("✅ Email and attachment processors initialized")
    
    async def cleanup(self):
        """Cleanup all components."""
        print("🧹 Cleaning up components...")
        
        if self.protocol:
            await self.protocol.cleanup()
        if self.connector:
            await self.connector.cleanup()
        
        print("✅ Cleanup completed")
    
    async def process_emails_batch(self, batch_size: int = 50, max_emails: int = None) -> Dict[str, Any]:
        """
        Process emails in batches for optimal performance.
        
        Args:
            batch_size: Number of emails to process in each batch
            max_emails: Maximum number of emails to process (None for no limit)
            
        Returns:
            Dictionary containing processing statistics
        """
        self.stats["start_time"] = datetime.utcnow()
        print(f"🚀 Starting batch processing (batch_size={batch_size}, max_emails={max_emails})")
        
        try:
            # Fetch emails in streaming mode for memory efficiency
            processed_count = 0
            
            async for email_batch in self.protocol.fetch_emails_stream(
                folder_filters=["Inbox"],
                batch_size=batch_size,
                limit=max_emails,
                include_attachments=True
            ):
                if not email_batch:
                    break
                
                self.stats["emails_fetched"] += len(email_batch)
                print(f"📧 Processing batch of {len(email_batch)} emails...")
                
                # Process the batch
                processed_batch = await self._process_email_batch(email_batch)
                
                # Store the batch in database
                if processed_batch:
                    await self._store_email_batch(processed_batch)
                
                processed_count += len(email_batch)
                
                # Progress update
                if processed_count % (batch_size * 5) == 0:  # Every 5 batches
                    await self._print_progress()
                
                # Check if we've reached the limit
                if max_emails and processed_count >= max_emails:
                    break
            
            self.stats["end_time"] = datetime.utcnow()
            return self._generate_final_report()
            
        except Exception as e:
            print(f"❌ Error during batch processing: {e}")
            self.stats["errors"] += 1
            raise
    
    async def _process_email_batch(self, emails: List[EmailMessage]) -> List[EmailMessage]:
        """Process a batch of emails through the processing pipeline."""
        processed_emails = []
        
        for email in emails:
            try:
                # Step 1: Process email content
                email_result = ProcessingResult(
                    operation_id=f"batch_email_{email.id}",
                    correlation_id="batch_processing",
                    status=ProcessingStatus.PROCESSING,
                    start_time=datetime.utcnow(),
                    total_items=1,
                )
                
                processed_email_result = await self.email_processor._process_data(email, email_result)
                
                if processed_email_result.successful_items > 0:
                    processed_email = processed_email_result.results[0]
                    
                    # Step 2: Process attachments if present
                    if processed_email.has_attachments:
                        attachment_result = ProcessingResult(
                            operation_id=f"batch_attachment_{email.id}",
                            correlation_id="batch_processing",
                            status=ProcessingStatus.PROCESSING,
                            start_time=datetime.utcnow(),
                            total_items=1,
                        )
                        
                        processed_attachment_result = await self.attachment_processor._process_data(
                            processed_email, attachment_result
                        )
                        
                        if processed_attachment_result.successful_items > 0:
                            processed_email = processed_attachment_result.results[0]
                    
                    processed_emails.append(processed_email)
                    self.stats["emails_processed"] += 1
                else:
                    print(f"⚠️  Failed to process email {email.id}: {processed_email_result.errors}")
                    self.stats["errors"] += 1
                    
            except Exception as e:
                print(f"❌ Error processing email {email.id}: {e}")
                self.stats["errors"] += 1
        
        return processed_emails
    
    async def _store_email_batch(self, emails: List[EmailMessage]):
        """Store a batch of processed emails in the database."""
        try:
            # Use database transaction for batch consistency
            async with self.connector.transaction() as tx:
                stored_ids = await self.connector.store_emails_batch(emails, transaction=tx)
                self.stats["emails_stored"] += len(stored_ids)
                print(f"💾 Stored {len(stored_ids)} emails in database")
                
        except Exception as e:
            print(f"❌ Error storing email batch: {e}")
            self.stats["errors"] += 1
            raise
    
    async def _print_progress(self):
        """Print current processing progress."""
        elapsed = (datetime.utcnow() - self.stats["start_time"]).total_seconds()
        rate = self.stats["emails_processed"] / elapsed if elapsed > 0 else 0
        
        print(f"📊 Progress Update:")
        print(f"   Fetched: {self.stats['emails_fetched']}")
        print(f"   Processed: {self.stats['emails_processed']}")
        print(f"   Stored: {self.stats['emails_stored']}")
        print(f"   Errors: {self.stats['errors']}")
        print(f"   Rate: {rate:.2f} emails/second")
        print(f"   Elapsed: {elapsed:.1f} seconds")
    
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate final processing report."""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        report = {
            "summary": {
                "emails_fetched": self.stats["emails_fetched"],
                "emails_processed": self.stats["emails_processed"],
                "emails_stored": self.stats["emails_stored"],
                "errors": self.stats["errors"],
                "success_rate": (self.stats["emails_processed"] / self.stats["emails_fetched"] * 100) if self.stats["emails_fetched"] > 0 else 0,
            },
            "performance": {
                "duration_seconds": duration,
                "emails_per_second": self.stats["emails_processed"] / duration if duration > 0 else 0,
                "storage_rate": self.stats["emails_stored"] / duration if duration > 0 else 0,
            },
            "timestamps": {
                "start_time": self.stats["start_time"].isoformat(),
                "end_time": self.stats["end_time"].isoformat(),
            }
        }
        
        return report


async def main():
    """
    Main function demonstrating batch processing with PostgreSQL storage.
    """
    print("🚀 Starting Batch Processing with PostgreSQL Example")
    print("=" * 60)
    
    # Configuration
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
            "pool_size": 10,
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
            "max_attachment_size": 10 * 1024 * 1024,  # 10MB
            "extract_metadata": True,
            "calculate_hashes": True,
            "scan_for_viruses": False,  # Disabled for example
        }
    }
    
    # Validate configuration
    if any(value.startswith("your_") for value in [
        config["graph_api"]["client_id"],
        config["graph_api"]["client_secret"],
        config["graph_api"]["tenant_id"],
        config["database"]["password"]
    ]):
        print("❌ Error: Please configure your credentials")
        print("   Set environment variables or update the config dictionary")
        return
    
    # Mask sensitive configuration for logging
    masked_config = CredentialMasker.mask_dict(config)
    print("📋 Configuration:")
    for section, settings in masked_config.items():
        print(f"   {section}:")
        for key, value in settings.items():
            print(f"     {key}: {value}")
    
    # Initialize and run batch processor
    processor = BatchEmailProcessor(config)
    
    try:
        await processor.initialize()
        
        # Run batch processing
        print("\n🔄 Starting batch processing...")
        report = await processor.process_emails_batch(
            batch_size=25,      # Process 25 emails per batch
            max_emails=100      # Limit to 100 emails for this example
        )
        
        # Display final report
        print("\n📊 Final Processing Report:")
        print("=" * 40)
        
        print("Summary:")
        for key, value in report["summary"].items():
            print(f"  {key}: {value}")
        
        print("\nPerformance:")
        for key, value in report["performance"].items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
        
        print(f"\nProcessing completed successfully!")
        
        # Demonstrate database querying
        await demonstrate_database_queries(processor.connector)
        
    except Exception as e:
        print(f"❌ Error during batch processing: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await processor.cleanup()


async def demonstrate_database_queries(connector):
    """Demonstrate various database query operations."""
    print("\n🔍 Database Query Examples:")
    print("-" * 30)
    
    try:
        # Search for emails by subject
        search_results = await connector.search_emails({
            "subject": "test",
            "limit": 5
        })
        print(f"Found {len(search_results)} emails with 'test' in subject")
        
        # Search by date range
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_emails = await connector.search_emails({
            "date_from": yesterday,
            "limit": 10
        })
        print(f"Found {len(recent_emails)} emails from the last 24 hours")
        
        # Get connector status
        status = connector.get_status()
        print(f"Database connector status: {status['is_connected']}")
        print(f"Total operations: {status['operation_count']}")
        
    except Exception as e:
        print(f"Error during database queries: {e}")


if __name__ == "__main__":
    print("Evolvishub Outlook Ingestor - Batch Processing Example")
    print("For more examples, see: https://github.com/evolvisai/metcal")
    print()
    
    asyncio.run(main())
