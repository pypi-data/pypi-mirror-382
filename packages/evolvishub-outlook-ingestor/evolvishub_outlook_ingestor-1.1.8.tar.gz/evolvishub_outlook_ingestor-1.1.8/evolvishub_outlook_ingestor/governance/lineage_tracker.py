"""
Data lineage tracking and impact analysis.

This module provides comprehensive data lineage tracking capabilities with
graph-based storage, transformation tracking, and impact analysis.
"""

import asyncio
import json
import logging
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import networkx as nx

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import GovernanceError

logger = logging.getLogger(__name__)


class LineageEventType(Enum):
    """Types of lineage events."""
    CREATED = "created"
    TRANSFORMED = "transformed"
    MERGED = "merged"
    SPLIT = "split"
    DELETED = "deleted"
    ACCESSED = "accessed"
    EXPORTED = "exported"
    ARCHIVED = "archived"


@dataclass
class LineageRecord:
    """A single lineage record."""
    id: str
    entity_id: str
    event_type: LineageEventType
    timestamp: datetime
    source_entities: List[str]
    target_entities: List[str]
    transformation_type: Optional[str]
    transformation_details: Dict[str, Any]
    user_id: Optional[str]
    system_id: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['event_type'] = self.event_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class LineageNode:
    """A node in the lineage graph."""
    entity_id: str
    entity_type: str
    created_at: datetime
    last_modified: datetime
    properties: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat(),
            'properties': self.properties
        }


@dataclass
class LineageEdge:
    """An edge in the lineage graph."""
    source_id: str
    target_id: str
    relationship_type: str
    created_at: datetime
    properties: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relationship_type': self.relationship_type,
            'created_at': self.created_at.isoformat(),
            'properties': self.properties
        }


@dataclass
class LineageGraph:
    """Complete lineage graph representation."""
    nodes: List[LineageNode]
    edges: List[LineageEdge]
    root_entity: str
    depth: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'nodes': [node.to_dict() for node in self.nodes],
            'edges': [edge.to_dict() for edge in self.edges],
            'root_entity': self.root_entity,
            'depth': self.depth
        }


@dataclass
class ImpactAnalysis:
    """Impact analysis results."""
    entity_id: str
    downstream_entities: List[str]
    upstream_entities: List[str]
    impact_score: float
    affected_systems: List[str]
    risk_level: str
    recommendations: List[str]


