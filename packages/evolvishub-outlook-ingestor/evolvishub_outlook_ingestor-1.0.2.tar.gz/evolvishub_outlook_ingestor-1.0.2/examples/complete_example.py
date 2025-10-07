#!/usr/bin/env python3
"""
Complete example demonstrating Evolvishub Outlook Ingestor usage.

This example shows how to:
1. Configure the library with all components
2. Set up protocol adapters, database connectors, and processors
3. Process emails with full workflow
4. Handle errors and monitoring

Run this example with:
    python examples/complete_example.py
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the library to the path for development
sys.path.insert(0, str(Path(__file__).parent.parent))

from evolvishub_outlook_ingestor import (
    OutlookIngestor,
    Settings,
    get_settings,
    GraphAPIAdapter,
    PostgreSQLConnector,
    EmailProcessor,
    AttachmentProcessor,
)
from evolvishub_outlook_ingestor.core.logging import setup_logging, set_correlation_id


async def main():
    """Main example function."""
    print("🚀 Complete Evolvishub Outlook Ingestor Example")
    print("=" * 60)
    
    # Setup logging
    setup_logging(
        log_level="INFO",
        log_format="text",
        enable_console=True,
        enable_correlation_id=True,
    )
    
    # Set correlation ID for this operation
    correlation_id = set_correlation_id("complete_example_001")
    print(f"📋 Correlation ID: {correlation_id}")
    
    try:
        # 1. Load and configure settings
        print("\n📁 Loading configuration...")
        settings = get_settings()
        
        # Override settings for example
        settings.environment = "development"
        settings.debug = True
        
        # Configure database
        settings.database.host = "localhost"
        settings.database.port = 5432
        settings.database.database = "outlook_example"
        settings.database.username = "example_user"
        settings.database.password = "example_password"
        
        # Configure protocols
        settings.protocols = {
            "graph_api": {
                "client_id": "your-client-id",
                "client_secret": "your-client-secret", 
                "tenant_id": "your-tenant-id",
                "rate_limit": 100,
                "timeout": 60,
            },
            "exchange": {
                "server": "outlook.office365.com",
                "username": "your-email@company.com",
                "password": "your-password",
                "timeout": 60,
            },
            "imap": {
                "server": "outlook.office365.com",
                "port": 993,
                "username": "your-email@company.com",
                "password": "your-password",
                "use_ssl": True,
            }
        }
        
        # Configure processing
        settings.processing.batch_size = 100
        settings.processing.max_workers = 4
        settings.processing.timeout_seconds = 300
        
        # Configure email processing
        settings.email.extract_attachments = True
        settings.email.max_attachment_size = 50 * 1024 * 1024  # 50MB
        
        print(f"✅ Configuration loaded for environment: {settings.environment}")
        
        # 2. Initialize components
        print("\n🔧 Initializing components...")
        
        # Protocol adapters
        protocol_adapters = {
            "graph_api": GraphAPIAdapter("graph_api", settings.protocols["graph_api"]),
            # Note: In a real implementation, you would add other adapters:
            # "exchange": ExchangeWebServicesAdapter("exchange", settings.protocols["exchange"]),
            # "imap": IMAPAdapter("imap", settings.protocols["imap"]),
        }
        
        # Database connectors
        database_connectors = {
            "postgresql": PostgreSQLConnector("postgresql", settings.database.model_dump()),
            # Note: In a real implementation, you would add other connectors:
            # "mongodb": MongoDBConnector("mongodb", mongodb_config),
        }
        
        # Processors
        processors = {
            "email": EmailProcessor("email", {
                "normalize_content": True,
                "extract_links": True,
                "validate_addresses": True,
                "html_to_text": True,
            }),
            "attachment": AttachmentProcessor("attachment", {
                "max_attachment_size": settings.email.max_attachment_size,
                "scan_for_viruses": False,  # Disabled for example
                "extract_metadata": True,
                "calculate_hashes": True,
            }),
        }
        
        # 3. Create and initialize ingestor
        print("\n🏗️  Creating Outlook Ingestor...")
        
        ingestor = OutlookIngestor(
            settings=settings,
            protocol_adapters=protocol_adapters,
            database_connectors=database_connectors,
            processors=processors,
        )
        
        # Initialize all components
        await ingestor.initialize()
        print("✅ Ingestor initialized successfully")
        
        try:
            # 4. Test connections
            print("\n🔍 Testing connections...")
            
            status = await ingestor.get_status()
            print("📊 Component Status:")
            for component_type, components in status.items():
                if component_type != "overall_status":
                    print(f"  {component_type.title()}:")
                    for name, component_status in components.items():
                        status_icon = "✅" if component_status.get("is_connected") else "❌"
                        print(f"    {status_icon} {name}")
            
            # 5. Example 1: Basic email processing
            print("\n📧 Example 1: Basic Email Processing")
            print("-" * 50)
            
            try:
                # Note: This will fail in the example since we don't have real credentials
                # In a real implementation, this would process actual emails
                
                result = await ingestor.process_emails(
                    protocol="graph_api",
                    database="postgresql",
                    folder_filters=["Inbox", "Sent Items"],
                    batch_size=100,
                    include_attachments=True,
                    date_range={
                        "start": datetime.utcnow() - timedelta(days=7),
                        "end": datetime.utcnow(),
                    }
                )
                
                print(f"✅ Processing completed!")
                print(f"   📊 Total emails: {result.total_items}")
                print(f"   ✅ Successful: {result.successful_items}")
                print(f"   ❌ Failed: {result.failed_items}")
                print(f"   ⏱️  Duration: {result.duration_seconds:.2f} seconds")
                print(f"   🚀 Rate: {result.items_per_second:.2f} emails/second")
                
            except Exception as e:
                print(f"❌ Email processing failed (expected in example): {e}")
                print("   This is expected since we're using placeholder credentials")
            
            # 6. Example 2: Streaming processing
            print("\n📦 Example 2: Streaming Processing")
            print("-" * 50)
            
            try:
                # Streaming processing for large datasets
                result = await ingestor.process_emails_stream(
                    protocol="graph_api",
                    database="postgresql",
                    batch_size=50,
                    include_attachments=True,
                )
                
                print(f"✅ Streaming processing completed!")
                print(f"   📊 Total emails: {result.total_items}")
                
            except Exception as e:
                print(f"❌ Streaming processing failed (expected in example): {e}")
                print("   This is expected since we're using placeholder credentials")
            
            # 7. Example 3: Configuration examples
            print("\n⚙️  Example 3: Configuration Examples")
            print("-" * 50)
            
            print("📋 Current configuration:")
            print(f"   App: {settings.app_name} v{settings.app_version}")
            print(f"   Environment: {settings.environment}")
            print(f"   Debug mode: {settings.debug}")
            print(f"   Database: {settings.database.host}:{settings.database.port}")
            print(f"   Batch size: {settings.processing.batch_size}")
            print(f"   Max workers: {settings.processing.max_workers}")
            print(f"   Protocols: {list(settings.protocols.keys())}")
            
            # 8. Example 4: Monitoring and metrics
            print("\n📊 Example 4: Monitoring and Metrics")
            print("-" * 50)
            
            # Get detailed status
            detailed_status = await ingestor.get_status()
            
            print("🔍 Detailed component status:")
            for component_type, components in detailed_status.items():
                if component_type == "overall_status":
                    print(f"   Overall: {components}")
                else:
                    print(f"   {component_type.title()}:")
                    for name, status_info in components.items():
                        print(f"     • {name}: {status_info}")
            
            print("\n🎉 All examples completed successfully!")
            
        finally:
            # 9. Cleanup
            print("\n🧹 Cleaning up...")
            await ingestor.cleanup()
            print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"\n❌ Example failed with error: {e}")
        logging.exception("Example execution failed")
        return 1
    
    return 0


def show_library_info():
    """Show library information."""
    print("\n📚 Library Information")
    print("-" * 50)
    
    try:
        from evolvishub_outlook_ingestor import __version__, __author__, __email__
        print(f"Version: {__version__}")
        print(f"Author: {__author__}")
        print(f"Email: {__email__}")
    except ImportError:
        print("Library information not available")
    
    print("\n🔧 Available Components:")
    
    # Check protocol adapters
    try:
        from evolvishub_outlook_ingestor.protocols import (
            GraphAPIAdapter,
            ExchangeWebServicesAdapter,
            IMAPAdapter,
        )
        print("   Protocol Adapters:")
        print("     ✅ Microsoft Graph API")
        print("     ✅ Exchange Web Services")
        print("     ✅ IMAP/POP3")
    except ImportError as e:
        print(f"   ❌ Protocol adapters not available: {e}")
    
    # Check database connectors
    try:
        from evolvishub_outlook_ingestor.connectors import (
            PostgreSQLConnector,
            MongoDBConnector,
        )
        print("   Database Connectors:")
        print("     ✅ PostgreSQL")
        print("     ✅ MongoDB")
    except ImportError as e:
        print(f"   ❌ Database connectors not available: {e}")
    
    # Check processors
    try:
        from evolvishub_outlook_ingestor.processors import (
            EmailProcessor,
            AttachmentProcessor,
        )
        print("   Processors:")
        print("     ✅ Email Processor")
        print("     ✅ Attachment Processor")
    except ImportError as e:
        print(f"   ❌ Processors not available: {e}")


if __name__ == "__main__":
    print("Starting Evolvishub Outlook Ingestor Complete Example...")
    
    # Show library information
    show_library_info()
    
    # Run the main example
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Example interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        logging.exception("Unexpected error in main")
        sys.exit(1)
