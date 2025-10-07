"""
Microsoft Graph API protocol adapter for Evolvishub Outlook Ingestor.

This module implements the Microsoft Graph API protocol adapter for accessing
Outlook emails using modern OAuth2 authentication and REST API calls.

Features:
- OAuth2 authentication using MSAL library
- Async HTTP operations with aiohttp
- Rate limiting (100 requests/minute default)
- Pagination support for large datasets
- Folder filtering and date range queries
- Comprehensive error handling for Graph API specific errors
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, List, Optional
from urllib.parse import urlencode

import aiohttp
from msal import ConfidentialClientApplication

from evolvishub_outlook_ingestor.core.data_models import (
    EmailAddress,
    EmailAttachment,
    EmailMessage,
    OutlookFolder,
    AttachmentType,
    EmailImportance,
    EmailSensitivity,
)
from evolvishub_outlook_ingestor.core.exceptions import (
    AuthenticationError,
    GraphAPIError,
    ProtocolError,
)
from evolvishub_outlook_ingestor.protocols.base_protocol import BaseProtocol
from evolvishub_outlook_ingestor.utils.retry import retry_with_config, RetryConfig
# Import security utilities with lazy loading to avoid circular imports
def _get_security_utils():
    from evolvishub_outlook_ingestor.utils.security import (
        get_credential_manager,
        mask_sensitive_data,
    )
    return get_credential_manager, mask_sensitive_data


class GraphAPIAdapter(BaseProtocol):
    """Microsoft Graph API protocol adapter."""
    
    def __init__(self, name: str, config: Dict[str, Any], **kwargs):
        """
        Initialize Graph API adapter.
        
        Args:
            name: Adapter name
            config: Configuration dictionary containing:
                - client_id: Azure AD application client ID
                - client_secret: Azure AD application client secret
                - tenant_id: Azure AD tenant ID
                - server: Graph API server (default: graph.microsoft.com)
                - rate_limit: Requests per minute (default: 100)
                - timeout: Request timeout in seconds (default: 60)
        """
        super().__init__(name, config, **kwargs)

        # Get credential manager (lazy loading)
        get_credential_manager, _ = _get_security_utils()
        self._credential_manager = get_credential_manager()

        # Graph API configuration
        self.client_id = config.get("client_id", "")
        self.tenant_id = config.get("tenant_id", "")
        self.server = config.get("server", "graph.microsoft.com")
        self.base_url = f"https://{self.server}/v1.0"

        # Secure client secret handling
        client_secret_raw = config.get("client_secret", "")
        client_secret_env = config.get("client_secret_env", "GRAPH_CLIENT_SECRET")

        # Try to get client secret from environment first, then from config
        client_secret = (
            self._credential_manager.get_credential_from_env(client_secret_env) or
            client_secret_raw
        )

        # Encrypt client secret for storage
        if client_secret:
            self._encrypted_client_secret = self._credential_manager.encrypt_credential(client_secret)
        else:
            self._encrypted_client_secret = ""
        
        # Authentication
        self.msal_app = None
        self.access_token = None
        self.token_expires_at = None
        
        # HTTP session
        self.session = None
        
        # Rate limiting
        self.rate_limit = config.get("rate_limit", 100)  # requests per minute
        self.request_interval = 60.0 / self.rate_limit  # seconds between requests
        self.last_request_time = 0.0
        
        # Retry configuration for Graph API
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay=1.0,
            max_delay=30.0,
            retry_on_exceptions=[
                aiohttp.ClientError,
                asyncio.TimeoutError,
                GraphAPIError,
            ],
            stop_on_exceptions=[
                AuthenticationError,
            ]
        )
    
    async def _initialize_connection(self) -> None:
        """Initialize connection to Graph API."""
        # Get decrypted client secret
        client_secret = self._credential_manager.decrypt_credential(self._encrypted_client_secret)

        if not all([self.client_id, client_secret, self.tenant_id]):
            raise AuthenticationError(
                "Missing required Graph API credentials",
                auth_method="oauth2",
                context={
                    "client_id_provided": bool(self.client_id),
                    "client_secret_provided": bool(client_secret),
                    "tenant_id_provided": bool(self.tenant_id),
                }
            )
        
        # Initialize MSAL application
        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.msal_app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=client_secret,
            authority=authority,
        )
        
        # Initialize HTTP session
        timeout = aiohttp.ClientTimeout(total=self.config.get("timeout", 60))
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        self.logger.info("Graph API connection initialized", server=self.server)
    
    async def _authenticate(self) -> None:
        """Authenticate with Microsoft Graph API using OAuth2."""
        if not self.msal_app:
            raise AuthenticationError("MSAL application not initialized")
        
        try:
            # Request access token for Graph API
            scopes = ["https://graph.microsoft.com/.default"]
            result = self.msal_app.acquire_token_for_client(scopes=scopes)
            
            if "access_token" not in result:
                error_description = result.get("error_description", "Unknown error")
                raise AuthenticationError(
                    f"Failed to acquire access token: {error_description}",
                    auth_method="oauth2",
                    context={"error": result.get("error"), "correlation_id": result.get("correlation_id")}
                )
            
            self.access_token = result["access_token"]
            expires_in = result.get("expires_in", 3600)
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)  # 5 min buffer
            
            self.logger.info(
                "Graph API authentication successful",
                expires_at=self.token_expires_at.isoformat()
            )
            
        except Exception as e:
            raise AuthenticationError(
                f"Graph API authentication failed: {e}",
                auth_method="oauth2",
                cause=e
            )
    
    async def _cleanup_connection(self) -> None:
        """Cleanup connection resources."""
        if self.session:
            await self.session.close()
            self.session = None
        
        self.access_token = None
        self.token_expires_at = None
        self.msal_app = None
    
    async def _ensure_authenticated(self) -> None:
        """Ensure we have a valid access token."""
        if not self.access_token or (
            self.token_expires_at and datetime.utcnow() >= self.token_expires_at
        ):
            await self._authenticate()
    
    async def _rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        if self.enable_rate_limiting:
            current_time = asyncio.get_event_loop().time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.request_interval:
                sleep_time = self.request_interval - time_since_last
                await asyncio.sleep(sleep_time)
            
            self.last_request_time = asyncio.get_event_loop().time()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make request with retry logic."""
        return await self._make_request_impl(method, endpoint, params, data)
    async def _make_request_impl(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to Graph API."""
        await self._ensure_authenticated()
        await self._rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
            ) as response:
                
                # Handle rate limiting
                if response.status == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    self.logger.warning(
                        "Graph API rate limit exceeded",
                        retry_after=retry_after,
                        endpoint=endpoint
                    )
                    await asyncio.sleep(retry_after)
                    raise GraphAPIError(
                        "Rate limit exceeded",
                        status_code=429,
                        error_code="TooManyRequests"
                    )
                
                # Handle authentication errors
                if response.status == 401:
                    self.access_token = None  # Force re-authentication
                    raise AuthenticationError(
                        "Graph API authentication failed",
                        auth_method="oauth2"
                    )
                
                # Parse response
                response_data = await response.json()
                
                # Handle API errors
                if response.status >= 400:
                    error_info = response_data.get("error", {})
                    error_code = error_info.get("code", "UnknownError")
                    error_message = error_info.get("message", "Unknown error")
                    
                    raise GraphAPIError(
                        f"Graph API error: {error_message}",
                        status_code=response.status,
                        error_code=error_code,
                        context={"endpoint": endpoint, "method": method}
                    )
                
                return response_data
                
        except aiohttp.ClientError as e:
            raise GraphAPIError(
                f"HTTP client error: {e}",
                context={"endpoint": endpoint, "method": method},
                cause=e
            )
    
    async def _fetch_emails_impl(
        self,
        folder_filters: Optional[List[str]] = None,
        date_range: Optional[Dict[str, datetime]] = None,
        limit: Optional[int] = None,
        include_attachments: bool = True,
        **kwargs
    ) -> List[EmailMessage]:
        """Fetch emails from Graph API."""
        emails = []
        
        # Get folders to process
        folders = await self.get_folders()
        if folder_filters:
            folders = [f for f in folders if f.name in folder_filters]
        
        # Process each folder
        for folder in folders:
            folder_emails = await self._fetch_folder_emails(
                folder.id,
                date_range=date_range,
                limit=limit,
                include_attachments=include_attachments,
                **kwargs
            )
            emails.extend(folder_emails)
            
            if limit and len(emails) >= limit:
                emails = emails[:limit]
                break
        
        return emails
    
    async def _fetch_folder_emails(
        self,
        folder_id: str,
        date_range: Optional[Dict[str, datetime]] = None,
        limit: Optional[int] = None,
        include_attachments: bool = True,
        **kwargs
    ) -> List[EmailMessage]:
        """Fetch emails from a specific folder."""
        emails = []
        
        # Build query parameters
        params = {
            "$top": min(limit or 1000, 1000),  # Graph API max is 1000
            "$orderby": "receivedDateTime desc",
        }
        
        # Add date filter
        if date_range:
            filters = []
            if "start" in date_range:
                filters.append(f"receivedDateTime ge {date_range['start'].isoformat()}Z")
            if "end" in date_range:
                filters.append(f"receivedDateTime le {date_range['end'].isoformat()}Z")
            
            if filters:
                params["$filter"] = " and ".join(filters)
        
        # Fetch emails with pagination
        endpoint = f"/me/mailFolders/{folder_id}/messages"
        
        while endpoint and (not limit or len(emails) < limit):
            response = await self._make_request("GET", endpoint, params=params)
            
            # Process emails
            for email_data in response.get("value", []):
                email = await self._convert_graph_email(email_data, include_attachments)
                emails.append(email)
                
                if limit and len(emails) >= limit:
                    break
            
            # Get next page
            endpoint = response.get("@odata.nextLink")
            if endpoint:
                # Extract endpoint from full URL
                endpoint = endpoint.replace(self.base_url, "")
                params = {}  # Parameters are included in the nextLink URL
        
        return emails

    async def _convert_graph_email(
        self,
        email_data: Dict[str, Any],
        include_attachments: bool = True
    ) -> EmailMessage:
        """Convert Graph API email data to EmailMessage."""
        # Extract basic email information
        email_id = email_data.get("id", "")
        subject = email_data.get("subject", "")
        body_content = email_data.get("body", {}).get("content", "")
        body_type = email_data.get("body", {}).get("contentType", "text").lower()

        # Parse sender and recipients
        sender = self._parse_email_address(email_data.get("sender", {}).get("emailAddress", {}))
        from_address = self._parse_email_address(email_data.get("from", {}).get("emailAddress", {}))

        to_recipients = [
            self._parse_email_address(addr.get("emailAddress", {}))
            for addr in email_data.get("toRecipients", [])
        ]
        cc_recipients = [
            self._parse_email_address(addr.get("emailAddress", {}))
            for addr in email_data.get("ccRecipients", [])
        ]
        bcc_recipients = [
            self._parse_email_address(addr.get("emailAddress", {}))
            for addr in email_data.get("bccRecipients", [])
        ]
        reply_to = [
            self._parse_email_address(addr.get("emailAddress", {}))
            for addr in email_data.get("replyTo", [])
        ]

        # Parse dates
        sent_date = self._parse_datetime(email_data.get("sentDateTime"))
        received_date = self._parse_datetime(email_data.get("receivedDateTime"))
        created_date = self._parse_datetime(email_data.get("createdDateTime"))
        modified_date = self._parse_datetime(email_data.get("lastModifiedDateTime"))

        # Parse importance and sensitivity
        importance_map = {
            "low": EmailImportance.LOW,
            "normal": EmailImportance.NORMAL,
            "high": EmailImportance.HIGH,
        }
        importance = importance_map.get(
            email_data.get("importance", "normal").lower(),
            EmailImportance.NORMAL
        )

        # Parse flags and properties
        is_read = email_data.get("isRead", False)
        is_draft = email_data.get("isDraft", False)
        has_attachments = email_data.get("hasAttachments", False)

        # Parse folder information
        folder_id = email_data.get("parentFolderId", "")

        # Parse headers (Graph API provides limited headers)
        headers = {}
        internet_headers = email_data.get("internetMessageHeaders", [])
        for header in internet_headers:
            headers[header.get("name", "")] = header.get("value", "")

        # Get message size
        size = email_data.get("bodyPreview", "")  # Graph API doesn't provide exact size

        # Fetch attachments if requested
        attachments = []
        if include_attachments and has_attachments:
            attachments = await self._fetch_email_attachments(email_id)

        # Create EmailMessage
        email = EmailMessage(
            id=email_id,
            message_id=headers.get("Message-ID"),
            conversation_id=email_data.get("conversationId"),
            subject=subject,
            body=body_content,
            body_type=body_type,
            is_html=(body_type == "html"),
            sender=sender,
            from_address=from_address,
            to_recipients=to_recipients,
            cc_recipients=cc_recipients,
            bcc_recipients=bcc_recipients,
            reply_to=reply_to,
            sent_date=sent_date,
            received_date=received_date,
            created_date=created_date,
            modified_date=modified_date,
            importance=importance,
            is_read=is_read,
            is_draft=is_draft,
            has_attachments=has_attachments,
            folder_id=folder_id,
            attachments=attachments,
            headers=headers,
            internet_headers=headers,
            size=len(body_content) if body_content else 0,
        )

        return email

    def _parse_email_address(self, addr_data: Dict[str, Any]) -> Optional[EmailAddress]:
        """Parse email address from Graph API data."""
        if not addr_data:
            return None

        email = addr_data.get("address", "")
        name = addr_data.get("name", "")

        if not email:
            return None

        return EmailAddress(email=email, name=name)

    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from Graph API."""
        if not date_str:
            return None

        try:
            # Graph API returns ISO format with Z suffix
            if date_str.endswith("Z"):
                date_str = date_str[:-1] + "+00:00"
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    async def _fetch_email_attachments(self, email_id: str) -> List[EmailAttachment]:
        """Fetch attachments for an email."""
        attachments = []

        try:
            endpoint = f"/me/messages/{email_id}/attachments"
            response = await self._make_request("GET", endpoint)

            for attachment_data in response.get("value", []):
                attachment = self._convert_graph_attachment(attachment_data)
                if attachment:
                    attachments.append(attachment)

        except Exception as e:
            self.logger.warning(
                "Failed to fetch attachments",
                email_id=email_id,
                error=str(e)
            )

        return attachments

    def _convert_graph_attachment(self, attachment_data: Dict[str, Any]) -> Optional[EmailAttachment]:
        """Convert Graph API attachment data to EmailAttachment."""
        attachment_id = attachment_data.get("id", "")
        name = attachment_data.get("name", "")
        content_type = attachment_data.get("contentType", "")
        size = attachment_data.get("size", 0)

        # Determine attachment type
        attachment_type = AttachmentType.FILE
        is_inline = attachment_data.get("isInline", False)
        if is_inline:
            attachment_type = AttachmentType.INLINE_ATTACHMENT

        content_id = attachment_data.get("contentId")

        # Get content if it's a file attachment (not reference)
        content = None
        if attachment_data.get("@odata.type") == "#microsoft.graph.fileAttachment":
            content_bytes = attachment_data.get("contentBytes")
            if content_bytes:
                import base64
                try:
                    content = base64.b64decode(content_bytes)
                except Exception:
                    pass

        return EmailAttachment(
            id=attachment_id,
            name=name,
            content_type=content_type,
            size=size,
            attachment_type=attachment_type,
            is_inline=is_inline,
            content_id=content_id,
            content=content,
        )

    async def _fetch_emails_stream_impl(
        self,
        folder_filters: Optional[List[str]] = None,
        date_range: Optional[Dict[str, datetime]] = None,
        batch_size: int = 100,
        include_attachments: bool = True,
        **kwargs
    ) -> AsyncGenerator[List[EmailMessage], None]:
        """Stream emails in batches."""
        # Get folders to process
        folders = await self.get_folders()
        if folder_filters:
            folders = [f for f in folders if f.name in folder_filters]

        # Process each folder
        for folder in folders:
            async for batch in self._stream_folder_emails(
                folder.id,
                date_range=date_range,
                batch_size=batch_size,
                include_attachments=include_attachments,
                **kwargs
            ):
                yield batch

    async def _stream_folder_emails(
        self,
        folder_id: str,
        date_range: Optional[Dict[str, datetime]] = None,
        batch_size: int = 100,
        include_attachments: bool = True,
        **kwargs
    ) -> AsyncGenerator[List[EmailMessage], None]:
        """Stream emails from a specific folder."""
        # Build query parameters
        params = {
            "$top": min(batch_size, 1000),  # Graph API max is 1000
            "$orderby": "receivedDateTime desc",
        }

        # Add date filter
        if date_range:
            filters = []
            if "start" in date_range:
                filters.append(f"receivedDateTime ge {date_range['start'].isoformat()}Z")
            if "end" in date_range:
                filters.append(f"receivedDateTime le {date_range['end'].isoformat()}Z")

            if filters:
                params["$filter"] = " and ".join(filters)

        # Fetch emails with pagination
        endpoint = f"/me/mailFolders/{folder_id}/messages"

        while endpoint:
            response = await self._make_request("GET", endpoint, params=params)

            # Process emails in current page
            emails = []
            for email_data in response.get("value", []):
                email = await self._convert_graph_email(email_data, include_attachments)
                emails.append(email)

            if emails:
                yield emails

            # Get next page
            endpoint = response.get("@odata.nextLink")
            if endpoint:
                # Extract endpoint from full URL
                endpoint = endpoint.replace(self.base_url, "")
                params = {}  # Parameters are included in the nextLink URL

    async def _get_folders_impl(self) -> List[OutlookFolder]:
        """Fetch folder list from Graph API."""
        folders = []

        try:
            endpoint = "/me/mailFolders"
            params = {"$top": 1000}  # Get all folders

            response = await self._make_request("GET", endpoint, params=params)

            for folder_data in response.get("value", []):
                folder = self._convert_graph_folder(folder_data)
                if folder:
                    folders.append(folder)

        except Exception as e:
            self.logger.error("Failed to fetch folders", error=str(e))
            raise ProtocolError(
                f"Failed to fetch folders: {e}",
                protocol=self.name,
                cause=e
            )

        return folders

    def _convert_graph_folder(self, folder_data: Dict[str, Any]) -> Optional[OutlookFolder]:
        """Convert Graph API folder data to OutlookFolder."""
        folder_id = folder_data.get("id", "")
        name = folder_data.get("displayName", "")
        parent_folder_id = folder_data.get("parentFolderId")

        total_item_count = folder_data.get("totalItemCount", 0)
        unread_item_count = folder_data.get("unreadItemCount", 0)

        return OutlookFolder(
            id=folder_id,
            name=name,
            display_name=name,
            parent_folder_id=parent_folder_id,
            folder_path=f"/{name}",  # Simplified path
            total_item_count=total_item_count,
            unread_item_count=unread_item_count,
        )
