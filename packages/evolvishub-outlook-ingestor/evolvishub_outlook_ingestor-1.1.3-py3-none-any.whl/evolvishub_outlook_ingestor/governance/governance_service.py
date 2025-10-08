"""
Data governance service for compliance and lineage tracking.

This module provides comprehensive data governance capabilities including
data lineage tracking, retention policies, compliance monitoring, and audit trails.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from evolvishub_outlook_ingestor.core.interfaces import IGovernanceService, service_registry
from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import GovernanceError


class LineageEventType(Enum):
    """Types of lineage events."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    TRANSFORM = "transform"
    EXPORT = "export"
    ARCHIVE = "archive"


class ComplianceStatus(Enum):
    """Compliance status options."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXEMPT = "exempt"


@dataclass
class LineageEvent:
    """Represents a data lineage event."""
    event_id: str
    entity_id: str
    entity_type: str
    event_type: LineageEventType
    timestamp: datetime
    user_id: Optional[str]
    system_id: str
    operation_details: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class RetentionPolicy:
    """Represents a data retention policy."""
    policy_id: str
    name: str
    description: str
    entity_types: List[str]
    retention_period_days: int
    action: str  # 'delete', 'archive', 'anonymize'
    conditions: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class ComplianceRule:
    """Represents a compliance rule."""
    rule_id: str
    name: str
    description: str
    regulation: str  # GDPR, CCPA, HIPAA, etc.
    rule_type: str
    conditions: Dict[str, Any]
    actions: List[str]
    severity: str
    is_active: bool


class GovernanceService(IGovernanceService):
    """
    Data governance service for compliance and lineage tracking.
    
    This service provides comprehensive governance capabilities including:
    - Complete data lineage tracking across all operations
    - Automated retention policy enforcement
    - Compliance monitoring and reporting
    - Audit trail generation and management
    - Data classification and sensitivity tracking
    - Privacy and security compliance (GDPR, CCPA, etc.)
    
    Example:
        ```python
        governance = GovernanceService({
            'storage_connector': postgresql_connector,
            'enable_lineage_tracking': True,
            'enable_retention_policies': True,
            'compliance_frameworks': ['GDPR', 'CCPA'],
            'audit_retention_days': 2555  # 7 years
        })
        
        await governance.initialize()
        
        # Track data lineage
        await governance.track_lineage(
            entity_id="email_123",
            operation="transform",
            metadata={'transformation': 'pii_masking'}
        )
        
        # Apply retention policy
        await governance.apply_retention_policy(
            policy_name="email_retention_7_years",
            entities=["email_123", "email_124"]
        )
        
        # Get lineage
        lineage = await governance.get_lineage("email_123")
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.storage_connector = config.get('storage_connector')
        self.enable_lineage_tracking = config.get('enable_lineage_tracking', True)
        self.enable_retention_policies = config.get('enable_retention_policies', True)
        self.enable_compliance_monitoring = config.get('enable_compliance_monitoring', True)
        self.compliance_frameworks = config.get('compliance_frameworks', ['GDPR'])
        self.audit_retention_days = config.get('audit_retention_days', 2555)  # 7 years default
        
        # State management
        self.is_initialized = False
        self._retention_policies: Dict[str, RetentionPolicy] = {}
        self._compliance_rules: Dict[str, ComplianceRule] = {}
        self._lineage_buffer: List[LineageEvent] = []
        
        # Background tasks
        self._lineage_processor_task: Optional[asyncio.Task] = None
        self._retention_enforcer_task: Optional[asyncio.Task] = None
        self._compliance_monitor_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            'lineage_events_tracked': 0,
            'retention_actions_executed': 0,
            'compliance_violations_detected': 0,
            'audit_records_created': 0
        }
    
    async def initialize(self) -> None:
        """Initialize the governance service."""
        if self.is_initialized:
            return
        
        try:
            self.logger.info("Initializing data governance service")
            
            # Validate storage connector
            if not self.storage_connector:
                raise ValueError("Storage connector is required for governance service")
            
            # Create governance tables
            await self._create_governance_tables()
            
            # Load policies and rules
            await self._load_retention_policies()
            await self._load_compliance_rules()
            
            # Start background tasks
            if self.enable_lineage_tracking:
                self._lineage_processor_task = asyncio.create_task(self._process_lineage_events())
            
            if self.enable_retention_policies:
                self._retention_enforcer_task = asyncio.create_task(self._enforce_retention_policies())
            
            if self.enable_compliance_monitoring:
                self._compliance_monitor_task = asyncio.create_task(self._monitor_compliance())
            
            self.is_initialized = True
            self.logger.info("Data governance service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize governance service: {str(e)}")
            raise GovernanceError(f"Governance initialization failed: {str(e)}")
    
    async def shutdown(self) -> None:
        """Shutdown the governance service."""
        if not self.is_initialized:
            return
        
        self.logger.info("Shutting down governance service")
        
        # Cancel background tasks
        tasks = [self._lineage_processor_task, self._retention_enforcer_task, self._compliance_monitor_task]
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Process remaining lineage events
        if self._lineage_buffer:
            await self._flush_lineage_events()
        
        self.is_initialized = False
        self.logger.info("Governance service shutdown complete")
    
    async def track_lineage(self, entity_id: str, operation: str, metadata: Dict[str, Any]) -> None:
        """
        Track data lineage for an entity.
        
        Args:
            entity_id: Unique identifier of the entity
            operation: Operation performed on the entity
            metadata: Additional metadata about the operation
        """
        if not self.enable_lineage_tracking:
            return
        
        try:
            event = LineageEvent(
                event_id=f"lineage_{datetime.utcnow().timestamp()}",
                entity_id=entity_id,
                entity_type=metadata.get('entity_type', 'email'),
                event_type=LineageEventType(operation),
                timestamp=datetime.utcnow(),
                user_id=metadata.get('user_id'),
                system_id=metadata.get('system_id', 'evolvishub-outlook-ingestor'),
                operation_details=metadata.get('operation_details', {}),
                metadata=metadata
            )
            
            # Add to buffer for batch processing
            self._lineage_buffer.append(event)
            self.stats['lineage_events_tracked'] += 1
            
            # Flush if buffer is getting large
            if len(self._lineage_buffer) >= 100:
                await self._flush_lineage_events()
            
            self.logger.debug(f"Tracked lineage event: {event.event_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to track lineage for {entity_id}: {str(e)}")
    
    async def get_lineage(self, entity_id: str) -> Dict[str, Any]:
        """
        Get data lineage for an entity.
        
        Args:
            entity_id: Entity identifier
            
        Returns:
            Complete lineage information for the entity
        """
        try:
            # Flush pending events first
            await self._flush_lineage_events()
            
            # Query lineage events
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based connector
                query = """
                    SELECT * FROM data_lineage 
                    WHERE entity_id = %s 
                    ORDER BY timestamp ASC
                """
                results = await self.storage_connector.execute(query, (entity_id,))
                events = [self._row_to_lineage_event(row) for row in results]
            
            elif hasattr(self.storage_connector, 'find'):
                # MongoDB-based connector
                cursor = self.storage_connector.database.data_lineage.find({
                    'entity_id': entity_id
                }).sort('timestamp', 1)
                
                results = await cursor.to_list(length=None)
                events = [self._doc_to_lineage_event(doc) for doc in results]
            
            else:
                raise ValueError("Unsupported storage connector for lineage")
            
            # Build lineage graph
            lineage_graph = {
                'entity_id': entity_id,
                'events': [
                    {
                        'event_id': event.event_id,
                        'event_type': event.event_type.value,
                        'timestamp': event.timestamp.isoformat(),
                        'user_id': event.user_id,
                        'system_id': event.system_id,
                        'operation_details': event.operation_details,
                        'metadata': event.metadata
                    }
                    for event in events
                ],
                'summary': {
                    'total_events': len(events),
                    'first_event': events[0].timestamp.isoformat() if events else None,
                    'last_event': events[-1].timestamp.isoformat() if events else None,
                    'operations': list(set(event.event_type.value for event in events))
                }
            }
            
            return lineage_graph
            
        except Exception as e:
            self.logger.error(f"Failed to get lineage for {entity_id}: {str(e)}")
            raise GovernanceError(f"Failed to retrieve lineage: {str(e)}")
    
    async def apply_retention_policy(self, policy_name: str, entities: List[str]) -> None:
        """
        Apply data retention policy to entities.
        
        Args:
            policy_name: Name of the retention policy
            entities: List of entity IDs to apply policy to
        """
        if not self.enable_retention_policies:
            return
        
        try:
            policy = self._retention_policies.get(policy_name)
            if not policy or not policy.is_active:
                raise ValueError(f"Retention policy not found or inactive: {policy_name}")
            
            current_time = datetime.utcnow()
            cutoff_date = current_time - timedelta(days=policy.retention_period_days)
            
            actions_executed = 0
            
            for entity_id in entities:
                # Check if entity meets retention criteria
                if await self._entity_meets_retention_criteria(entity_id, policy, cutoff_date):
                    # Execute retention action
                    await self._execute_retention_action(entity_id, policy)
                    actions_executed += 1
                    
                    # Track lineage
                    await self.track_lineage(
                        entity_id=entity_id,
                        operation="archive" if policy.action == "archive" else "delete",
                        metadata={
                            'retention_policy': policy_name,
                            'action': policy.action,
                            'cutoff_date': cutoff_date.isoformat()
                        }
                    )
            
            self.stats['retention_actions_executed'] += actions_executed
            self.logger.info(f"Applied retention policy {policy_name} to {actions_executed} entities")
            
        except Exception as e:
            self.logger.error(f"Failed to apply retention policy {policy_name}: {str(e)}")
            raise GovernanceError(f"Retention policy application failed: {str(e)}")
    
    async def create_retention_policy(self, policy_data: Dict[str, Any]) -> str:
        """
        Create a new retention policy.
        
        Args:
            policy_data: Policy configuration data
            
        Returns:
            Created policy ID
        """
        try:
            policy_id = f"policy_{datetime.utcnow().timestamp()}"
            
            policy = RetentionPolicy(
                policy_id=policy_id,
                name=policy_data['name'],
                description=policy_data.get('description', ''),
                entity_types=policy_data.get('entity_types', ['email']),
                retention_period_days=policy_data['retention_period_days'],
                action=policy_data.get('action', 'delete'),
                conditions=policy_data.get('conditions', {}),
                is_active=policy_data.get('is_active', True),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store policy
            self._retention_policies[policy.name] = policy
            await self._save_retention_policy(policy)
            
            self.logger.info(f"Created retention policy: {policy.name}")
            return policy_id
            
        except Exception as e:
            self.logger.error(f"Failed to create retention policy: {str(e)}")
            raise GovernanceError(f"Policy creation failed: {str(e)}")
    
    async def check_compliance(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check compliance status for an entity.
        
        Args:
            entity_id: Entity identifier
            entity_data: Entity data to check
            
        Returns:
            Compliance check results
        """
        try:
            compliance_results = {
                'entity_id': entity_id,
                'overall_status': ComplianceStatus.COMPLIANT,
                'framework_results': {},
                'violations': [],
                'recommendations': [],
                'checked_at': datetime.utcnow().isoformat()
            }
            
            # Check against each compliance framework
            for framework in self.compliance_frameworks:
                framework_result = await self._check_framework_compliance(framework, entity_data)
                compliance_results['framework_results'][framework] = framework_result
                
                if framework_result['status'] != ComplianceStatus.COMPLIANT:
                    compliance_results['overall_status'] = ComplianceStatus.NON_COMPLIANT
                    compliance_results['violations'].extend(framework_result.get('violations', []))
            
            # Generate recommendations
            if compliance_results['violations']:
                compliance_results['recommendations'] = await self._generate_compliance_recommendations(
                    compliance_results['violations']
                )
            
            return compliance_results
            
        except Exception as e:
            self.logger.error(f"Failed to check compliance for {entity_id}: {str(e)}")
            return {
                'entity_id': entity_id,
                'overall_status': ComplianceStatus.PENDING_REVIEW,
                'error': str(e)
            }
    
    async def _create_governance_tables(self) -> None:
        """Create governance-related tables."""
        if hasattr(self.storage_connector, 'execute'):
            # SQL-based connector
            await self.storage_connector.execute("""
                CREATE TABLE IF NOT EXISTS data_lineage (
                    event_id VARCHAR(255) PRIMARY KEY,
                    entity_id VARCHAR(255) NOT NULL,
                    entity_type VARCHAR(50) NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    user_id VARCHAR(255),
                    system_id VARCHAR(255) NOT NULL,
                    operation_details JSONB DEFAULT '{}',
                    metadata JSONB DEFAULT '{}'
                )
            """)
            
            await self.storage_connector.execute("""
                CREATE TABLE IF NOT EXISTS retention_policies (
                    policy_id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    description TEXT,
                    entity_types JSONB NOT NULL,
                    retention_period_days INTEGER NOT NULL,
                    action VARCHAR(50) NOT NULL,
                    conditions JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            
            await self.storage_connector.execute("""
                CREATE TABLE IF NOT EXISTS compliance_rules (
                    rule_id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    regulation VARCHAR(100) NOT NULL,
                    rule_type VARCHAR(50) NOT NULL,
                    conditions JSONB DEFAULT '{}',
                    actions JSONB DEFAULT '[]',
                    severity VARCHAR(20) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Create indexes
            await self.storage_connector.execute("CREATE INDEX IF NOT EXISTS idx_lineage_entity ON data_lineage(entity_id)")
            await self.storage_connector.execute("CREATE INDEX IF NOT EXISTS idx_lineage_timestamp ON data_lineage(timestamp)")
        
        elif hasattr(self.storage_connector, 'create_index'):
            # MongoDB-based connector
            await self.storage_connector.database.data_lineage.create_index("entity_id")
            await self.storage_connector.database.data_lineage.create_index("timestamp")
            await self.storage_connector.database.retention_policies.create_index("name", unique=True)
            await self.storage_connector.database.compliance_rules.create_index("regulation")
    
    async def _load_retention_policies(self) -> None:
        """Load retention policies from storage."""
        try:
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based connector
                results = await self.storage_connector.execute("SELECT * FROM retention_policies WHERE is_active = TRUE")
                for row in results:
                    policy = self._row_to_retention_policy(row)
                    self._retention_policies[policy.name] = policy
            
            elif hasattr(self.storage_connector, 'find'):
                # MongoDB-based connector
                cursor = self.storage_connector.database.retention_policies.find({'is_active': True})
                async for doc in cursor:
                    policy = self._doc_to_retention_policy(doc)
                    self._retention_policies[policy.name] = policy
            
            self.logger.info(f"Loaded {len(self._retention_policies)} retention policies")
            
        except Exception as e:
            self.logger.error(f"Failed to load retention policies: {str(e)}")
    
    async def _load_compliance_rules(self) -> None:
        """Load compliance rules from storage."""
        try:
            # Load default compliance rules for configured frameworks
            for framework in self.compliance_frameworks:
                rules = await self._get_default_compliance_rules(framework)
                for rule in rules:
                    self._compliance_rules[rule.rule_id] = rule
            
            self.logger.info(f"Loaded {len(self._compliance_rules)} compliance rules")
            
        except Exception as e:
            self.logger.error(f"Failed to load compliance rules: {str(e)}")
    
    async def _get_default_compliance_rules(self, framework: str) -> List[ComplianceRule]:
        """Get default compliance rules for a framework."""
        rules = []
        
        if framework == 'GDPR':
            rules.extend([
                ComplianceRule(
                    rule_id="gdpr_data_minimization",
                    name="Data Minimization",
                    description="Ensure only necessary data is collected and processed",
                    regulation="GDPR",
                    rule_type="data_collection",
                    conditions={'max_retention_days': 2555},  # 7 years
                    actions=['review', 'anonymize'],
                    severity="high",
                    is_active=True
                ),
                ComplianceRule(
                    rule_id="gdpr_consent_tracking",
                    name="Consent Tracking",
                    description="Track and validate user consent for data processing",
                    regulation="GDPR",
                    rule_type="consent",
                    conditions={'requires_consent': True},
                    actions=['validate_consent', 'request_consent'],
                    severity="critical",
                    is_active=True
                )
            ])
        
        elif framework == 'CCPA':
            rules.extend([
                ComplianceRule(
                    rule_id="ccpa_data_disclosure",
                    name="Data Disclosure Rights",
                    description="Provide data disclosure capabilities for California residents",
                    regulation="CCPA",
                    rule_type="disclosure",
                    conditions={'california_resident': True},
                    actions=['provide_disclosure', 'track_request'],
                    severity="high",
                    is_active=True
                )
            ])
        
        return rules
    
    async def _flush_lineage_events(self) -> None:
        """Flush pending lineage events to storage."""
        if not self._lineage_buffer:
            return
        
        events_to_flush = self._lineage_buffer.copy()
        self._lineage_buffer.clear()
        
        try:
            if hasattr(self.storage_connector, 'execute_many'):
                # SQL-based connector
                values = []
                for event in events_to_flush:
                    values.append((
                        event.event_id, event.entity_id, event.entity_type,
                        event.event_type.value, event.timestamp, event.user_id,
                        event.system_id, event.operation_details, event.metadata
                    ))
                
                query = """
                    INSERT INTO data_lineage 
                    (event_id, entity_id, entity_type, event_type, timestamp, user_id, system_id, operation_details, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                await self.storage_connector.execute_many(query, values)
            
            elif hasattr(self.storage_connector, 'insert_many'):
                # MongoDB-based connector
                documents = []
                for event in events_to_flush:
                    doc = asdict(event)
                    doc['event_type'] = event.event_type.value
                    documents.append(doc)
                
                await self.storage_connector.database.data_lineage.insert_many(documents)
            
            self.logger.debug(f"Flushed {len(events_to_flush)} lineage events")
            
        except Exception as e:
            self.logger.error(f"Failed to flush lineage events: {str(e)}")
            # Put events back in buffer for retry
            self._lineage_buffer.extend(events_to_flush)
    
    async def _process_lineage_events(self) -> None:
        """Background task to process lineage events."""
        while self.is_initialized:
            try:
                if len(self._lineage_buffer) >= 50:  # Batch size
                    await self._flush_lineage_events()
                
                await asyncio.sleep(30)  # Process every 30 seconds
            
            except Exception as e:
                self.logger.error(f"Error in lineage processor: {str(e)}")
                await asyncio.sleep(60)
    
    async def _enforce_retention_policies(self) -> None:
        """Background task to enforce retention policies."""
        while self.is_initialized:
            try:
                for policy in self._retention_policies.values():
                    if policy.is_active:
                        await self._apply_policy_to_eligible_entities(policy)
                
                # Run daily
                await asyncio.sleep(24 * 60 * 60)
            
            except Exception as e:
                self.logger.error(f"Error in retention enforcer: {str(e)}")
                await asyncio.sleep(60 * 60)
    
    async def _monitor_compliance(self) -> None:
        """Background task to monitor compliance."""
        while self.is_initialized:
            try:
                # Scan recent data for compliance violations
                await self._scan_for_compliance_violations()

                # Check retention policy compliance
                await self._check_retention_compliance()

                # Validate data lineage completeness
                await self._validate_lineage_completeness()

                await asyncio.sleep(60 * 60)  # Check hourly

            except Exception as e:
                self.logger.error(f"Error in compliance monitor: {str(e)}")
                await asyncio.sleep(60 * 60)
    
    async def _entity_meets_retention_criteria(self, entity_id: str, policy: RetentionPolicy, cutoff_date: datetime) -> bool:
        """Check if entity meets retention criteria."""
        try:
            # Get entity metadata from lineage
            lineage = await self.get_lineage(entity_id)

            if not lineage or not lineage.get('events'):
                return False

            # Get creation date from first event
            first_event = min(lineage['events'], key=lambda e: e['timestamp'])
            creation_date = datetime.fromisoformat(first_event['timestamp'].replace('Z', '+00:00'))

            # Check if entity is old enough for retention action
            if creation_date > cutoff_date:
                return False

            # Check additional conditions from policy
            conditions = policy.conditions

            # Check last access time if specified
            if 'max_days_since_access' in conditions:
                last_event = max(lineage['events'], key=lambda e: e['timestamp'])
                last_access = datetime.fromisoformat(last_event['timestamp'].replace('Z', '+00:00'))
                days_since_access = (datetime.utcnow() - last_access).days

                if days_since_access < conditions['max_days_since_access']:
                    return False

            # Check entity type
            if 'entity_types' in conditions:
                entity_type = lineage['events'][0].get('metadata', {}).get('entity_type', 'unknown')
                if entity_type not in conditions['entity_types']:
                    return False

            # Check minimum age
            if 'minimum_age_days' in conditions:
                age_days = (datetime.utcnow() - creation_date).days
                if age_days < conditions['minimum_age_days']:
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Failed to check retention criteria for {entity_id}: {str(e)}")
            return False
    
    async def _execute_retention_action(self, entity_id: str, policy: RetentionPolicy) -> None:
        """Execute retention action on entity."""
        try:
            if policy.action == 'delete':
                await self._delete_entity(entity_id)
                self.logger.info(f"Deleted entity {entity_id} per retention policy {policy.name}")

            elif policy.action == 'archive':
                await self._archive_entity(entity_id)
                self.logger.info(f"Archived entity {entity_id} per retention policy {policy.name}")

            elif policy.action == 'anonymize':
                await self._anonymize_entity(entity_id)
                self.logger.info(f"Anonymized entity {entity_id} per retention policy {policy.name}")

            else:
                raise ValueError(f"Unknown retention action: {policy.action}")

            # Track the retention action in lineage
            await self.track_lineage(
                entity_id=entity_id,
                operation="retention_action",
                metadata={
                    'action': policy.action,
                    'policy_name': policy.name,
                    'policy_id': policy.policy_id,
                    'executed_at': datetime.utcnow().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to execute retention action {policy.action} on {entity_id}: {str(e)}")
            raise
    
    async def _apply_policy_to_eligible_entities(self, policy: RetentionPolicy) -> None:
        """Apply retention policy to eligible entities."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_period_days)

            # Query for entities that meet the policy criteria
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based query
                query = """
                    SELECT id FROM emails
                    WHERE created_at < %s
                    AND (entity_type = ANY(%s) OR %s = '{}')
                """
                entity_types = policy.entity_types if policy.entity_types else []
                results = await self.storage_connector.execute(
                    query, (cutoff_date, entity_types, entity_types)
                )
                entity_ids = [row[0] for row in results]

            elif hasattr(self.storage_connector, 'find'):
                # MongoDB-based query
                query_filter = {
                    'created_at': {'$lt': cutoff_date}
                }
                if policy.entity_types:
                    query_filter['entity_type'] = {'$in': policy.entity_types}

                cursor = self.storage_connector.database.emails.find(query_filter, {'id': 1})
                entity_ids = [doc['id'] async for doc in cursor]

            else:
                self.logger.warning("No compatible storage connector for policy enforcement")
                return

            # Apply policy to eligible entities
            for entity_id in entity_ids:
                if await self._entity_meets_retention_criteria(entity_id, policy, cutoff_date):
                    await self._execute_retention_action(entity_id, policy)

            self.logger.info(f"Applied retention policy {policy.name} to {len(entity_ids)} entities")

        except Exception as e:
            self.logger.error(f"Failed to apply policy {policy.name}: {str(e)}")
            raise
    
    async def _check_framework_compliance(self, framework: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance against a specific framework."""
        result = {
            'framework': framework,
            'status': ComplianceStatus.COMPLIANT,
            'violations': [],
            'checks_performed': []
        }
        
        # Get rules for this framework
        framework_rules = [rule for rule in self._compliance_rules.values() if rule.regulation == framework]
        
        for rule in framework_rules:
            check_result = await self._evaluate_compliance_rule(rule, entity_data)
            result['checks_performed'].append({
                'rule_id': rule.rule_id,
                'rule_name': rule.name,
                'passed': check_result['passed'],
                'details': check_result.get('details', '')
            })
            
            if not check_result['passed']:
                result['status'] = ComplianceStatus.NON_COMPLIANT
                result['violations'].append({
                    'rule_id': rule.rule_id,
                    'rule_name': rule.name,
                    'severity': rule.severity,
                    'description': check_result.get('violation_description', '')
                })
        
        return result
    
    async def _evaluate_compliance_rule(self, rule: ComplianceRule, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a compliance rule against entity data."""
        try:
            if rule.rule_type == 'data_collection':
                return await self._evaluate_data_collection_rule(rule, entity_data)
            elif rule.rule_type == 'consent':
                return await self._evaluate_consent_rule(rule, entity_data)
            elif rule.rule_type == 'disclosure':
                return await self._evaluate_disclosure_rule(rule, entity_data)
            elif rule.rule_type == 'retention':
                return await self._evaluate_retention_rule(rule, entity_data)
            elif rule.rule_type == 'anonymization':
                return await self._evaluate_anonymization_rule(rule, entity_data)
            else:
                return {
                    'passed': False,
                    'details': f"Unknown rule type: {rule.rule_type}",
                    'violation_description': f"Rule type {rule.rule_type} is not supported"
                }

        except Exception as e:
            self.logger.error(f"Failed to evaluate rule {rule.name}: {str(e)}")
            return {
                'passed': False,
                'details': f"Rule evaluation failed: {str(e)}",
                'violation_description': f"Technical error in rule evaluation"
            }
    
    async def _generate_compliance_recommendations(self, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on compliance violations."""
        recommendations = []
        
        for violation in violations:
            if 'consent' in violation['rule_id']:
                recommendations.append("Implement consent tracking mechanism")
            elif 'retention' in violation['rule_id']:
                recommendations.append("Review and update data retention policies")
            elif 'anonymization' in violation['rule_id']:
                recommendations.append("Implement data anonymization procedures")
        
        return recommendations
    
    async def _save_retention_policy(self, policy: RetentionPolicy) -> None:
        """Save retention policy to storage."""
        try:
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based storage
                await self.storage_connector.execute("""
                    INSERT INTO retention_policies
                    (policy_id, name, description, entity_types, retention_period_days,
                     action, conditions, is_active, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (policy_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        entity_types = EXCLUDED.entity_types,
                        retention_period_days = EXCLUDED.retention_period_days,
                        action = EXCLUDED.action,
                        conditions = EXCLUDED.conditions,
                        is_active = EXCLUDED.is_active,
                        updated_at = EXCLUDED.updated_at
                """, (
                    policy.policy_id, policy.name, policy.description,
                    policy.entity_types, policy.retention_period_days,
                    policy.action, policy.conditions, policy.is_active,
                    policy.created_at, policy.updated_at
                ))

            elif hasattr(self.storage_connector, 'replace_one'):
                # MongoDB-based storage
                doc = asdict(policy)
                await self.storage_connector.database.retention_policies.replace_one(
                    {'policy_id': policy.policy_id},
                    doc,
                    upsert=True
                )

            self.logger.info(f"Saved retention policy: {policy.name}")

        except Exception as e:
            self.logger.error(f"Failed to save retention policy {policy.name}: {str(e)}")
            raise
    
    def _row_to_lineage_event(self, row: tuple) -> LineageEvent:
        """Convert database row to LineageEvent."""
        return LineageEvent(
            event_id=row[0],
            entity_id=row[1],
            entity_type=row[2],
            event_type=LineageEventType(row[3]),
            timestamp=row[4],
            user_id=row[5],
            system_id=row[6],
            operation_details=row[7] or {},
            metadata=row[8] or {}
        )
    
    def _doc_to_lineage_event(self, doc: Dict[str, Any]) -> LineageEvent:
        """Convert MongoDB document to LineageEvent."""
        return LineageEvent(
            event_id=doc['event_id'],
            entity_id=doc['entity_id'],
            entity_type=doc['entity_type'],
            event_type=LineageEventType(doc['event_type']),
            timestamp=doc['timestamp'],
            user_id=doc.get('user_id'),
            system_id=doc['system_id'],
            operation_details=doc.get('operation_details', {}),
            metadata=doc.get('metadata', {})
        )
    
    def _row_to_retention_policy(self, row: tuple) -> RetentionPolicy:
        """Convert database row to RetentionPolicy."""
        return RetentionPolicy(
            policy_id=row[0],
            name=row[1],
            description=row[2] or '',
            entity_types=row[3] or [],
            retention_period_days=row[4],
            action=row[5],
            conditions=row[6] or {},
            is_active=row[7],
            created_at=row[8],
            updated_at=row[9]
        )
    
    def _doc_to_retention_policy(self, doc: Dict[str, Any]) -> RetentionPolicy:
        """Convert MongoDB document to RetentionPolicy."""
        return RetentionPolicy(
            policy_id=doc['policy_id'],
            name=doc['name'],
            description=doc.get('description', ''),
            entity_types=doc.get('entity_types', []),
            retention_period_days=doc['retention_period_days'],
            action=doc['action'],
            conditions=doc.get('conditions', {}),
            is_active=doc.get('is_active', True),
            created_at=doc['created_at'],
            updated_at=doc['updated_at']
        )
    
    async def _scan_for_compliance_violations(self) -> None:
        """Scan recent data for compliance violations."""
        try:
            # This would scan recent lineage events for compliance issues
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)

            # Check for data processing without consent
            await self._check_consent_violations(recent_cutoff)

            # Check for data retention violations
            await self._check_retention_violations(recent_cutoff)

            # Check for unauthorized data access
            await self._check_access_violations(recent_cutoff)

        except Exception as e:
            self.logger.error(f"Failed to scan for compliance violations: {str(e)}")

    async def _check_retention_compliance(self) -> None:
        """Check compliance with retention policies."""
        try:
            for policy in self._retention_policies.values():
                if policy.is_active:
                    # Check if policy is being properly enforced
                    cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_period_days)
                    # Implementation would check for entities older than cutoff
                    pass
        except Exception as e:
            self.logger.error(f"Failed to check retention compliance: {str(e)}")

    async def _validate_lineage_completeness(self) -> None:
        """Validate that lineage tracking is complete."""
        try:
            # Check for gaps in lineage tracking
            # Implementation would verify all operations are properly tracked
            pass
        except Exception as e:
            self.logger.error(f"Failed to validate lineage completeness: {str(e)}")

    async def _delete_entity(self, entity_id: str) -> None:
        """Delete an entity and all its data."""
        try:
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based deletion
                await self.storage_connector.execute(
                    "DELETE FROM emails WHERE id = %s", (entity_id,)
                )
            elif hasattr(self.storage_connector, 'delete_one'):
                # MongoDB-based deletion
                await self.storage_connector.database.emails.delete_one({'id': entity_id})
        except Exception as e:
            self.logger.error(f"Failed to delete entity {entity_id}: {str(e)}")
            raise

    async def _archive_entity(self, entity_id: str) -> None:
        """Archive an entity to long-term storage."""
        try:
            if hasattr(self.storage_connector, 'execute'):
                # SQL-based archival
                await self.storage_connector.execute(
                    "UPDATE emails SET archived = TRUE, archived_at = %s WHERE id = %s",
                    (datetime.utcnow(), entity_id)
                )
            elif hasattr(self.storage_connector, 'update_one'):
                # MongoDB-based archival
                await self.storage_connector.database.emails.update_one(
                    {'id': entity_id},
                    {'$set': {'archived': True, 'archived_at': datetime.utcnow()}}
                )
        except Exception as e:
            self.logger.error(f"Failed to archive entity {entity_id}: {str(e)}")
            raise

    async def _anonymize_entity(self, entity_id: str) -> None:
        """Anonymize an entity by removing PII."""
        try:
            anonymized_data = {
                'sender_email': 'anonymized@example.com',
                'sender_name': 'Anonymized User',
                'subject': '[ANONYMIZED]',
                'body': '[CONTENT ANONYMIZED]',
                'anonymized': True,
                'anonymized_at': datetime.utcnow()
            }

            if hasattr(self.storage_connector, 'execute'):
                # SQL-based anonymization
                set_clause = ', '.join([f"{k} = %s" for k in anonymized_data.keys()])
                values = list(anonymized_data.values()) + [entity_id]
                await self.storage_connector.execute(
                    f"UPDATE emails SET {set_clause} WHERE id = %s", values
                )
            elif hasattr(self.storage_connector, 'update_one'):
                # MongoDB-based anonymization
                await self.storage_connector.database.emails.update_one(
                    {'id': entity_id},
                    {'$set': anonymized_data}
                )
        except Exception as e:
            self.logger.error(f"Failed to anonymize entity {entity_id}: {str(e)}")
            raise

    async def _evaluate_data_collection_rule(self, rule: ComplianceRule, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate data collection compliance rule."""
        conditions = rule.conditions

        # Check data minimization
        if 'max_retention_days' in conditions:
            if 'created_at' in entity_data:
                created_at = datetime.fromisoformat(entity_data['created_at'])
                age_days = (datetime.utcnow() - created_at).days
                if age_days > conditions['max_retention_days']:
                    return {
                        'passed': False,
                        'details': f"Data retained for {age_days} days, exceeds limit of {conditions['max_retention_days']}",
                        'violation_description': "Data retention period exceeded"
                    }

        return {'passed': True, 'details': 'Data collection rule passed'}

    async def _evaluate_consent_rule(self, rule: ComplianceRule, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate consent compliance rule."""
        conditions = rule.conditions

        if conditions.get('requires_consent', False):
            if not entity_data.get('consent_given', False):
                return {
                    'passed': False,
                    'details': 'No consent recorded for data processing',
                    'violation_description': 'Data processed without user consent'
                }

        return {'passed': True, 'details': 'Consent rule passed'}

    async def _evaluate_disclosure_rule(self, rule: ComplianceRule, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate disclosure compliance rule."""
        # Check if disclosure capabilities are available
        if not entity_data.get('disclosure_available', True):
            return {
                'passed': False,
                'details': 'Data disclosure capability not available',
                'violation_description': 'Cannot provide data disclosure to user'
            }

        return {'passed': True, 'details': 'Disclosure rule passed'}

    async def _evaluate_retention_rule(self, rule: ComplianceRule, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate retention compliance rule."""
        conditions = rule.conditions

        if 'max_retention_days' in conditions and 'created_at' in entity_data:
            created_at = datetime.fromisoformat(entity_data['created_at'])
            age_days = (datetime.utcnow() - created_at).days
            if age_days > conditions['max_retention_days']:
                return {
                    'passed': False,
                    'details': f"Data age {age_days} days exceeds retention limit",
                    'violation_description': 'Data retention period exceeded'
                }

        return {'passed': True, 'details': 'Retention rule passed'}

    async def _evaluate_anonymization_rule(self, rule: ComplianceRule, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate anonymization compliance rule."""
        conditions = rule.conditions

        if conditions.get('requires_anonymization', False):
            if not entity_data.get('anonymized', False):
                return {
                    'passed': False,
                    'details': 'Data requires anonymization but is not anonymized',
                    'violation_description': 'PII data not properly anonymized'
                }

        return {'passed': True, 'details': 'Anonymization rule passed'}

    async def _check_consent_violations(self, cutoff_date: datetime) -> None:
        """Check for consent violations in recent data."""
        try:
            # Query recent lineage events for consent-related operations
            if hasattr(self.storage_connector, 'execute'):
                query = """
                    SELECT entity_id, metadata FROM data_lineage
                    WHERE timestamp >= %s
                    AND event_type IN ('create', 'read', 'update')
                """
                results = await self.storage_connector.execute(query, (cutoff_date,))

                for entity_id, metadata in results:
                    # Check if consent was properly recorded
                    if not metadata.get('consent_verified', False):
                        self.logger.warning(f"Potential consent violation for entity {entity_id}")
                        self.stats['compliance_violations_detected'] += 1

        except Exception as e:
            self.logger.error(f"Failed to check consent violations: {str(e)}")

    async def _check_retention_violations(self, cutoff_date: datetime) -> None:
        """Check for retention policy violations."""
        try:
            # Check for data older than any retention policy allows
            for policy in self._retention_policies.values():
                if not policy.is_active:
                    continue

                policy_cutoff = datetime.utcnow() - timedelta(days=policy.retention_period_days)

                if hasattr(self.storage_connector, 'execute'):
                    query = """
                        SELECT COUNT(*) FROM emails
                        WHERE created_at < %s
                        AND entity_type = ANY(%s)
                    """
                    results = await self.storage_connector.execute(
                        query, (policy_cutoff, policy.entity_types)
                    )
                    violation_count = results[0][0] if results else 0

                    if violation_count > 0:
                        self.logger.warning(f"Retention policy violation: {violation_count} entities exceed retention period for policy {policy.name}")
                        self.stats['compliance_violations_detected'] += violation_count

        except Exception as e:
            self.logger.error(f"Failed to check retention violations: {str(e)}")

    async def _check_access_violations(self, cutoff_date: datetime) -> None:
        """Check for unauthorized data access."""
        try:
            # Check lineage events for unauthorized access patterns
            if hasattr(self.storage_connector, 'execute'):
                query = """
                    SELECT user_id, entity_id, COUNT(*) as access_count
                    FROM data_lineage
                    WHERE timestamp >= %s
                    AND event_type = 'read'
                    GROUP BY user_id, entity_id
                    HAVING COUNT(*) > 100
                """
                results = await self.storage_connector.execute(query, (cutoff_date,))

                for user_id, entity_id, access_count in results:
                    self.logger.warning(f"Potential access violation: User {user_id} accessed entity {entity_id} {access_count} times")
                    self.stats['compliance_violations_detected'] += 1

        except Exception as e:
            self.logger.error(f"Failed to check access violations: {str(e)}")

    async def get_governance_stats(self) -> Dict[str, Any]:
        """Get governance service statistics."""
        return {
            **self.stats,
            'is_initialized': self.is_initialized,
            'lineage_tracking_enabled': self.enable_lineage_tracking,
            'retention_policies_enabled': self.enable_retention_policies,
            'compliance_monitoring_enabled': self.enable_compliance_monitoring,
            'compliance_frameworks': self.compliance_frameworks,
            'active_retention_policies': len(self._retention_policies),
            'active_compliance_rules': len(self._compliance_rules),
            'pending_lineage_events': len(self._lineage_buffer)
        }
