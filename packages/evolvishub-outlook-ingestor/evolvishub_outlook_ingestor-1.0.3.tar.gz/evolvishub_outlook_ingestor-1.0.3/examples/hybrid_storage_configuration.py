#!/usr/bin/env python3
"""
Hybrid Storage Configuration Example for Evolvishub Outlook Ingestor.

This example demonstrates how to configure and use the enhanced attachment
processor with hybrid storage, combining database storage for metadata
and object storage for large attachments.

Features demonstrated:
- Multiple storage backend configuration (MinIO, AWS S3, Azure Blob)
- Size-based storage routing rules
- Attachment deduplication
- Compression for text files
- Secure URL generation for attachment access

Requirements:
    pip install evolvishub-outlook-ingestor[all]
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from evolvishub_outlook_ingestor.protocols.microsoft_graph import GraphAPIAdapter
from evolvishub_outlook_ingestor.connectors.postgresql_connector import PostgreSQLConnector
from evolvishub_outlook_ingestor.connectors.minio_connector import MinIOConnector
from evolvishub_outlook_ingestor.connectors.aws_s3_connector import AWSS3Connector
from evolvishub_outlook_ingestor.connectors.azure_blob_connector import AzureBlobConnector
from evolvishub_outlook_ingestor.processors.enhanced_attachment_processor import (
    EnhancedAttachmentProcessor,
    StorageStrategy,
    CompressionType,
    StorageRule
)
from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.utils.security import SecureCredentialManager


async def setup_storage_backends() -> Dict[str, Any]:
    """
    Set up multiple storage backends for hybrid storage.
    
    Returns:
        Dictionary of configured storage connectors
    """
    print("🔧 Setting up storage backends...")
    
    storage_backends = {}
    
    # MinIO for primary object storage (self-hosted)
    minio_config = {
        "endpoint_url": os.getenv("MINIO_ENDPOINT", "localhost:9000"),
        "access_key": os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        "secret_key": os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        "bucket_name": "email-attachments-primary",
        "use_ssl": False,  # Set to True for production
    }
    
    try:
        minio_connector = MinIOConnector("minio_primary", minio_config)
        await minio_connector.initialize()
        storage_backends["minio"] = minio_connector
        print("✅ MinIO connector initialized")
    except Exception as e:
        print(f"⚠️  MinIO not available: {e}")
    
    # AWS S3 for archive storage (cloud)
    if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
        s3_config = {
            "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "bucket_name": "email-attachments-archive",
            "region": os.getenv("AWS_REGION", "us-east-1"),
        }
        
        try:
            s3_connector = AWSS3Connector("aws_s3_archive", s3_config)
            await s3_connector.initialize()
            storage_backends["aws_s3"] = s3_connector
            print("✅ AWS S3 connector initialized")
        except Exception as e:
            print(f"⚠️  AWS S3 not available: {e}")
    
    # Azure Blob Storage for backup (cloud)
    if os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
        azure_config = {
            "access_key": os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
            "secret_key": "",  # Not used with connection string
            "bucket_name": "email-attachments-backup",
        }
        
        try:
            azure_connector = AzureBlobConnector("azure_backup", azure_config)
            await azure_connector.initialize()
            storage_backends["azure"] = azure_connector
            print("✅ Azure Blob Storage connector initialized")
        except Exception as e:
            print(f"⚠️  Azure Blob Storage not available: {e}")
    
    return storage_backends


async def configure_enhanced_processor(storage_backends: Dict[str, Any]) -> EnhancedAttachmentProcessor:
    """
    Configure the enhanced attachment processor with hybrid storage rules.
    
    Args:
        storage_backends: Available storage backend connectors
        
    Returns:
        Configured enhanced attachment processor
    """
    print("⚙️  Configuring enhanced attachment processor...")
    
    # Enhanced processor configuration
    processor_config = {
        "storage_strategy": "hybrid",
        "size_threshold": 1024 * 1024,  # 1MB threshold
        "enable_compression": True,
        "enable_deduplication": True,
        "enable_virus_scanning": False,  # Disabled for demo
        "max_attachment_size": 50 * 1024 * 1024,  # 50MB max
        "default_storage_backend": "minio",
        
        # Allowed file types
        "allowed_extensions": [
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".txt", ".csv", ".json", ".xml", ".zip", ".tar", ".gz",
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"
        ],
        
        # Blocked file types for security
        "blocked_extensions": [
            ".exe", ".bat", ".cmd", ".com", ".scr", ".vbs", ".js", ".jar"
        ],
        
        # Compressible content types
        "compressible_types": [
            "text/plain", "text/html", "text/css", "text/javascript",
            "application/json", "application/xml", "application/csv"
        ],
        
        # Storage routing rules
        "storage_rules": [
            {
                "name": "large_files",
                "condition": "size > 5*1024*1024",  # Files > 5MB
                "strategy": "storage_only",
                "storage_backend": "minio",
            },
            {
                "name": "archive_old_files",
                "condition": "size > 10*1024*1024",  # Files > 10MB
                "strategy": "storage_only",
                "storage_backend": "aws_s3" if "aws_s3" in storage_backends else "minio",
            },
            {
                "name": "medium_files",
                "condition": "size > 1024*1024 and size <= 5*1024*1024",  # 1-5MB
                "strategy": "hybrid",
                "storage_backend": "minio",
            },
            {
                "name": "small_files",
                "condition": "size <= 1024*1024",  # Files <= 1MB
                "strategy": "database_only",
            },
            {
                "name": "compressible_text",
                "condition": "content_type.startswith('text/') and size > 1024",
                "strategy": "hybrid",
                "storage_backend": "minio",
                "compress": True,
                "compression_type": "gzip"
            },
            {
                "name": "images",
                "condition": "content_type.startswith('image/')",
                "strategy": "hybrid",
                "storage_backend": "minio",
            },
            {
                "name": "documents",
                "condition": "extension in ['.pdf', '.doc', '.docx', '.xls', '.xlsx']",
                "strategy": "hybrid",
                "storage_backend": "minio",
            }
        ]
    }
    
    # Create processor
    processor = EnhancedAttachmentProcessor("hybrid_attachments", processor_config)
    
    # Add storage backends
    for name, connector in storage_backends.items():
        await processor.add_storage_backend(name, connector)
    
    print(f"✅ Enhanced processor configured with {len(storage_backends)} storage backends")
    return processor


async def demonstrate_hybrid_storage():
    """
    Demonstrate hybrid storage functionality with real email processing.
    """
    print("🚀 Starting Hybrid Storage Configuration Demo")
    print("=" * 60)
    
    # Setup storage backends
    storage_backends = await setup_storage_backends()
    
    if not storage_backends:
        print("❌ No storage backends available. Please configure at least MinIO.")
        return
    
    # Configure enhanced processor
    processor = await configure_enhanced_processor(storage_backends)
    
    # Setup database connector for metadata
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "outlook_ingestor"),
        "username": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
    }
    
    try:
        # Initialize database connector
        db_connector = PostgreSQLConnector("postgres_main", db_config)
        await db_connector.initialize()
        print("✅ Database connector initialized")
        
        # Setup Graph API (if credentials available)
        graph_config = {
            "client_id": os.getenv("GRAPH_CLIENT_ID", "your_client_id"),
            "client_secret": os.getenv("GRAPH_CLIENT_SECRET", "your_client_secret"),
            "tenant_id": os.getenv("GRAPH_TENANT_ID", "your_tenant_id"),
        }
        
        if all(v != f"your_{k.split('_')[-1]}" for k, v in graph_config.items()):
            # Real credentials provided
            graph_adapter = GraphAPIAdapter("graph_api", graph_config)
            await graph_adapter.initialize()
            
            print("📧 Fetching emails with attachments...")
            emails = await graph_adapter.fetch_emails(
                limit=5,
                filter_query="hasAttachments eq true"
            )
            
            print(f"📨 Processing {len(emails)} emails with attachments...")
            
            for i, email in enumerate(emails, 1):
                print(f"\n📧 Processing email {i}: {email.subject}")
                
                # Process attachments with enhanced processor
                result = await processor.process(email)
                
                if result.status.value == "success":
                    metadata = result.metadata
                    print(f"   ✅ Processed {metadata['processed_count']}/{metadata['attachment_count']} attachments")
                    
                    # Show storage information
                    for storage_info in metadata.get('storage_infos', []):
                        info = storage_info
                        print(f"      📎 {info.get('attachment_id', 'Unknown')}: "
                              f"stored in {info.get('storage_location', 'unknown')} "
                              f"({info.get('original_size', 0)} -> {info.get('stored_size', 0)} bytes)")
                        
                        if info.get('compressed'):
                            compression_ratio = (1 - info['stored_size'] / info['original_size']) * 100
                            print(f"         🗜️  Compressed: {compression_ratio:.1f}% reduction")
                    
                    # Store email metadata in database
                    await db_connector.store_email(email)
                    print(f"   💾 Email metadata stored in database")
                    
                else:
                    print(f"   ❌ Processing failed: {result.error_message}")
        
        else:
            print("⚠️  No Graph API credentials provided. Using mock data for demonstration.")
            await demonstrate_with_mock_data(processor, db_connector)
        
        # Demonstrate attachment retrieval
        print("\n🔍 Demonstrating attachment retrieval...")
        await demonstrate_attachment_retrieval(processor, storage_backends)
        
        # Show processor status
        print("\n📊 Processor Status:")
        status = processor.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Show storage backend status
        print("\n🗄️  Storage Backend Status:")
        for name, backend in storage_backends.items():
            backend_status = backend.get_status()
            print(f"   {name}: {backend_status['storage_type']} - Connected: {backend_status['is_connected']}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        try:
            await db_connector.cleanup()
        except:
            pass
        
        for backend in storage_backends.values():
            try:
                await backend.cleanup()
            except:
                pass
        
        print("✅ Cleanup completed")


async def demonstrate_with_mock_data(processor, db_connector):
    """Demonstrate with mock email data."""
    from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAddress, EmailAttachment
    
    # Create mock email with various attachment types
    sender = EmailAddress(email="demo@example.com", name="Demo User")
    
    # Create different types of attachments to test routing rules
    attachments = [
        # Small text file (should go to database)
        EmailAttachment(
            id="att_001",
            name="small_note.txt",
            content_type="text/plain",
            size=512,
            content=b"This is a small text file for testing." * 10,
        ),
        # Medium image (should use hybrid storage)
        EmailAttachment(
            id="att_002", 
            name="medium_image.jpg",
            content_type="image/jpeg",
            size=2 * 1024 * 1024,  # 2MB
            content=b"FAKE_JPEG_DATA" * (2 * 1024 * 1024 // 15),
        ),
        # Large document (should go to object storage)
        EmailAttachment(
            id="att_003",
            name="large_document.pdf", 
            content_type="application/pdf",
            size=8 * 1024 * 1024,  # 8MB
            content=b"FAKE_PDF_DATA" * (8 * 1024 * 1024 // 13),
        ),
    ]
    
    email = EmailMessage(
        id="demo_email_001",
        subject="Demo Email with Mixed Attachments",
        body="This is a demo email with various attachment types.",
        sender=sender,
        from_address=sender,
        to_recipients=[sender],
        sent_date=datetime.utcnow(),
        received_date=datetime.utcnow(),
        attachments=attachments,
        has_attachments=True
    )
    
    print("📧 Processing mock email with mixed attachments...")
    result = await processor.process(email)
    
    if result.status.value == "success":
        metadata = result.metadata
        print(f"   ✅ Processed {metadata['processed_count']}/{metadata['attachment_count']} attachments")
        
        # Store in database
        await db_connector.store_email(email)
        print("   💾 Mock email stored in database")
    else:
        print(f"   ❌ Processing failed: {result.error_message}")


async def demonstrate_attachment_retrieval(processor, storage_backends):
    """Demonstrate secure attachment retrieval."""
    print("🔗 Generating secure URLs for attachment access...")
    
    # This would normally use real storage info from processed attachments
    for backend_name, backend in storage_backends.items():
        try:
            # List some objects to demonstrate URL generation
            objects = await backend.list_attachments(limit=3)
            
            for obj in objects[:2]:  # Just show first 2
                # Generate secure URL
                secure_url = await backend.generate_presigned_url(
                    obj.key,
                    expires_in=3600  # 1 hour
                )
                
                print(f"   🔗 {backend_name}/{obj.key}: {secure_url[:80]}...")
                
        except Exception as e:
            print(f"   ⚠️  Could not generate URLs for {backend_name}: {e}")


if __name__ == "__main__":
    print("Evolvishub Outlook Ingestor - Hybrid Storage Configuration Demo")
    print("================================================================")
    print()
    print("This demo shows how to configure hybrid storage with multiple backends.")
    print("Make sure you have the required services running:")
    print("  - PostgreSQL database")
    print("  - MinIO server (optional: docker run -p 9000:9000 minio/minio server /data)")
    print("  - AWS/Azure credentials (optional)")
    print()
    
    # Run the demonstration
    asyncio.run(demonstrate_hybrid_storage())