class LineageTracker:
    """
    Tracks data lineage and transformation history using graph-based storage.
    
    Provides comprehensive lineage tracking including:
    - Graph-based lineage storage using NetworkX
    - Transformation tracking and history
    - Impact analysis for data changes
    - Lineage visualization and reporting
    - Compliance and audit trail support
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the lineage tracker.
        
        Args:
            config: Configuration dictionary containing:
                - storage_backend: Storage backend ('memory', 'database', 'file')
                - max_depth: Maximum lineage depth to track (default: 10)
                - retention_days: Lineage retention period (default: 365)
                - enable_impact_analysis: Enable impact analysis (default: True)
        """
        self.config = config
        self.storage_backend = config.get('storage_backend', 'memory')
        self.max_depth = config.get('max_depth', 10)
        self.retention_days = config.get('retention_days', 365)
        self.enable_impact_analysis = config.get('enable_impact_analysis', True)
        
        # In-memory storage (for demonstration)
        self.lineage_graph = nx.DiGraph()
        self.lineage_records: List[LineageRecord] = []
        self.entity_metadata: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> None:
        """Initialize the lineage tracker."""
        logger.info("Initializing LineageTracker")
        
        if self.storage_backend == 'database':
            await self._initialize_database()
        elif self.storage_backend == 'file':
            await self._initialize_file_storage()
        
    async def track_lineage(
        self, 
        entity_id: str, 
        event_type: LineageEventType,
        source_entities: Optional[List[str]] = None,
        target_entities: Optional[List[str]] = None,
        transformation_type: Optional[str] = None,
        transformation_details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Track a lineage event.
        
        Args:
            entity_id: ID of the entity being tracked
            event_type: Type of lineage event
            source_entities: List of source entity IDs
            target_entities: List of target entity IDs
            transformation_type: Type of transformation applied
            transformation_details: Details about the transformation
            user_id: ID of the user performing the action
            metadata: Additional metadata
            
        Returns:
            Lineage record ID
            
        Raises:
            GovernanceError: If lineage tracking fails
        """
        try:
            record_id = str(uuid.uuid4())
            
            lineage_record = LineageRecord(
                id=record_id,
                entity_id=entity_id,
                event_type=event_type,
                timestamp=datetime.utcnow(),
                source_entities=source_entities or [],
                target_entities=target_entities or [],
                transformation_type=transformation_type,
                transformation_details=transformation_details or {},
                user_id=user_id,
                system_id=self.config.get('system_id', 'outlook_ingestor'),
                metadata=metadata or {}
            )
            
            # Store the record
            await self._store_lineage_record(lineage_record)
            
            # Update the lineage graph
            await self._update_lineage_graph(lineage_record)
            
            logger.debug(f"Tracked lineage event {event_type.value} for entity {entity_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error tracking lineage: {e}")
            raise GovernanceError(f"Lineage tracking failed: {e}")
    
    async def get_lineage_graph(
        self, 
        entity_id: str, 
        depth: Optional[int] = None,
        direction: str = 'both'
    ) -> LineageGraph:
        """
        Retrieve lineage graph for an entity.
        
        Args:
            entity_id: Entity ID to get lineage for
            depth: Maximum depth to traverse (default: max_depth)
            direction: Direction to traverse ('upstream', 'downstream', 'both')
            
        Returns:
            Lineage graph
        """
        try:
            if depth is None:
                depth = self.max_depth
            
            nodes = []
            edges = []
            visited = set()
            
            # Build the lineage graph
            await self._build_lineage_graph_recursive(
                entity_id, nodes, edges, visited, depth, direction
            )
            
            return LineageGraph(
                nodes=nodes,
                edges=edges,
                root_entity=entity_id,
                depth=depth
            )
            
        except Exception as e:
            logger.error(f"Error getting lineage graph: {e}")
            raise GovernanceError(f"Lineage graph retrieval failed: {e}")
    
    async def analyze_impact(self, entity_id: str) -> ImpactAnalysis:
        """
        Analyze the impact of changes to an entity.
        
        Args:
            entity_id: Entity ID to analyze
            
        Returns:
            Impact analysis results
        """
        try:
            if not self.enable_impact_analysis:
                return ImpactAnalysis(
                    entity_id=entity_id,
                    downstream_entities=[],
                    upstream_entities=[],
                    impact_score=0.0,
                    affected_systems=[],
                    risk_level='unknown',
                    recommendations=[]
                )
            
            # Get downstream entities (entities that depend on this one)
            downstream_entities = await self._get_downstream_entities(entity_id)
            
            # Get upstream entities (entities this one depends on)
            upstream_entities = await self._get_upstream_entities(entity_id)
            
            # Calculate impact score
            impact_score = await self._calculate_impact_score(entity_id, downstream_entities)
            
            # Identify affected systems
            affected_systems = await self._identify_affected_systems(downstream_entities)
            
            # Determine risk level
            risk_level = await self._determine_risk_level(impact_score, len(downstream_entities))
            
            # Generate recommendations
            recommendations = await self._generate_impact_recommendations(
                entity_id, downstream_entities, risk_level
            )
            
            return ImpactAnalysis(
                entity_id=entity_id,
                downstream_entities=downstream_entities,
                upstream_entities=upstream_entities,
                impact_score=impact_score,
                affected_systems=affected_systems,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing impact: {e}")
            raise GovernanceError(f"Impact analysis failed: {e}")
    
    async def get_lineage_history(
        self, 
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[LineageRecord]:
        """
        Get lineage history for an entity.
        
        Args:
            entity_id: Entity ID
            start_date: Start date for history
            end_date: End date for history
            
        Returns:
            List of lineage records
        """
        try:
            records = []
            
            for record in self.lineage_records:
                if record.entity_id == entity_id:
                    # Apply date filters
                    if start_date and record.timestamp < start_date:
                        continue
                    if end_date and record.timestamp > end_date:
                        continue
                    
                    records.append(record)
            
            # Sort by timestamp
            records.sort(key=lambda r: r.timestamp)
            
            return records
            
        except Exception as e:
            logger.error(f"Error getting lineage history: {e}")
            raise GovernanceError(f"Lineage history retrieval failed: {e}")
    
    async def track_email_lineage(self, email: EmailMessage, operation: str) -> str:
        """
        Track lineage for email operations.
        
        Args:
            email: Email message
            operation: Operation performed on the email
            
        Returns:
            Lineage record ID
        """
        try:
            # Determine event type based on operation
            event_type_mapping = {
                'ingest': LineageEventType.CREATED,
                'transform': LineageEventType.TRANSFORMED,
                'merge': LineageEventType.MERGED,
                'export': LineageEventType.EXPORTED,
                'archive': LineageEventType.ARCHIVED,
                'delete': LineageEventType.DELETED
            }
            
            event_type = event_type_mapping.get(operation, LineageEventType.TRANSFORMED)
            
            # Extract metadata
            metadata = {
                'subject': email.subject,
                'sender': email.sender.email if hasattr(email.sender, 'email') else str(email.sender) if email.sender else None,
                'received_date': email.received_date.isoformat() if email.received_date else None,
                'has_attachments': email.has_attachments,
                'operation': operation
            }
            
            # Track the lineage
            return await self.track_lineage(
                entity_id=email.id,
                event_type=event_type,
                transformation_type=operation,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error tracking email lineage: {e}")
            raise GovernanceError(f"Email lineage tracking failed: {e}")
    
    async def _store_lineage_record(self, record: LineageRecord) -> None:
        """Store a lineage record."""
        if self.storage_backend == 'memory':
            self.lineage_records.append(record)
        elif self.storage_backend == 'database':
            await self._store_record_to_database(record)
        elif self.storage_backend == 'file':
            await self._store_record_to_file(record)
    
    async def _update_lineage_graph(self, record: LineageRecord) -> None:
        """Update the lineage graph with a new record."""
        # Add the entity as a node if it doesn't exist
        if not self.lineage_graph.has_node(record.entity_id):
            self.lineage_graph.add_node(
                record.entity_id,
                entity_type='email',
                created_at=record.timestamp,
                last_modified=record.timestamp,
                properties=record.metadata
            )
        else:
            # Update last modified time
            self.lineage_graph.nodes[record.entity_id]['last_modified'] = record.timestamp
        
        # Add edges for source relationships
        for source_id in record.source_entities:
            if not self.lineage_graph.has_node(source_id):
                self.lineage_graph.add_node(source_id, entity_type='unknown')
            
            self.lineage_graph.add_edge(
                source_id,
                record.entity_id,
                relationship_type=record.transformation_type or 'derived_from',
                created_at=record.timestamp,
                properties=record.transformation_details
            )
        
        # Add edges for target relationships
        for target_id in record.target_entities:
            if not self.lineage_graph.has_node(target_id):
                self.lineage_graph.add_node(target_id, entity_type='unknown')
            
            self.lineage_graph.add_edge(
                record.entity_id,
                target_id,
                relationship_type=record.transformation_type or 'produces',
                created_at=record.timestamp,
                properties=record.transformation_details
            )
    
    async def _build_lineage_graph_recursive(
        self,
        entity_id: str,
        nodes: List[LineageNode],
        edges: List[LineageEdge],
        visited: Set[str],
        remaining_depth: int,
        direction: str
    ) -> None:
        """Recursively build lineage graph."""
        if entity_id in visited or remaining_depth <= 0:
            return
        
        visited.add(entity_id)
        
        # Add the current node
        if self.lineage_graph.has_node(entity_id):
            node_data = self.lineage_graph.nodes[entity_id]
            nodes.append(LineageNode(
                entity_id=entity_id,
                entity_type=node_data.get('entity_type', 'unknown'),
                created_at=node_data.get('created_at', datetime.utcnow()),
                last_modified=node_data.get('last_modified', datetime.utcnow()),
                properties=node_data.get('properties', {})
            ))
        
        # Traverse based on direction
        if direction in ['upstream', 'both']:
            # Get predecessors (upstream)
            for predecessor in self.lineage_graph.predecessors(entity_id):
                edge_data = self.lineage_graph.edges[predecessor, entity_id]
                edges.append(LineageEdge(
                    source_id=predecessor,
                    target_id=entity_id,
                    relationship_type=edge_data.get('relationship_type', 'unknown'),
                    created_at=edge_data.get('created_at', datetime.utcnow()),
                    properties=edge_data.get('properties', {})
                ))
                
                await self._build_lineage_graph_recursive(
                    predecessor, nodes, edges, visited, remaining_depth - 1, direction
                )
        
        if direction in ['downstream', 'both']:
            # Get successors (downstream)
            for successor in self.lineage_graph.successors(entity_id):
                edge_data = self.lineage_graph.edges[entity_id, successor]
                edges.append(LineageEdge(
                    source_id=entity_id,
                    target_id=successor,
                    relationship_type=edge_data.get('relationship_type', 'unknown'),
                    created_at=edge_data.get('created_at', datetime.utcnow()),
                    properties=edge_data.get('properties', {})
                ))
                
                await self._build_lineage_graph_recursive(
                    successor, nodes, edges, visited, remaining_depth - 1, direction
                )
    
    async def _get_downstream_entities(self, entity_id: str) -> List[str]:
        """Get all downstream entities."""
        if not self.lineage_graph.has_node(entity_id):
            return []
        
        # Use DFS to find all reachable nodes
        downstream = []
        visited = set()
        
        def dfs(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            
            for successor in self.lineage_graph.successors(node_id):
                downstream.append(successor)
                dfs(successor)
        
        dfs(entity_id)
        return downstream
    
    async def _get_upstream_entities(self, entity_id: str) -> List[str]:
        """Get all upstream entities."""
        if not self.lineage_graph.has_node(entity_id):
            return []
        
        # Use DFS to find all reachable nodes in reverse direction
        upstream = []
        visited = set()
        
        def dfs(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            
            for predecessor in self.lineage_graph.predecessors(node_id):
                upstream.append(predecessor)
                dfs(predecessor)
        
        dfs(entity_id)
        return upstream
    
    async def _calculate_impact_score(self, entity_id: str, downstream_entities: List[str]) -> float:
        """Calculate impact score based on downstream dependencies."""
        # Simple scoring based on number of downstream entities
        base_score = len(downstream_entities) * 0.1
        
        # Weight by entity types and criticality
        weighted_score = base_score
        for downstream_id in downstream_entities:
            if self.lineage_graph.has_node(downstream_id):
                node_data = self.lineage_graph.nodes[downstream_id]
                entity_type = node_data.get('entity_type', 'unknown')
                
                # Apply weights based on entity type
                if entity_type == 'report':
                    weighted_score += 0.5
                elif entity_type == 'dashboard':
                    weighted_score += 0.3
                elif entity_type == 'export':
                    weighted_score += 0.2
        
        return min(10.0, weighted_score)  # Cap at 10.0
    
    async def _identify_affected_systems(self, downstream_entities: List[str]) -> List[str]:
        """Identify systems affected by downstream entities."""
        systems = set()
        
        for entity_id in downstream_entities:
            if self.lineage_graph.has_node(entity_id):
                node_data = self.lineage_graph.nodes[entity_id]
                system_id = node_data.get('properties', {}).get('system_id')
                if system_id:
                    systems.add(system_id)
        
        return list(systems)
    
    async def _determine_risk_level(self, impact_score: float, downstream_count: int) -> str:
        """Determine risk level based on impact score and downstream count."""
        if impact_score >= 7.0 or downstream_count >= 20:
            return 'critical'
        elif impact_score >= 4.0 or downstream_count >= 10:
            return 'high'
        elif impact_score >= 2.0 or downstream_count >= 5:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_impact_recommendations(
        self, 
        entity_id: str, 
        downstream_entities: List[str], 
        risk_level: str
    ) -> List[str]:
        """Generate recommendations based on impact analysis."""
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.extend([
                "Implement comprehensive testing before making changes",
                "Notify all stakeholders of potential impact",
                "Consider phased rollout approach",
                "Prepare rollback procedures"
            ])
        elif risk_level == 'high':
            recommendations.extend([
                "Test changes in staging environment",
                "Notify key stakeholders",
                "Monitor downstream systems after changes"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Review downstream dependencies",
                "Test critical paths"
            ])
        else:
            recommendations.append("Standard change management procedures apply")
        
        if len(downstream_entities) > 10:
            recommendations.append("Consider impact on large number of dependent entities")
        
        return recommendations
    
    async def _initialize_database(self) -> None:
        """Initialize database storage."""
        # Placeholder for database initialization
        logger.info("Database storage not implemented - using memory storage")
    
    async def _initialize_file_storage(self) -> None:
        """Initialize file storage."""
        # Placeholder for file storage initialization
        logger.info("File storage not implemented - using memory storage")
    
    async def _store_record_to_database(self, record: LineageRecord) -> None:
        """Store record to database."""
        # Placeholder for database storage
        pass
    
    async def _store_record_to_file(self, record: LineageRecord) -> None:
        """Store record to file."""
        # Placeholder for file storage
        pass
