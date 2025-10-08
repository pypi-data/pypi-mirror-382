#!/usr/bin/env python3
"""
Basic Email Ingestion from Microsoft Graph API

This example demonstrates how to set up basic email ingestion from Microsoft Graph API
using the Evolvishub Outlook Ingestor. It shows the minimal configuration required
to connect to Microsoft Graph API and fetch emails.

Requirements:
- Microsoft Azure App Registration with appropriate permissions
- Client ID, Client Secret, and Tenant ID
- Mail.Read permission granted to the application

Usage:
    python basic_graph_api_ingestion.py
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import List

from evolvishub_outlook_ingestor.protocols.microsoft_graph import GraphAPIAdapter
from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.utils.security import SecureCredentialManager


async def main():
    """
    Main function demonstrating basic email ingestion from Microsoft Graph API.
    """
    print("🚀 Starting Basic Microsoft Graph API Email Ingestion Example")
    print("=" * 60)
    
    # Configuration - In production, use environment variables or secure config
    config = {
        "client_id": os.getenv("GRAPH_CLIENT_ID", "your_client_id_here"),
        "client_secret": os.getenv("GRAPH_CLIENT_SECRET", "your_client_secret_here"),
        "tenant_id": os.getenv("GRAPH_TENANT_ID", "your_tenant_id_here"),
        "rate_limit": 100,  # Requests per minute
        "timeout": 30,      # Request timeout in seconds
    }
    
    # Validate configuration
    if any(value.startswith("your_") for value in [config["client_id"], config["client_secret"], config["tenant_id"]]):
        print("❌ Error: Please set your Microsoft Graph API credentials")
        print("   Set environment variables: GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, GRAPH_TENANT_ID")
        print("   Or update the config dictionary in this script")
        return
    
    # Initialize the Graph API adapter
    graph_adapter = GraphAPIAdapter("graph_api", config)
    
    try:
        # Step 1: Initialize and authenticate
        print("\n📡 Initializing Microsoft Graph API connection...")
        await graph_adapter.initialize()
        print("✅ Successfully connected and authenticated")
        
        # Step 2: Get available folders
        print("\n📁 Fetching available folders...")
        folders = await graph_adapter.get_folders()
        print(f"✅ Found {len(folders)} folders:")
        for folder in folders:
            print(f"   - {folder.name} ({folder.total_items} items, {folder.unread_items} unread)")
        
        # Step 3: Fetch recent emails from Inbox
        print("\n📧 Fetching recent emails from Inbox...")
        
        # Define date range for the last 7 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        emails = await graph_adapter.fetch_emails(
            folder_filters=["Inbox"],
            date_range={
                "start": start_date,
                "end": end_date
            },
            limit=10,  # Fetch only 10 emails for this example
            include_attachments=True
        )
        
        print(f"✅ Successfully fetched {len(emails)} emails")
        
        # Step 4: Display email information
        print("\n📋 Email Summary:")
        print("-" * 60)
        
        for i, email in enumerate(emails, 1):
            print(f"\n{i}. Subject: {email.subject}")
            print(f"   From: {email.sender.name} <{email.sender.email}>")
            print(f"   Date: {email.sent_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Size: {email.size or 'Unknown'} bytes")
            
            if email.has_attachments:
                print(f"   Attachments: {len(email.attachments)}")
                for att in email.attachments:
                    print(f"     - {att.name} ({att.size} bytes, {att.content_type})")
            
            # Show first 100 characters of body
            body_preview = email.body[:100] + "..." if len(email.body) > 100 else email.body
            print(f"   Preview: {body_preview}")
        
        # Step 5: Demonstrate email streaming for large datasets
        print("\n🔄 Demonstrating email streaming...")
        
        email_count = 0
        async for email_batch in graph_adapter.fetch_emails_stream(
            folder_filters=["Inbox"],
            batch_size=5,
            limit=15
        ):
            email_count += len(email_batch)
            print(f"   Processed batch of {len(email_batch)} emails (total: {email_count})")
        
        print(f"✅ Streaming completed. Total emails processed: {email_count}")
        
        # Step 6: Get adapter status
        print("\n📊 Adapter Status:")
        status = graph_adapter.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error during email ingestion: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Step 7: Cleanup
        print("\n🧹 Cleaning up...")
        await graph_adapter.cleanup()
        print("✅ Cleanup completed")
    
    print("\n🎉 Basic email ingestion example completed successfully!")


def setup_secure_credentials():
    """
    Example of how to securely manage credentials using the built-in credential manager.
    
    This function demonstrates how to encrypt and store sensitive credentials
    securely instead of using plain text.
    """
    print("\n🔒 Secure Credential Management Example")
    print("-" * 40)
    
    # Initialize credential manager with a master key
    # In production, store this key securely (e.g., environment variable, key vault)
    master_key = os.getenv("MASTER_ENCRYPTION_KEY", "your_master_key_here")
    credential_manager = SecureCredentialManager(master_key)
    
    # Example: Encrypt sensitive credentials
    client_secret = "your_actual_client_secret"
    encrypted_secret = credential_manager.encrypt_credential(client_secret)
    
    print(f"Original secret: {client_secret}")
    print(f"Encrypted secret: {encrypted_secret}")
    
    # Decrypt when needed
    decrypted_secret = credential_manager.decrypt_credential(encrypted_secret)
    print(f"Decrypted secret: {decrypted_secret}")
    print(f"Encryption successful: {client_secret == decrypted_secret}")
    
    return encrypted_secret


def demonstrate_error_handling():
    """
    Example of proper error handling patterns when using the Graph API adapter.
    """
    print("\n⚠️  Error Handling Best Practices")
    print("-" * 40)
    
    # Common error scenarios and how to handle them:
    
    print("1. Authentication Errors:")
    print("   - Check client credentials")
    print("   - Verify tenant ID")
    print("   - Ensure proper permissions are granted")
    
    print("\n2. Rate Limiting:")
    print("   - The adapter automatically handles rate limiting")
    print("   - Configure rate_limit in config to match your quota")
    print("   - Use batch processing for large datasets")
    
    print("\n3. Network Errors:")
    print("   - The adapter includes automatic retry logic")
    print("   - Configure timeout values appropriately")
    print("   - Implement circuit breaker pattern for production")
    
    print("\n4. Data Validation:")
    print("   - Always validate email data before processing")
    print("   - Handle missing or malformed email fields gracefully")
    print("   - Use the built-in input sanitization features")


if __name__ == "__main__":
    print("Evolvishub Outlook Ingestor - Basic Graph API Example")
    print("For more examples, see: https://github.com/evolvisai/metcal")
    print()
    
    # Show secure credential management example
    setup_secure_credentials()
    
    # Show error handling best practices
    demonstrate_error_handling()
    
    # Run the main example
    asyncio.run(main())
