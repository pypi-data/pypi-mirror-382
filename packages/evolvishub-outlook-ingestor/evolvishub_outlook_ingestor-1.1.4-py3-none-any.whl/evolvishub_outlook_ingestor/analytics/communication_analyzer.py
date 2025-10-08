"""
Communication pattern analysis for email data.

This module provides comprehensive analysis of email communication patterns,
including network analysis, centrality metrics, and communication behavior insights.
"""

import asyncio
import logging
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import networkx as nx
import numpy as np
from scipy import stats

from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAddress
from evolvishub_outlook_ingestor.core.exceptions import AnalyticsError

logger = logging.getLogger(__name__)


@dataclass
class CommunicationMetrics:
    """Communication metrics for an entity."""
    total_emails_sent: int
    total_emails_received: int
    unique_contacts: int
    response_rate: float
    average_response_time_hours: float
    communication_frequency: float
    centrality_score: float


@dataclass
class NetworkAnalysis:
    """Network analysis results."""
    total_nodes: int
    total_edges: int
    density: float
    average_clustering: float
    diameter: Optional[int]
    connected_components: int
    top_communicators: List[Tuple[str, CommunicationMetrics]]
    communication_clusters: List[List[str]]


@dataclass
class CommunicationPattern:
    """Communication pattern analysis results."""
    pattern_type: str
    participants: List[str]
    frequency: int
    time_distribution: Dict[str, int]
    strength: float
    description: str


class CommunicationAnalyzer:
    """
    Analyzes email communication patterns and networks using NetworkX.
    
    Provides comprehensive analysis of communication behavior including:
    - Network topology analysis
    - Centrality metrics calculation
    - Communication pattern detection
    - Response time analysis
    - Clustering and community detection
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the communication analyzer.
        
        Args:
            config: Configuration dictionary containing:
                - min_interactions: Minimum interactions for analysis (default: 2)
                - time_window_days: Analysis time window in days (default: 30)
                - clustering_algorithm: Algorithm for clustering (default: 'louvain')
                - centrality_metrics: List of centrality metrics to calculate
        """
        self.config = config
        self.min_interactions = config.get('min_interactions', 2)
        self.time_window_days = config.get('time_window_days', 30)
        self.clustering_algorithm = config.get('clustering_algorithm', 'louvain')
        self.centrality_metrics = config.get('centrality_metrics', [
            'degree', 'betweenness', 'closeness', 'eigenvector'
        ])
        
        self.communication_graph: Optional[nx.DiGraph] = None
        self.email_cache: List[EmailMessage] = []
        
    async def initialize(self) -> None:
        """Initialize the analyzer."""
        logger.info("Initializing CommunicationAnalyzer")
        self.communication_graph = nx.DiGraph()
        
    async def analyze_communication_patterns(
        self, 
        emails: List[EmailMessage],
        time_window: Optional[timedelta] = None
    ) -> List[CommunicationPattern]:
        """
        Analyze communication patterns from email data.
        
        Args:
            emails: List of email messages to analyze
            time_window: Optional time window for analysis
            
        Returns:
            List of detected communication patterns
            
        Raises:
            AnalyticsError: If analysis fails
        """
        try:
            if not emails:
                return []
                
            # Filter emails by time window if specified
            if time_window:
                cutoff_date = datetime.utcnow() - time_window
                emails = [
                    email for email in emails 
                    if email.received_date and email.received_date >= cutoff_date
                ]
            
            # Build communication network
            await self._build_communication_network(emails)
            
            # Detect patterns
            patterns = []
            
            # Detect frequent communication pairs
            frequent_pairs = await self._detect_frequent_pairs(emails)
            patterns.extend(frequent_pairs)
            
            # Detect broadcast patterns
            broadcast_patterns = await self._detect_broadcast_patterns(emails)
            patterns.extend(broadcast_patterns)
            
            # Detect response chains
            response_chains = await self._detect_response_chains(emails)
            patterns.extend(response_chains)
            
            # Detect time-based patterns
            time_patterns = await self._detect_time_patterns(emails)
            patterns.extend(time_patterns)
            
            logger.info(f"Detected {len(patterns)} communication patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Error analyzing communication patterns: {e}")
            raise AnalyticsError(f"Communication pattern analysis failed: {e}")
    
    async def build_network_graph(self, emails: List[EmailMessage]) -> NetworkAnalysis:
        """
        Build and analyze communication network graph.
        
        Args:
            emails: List of email messages
            
        Returns:
            Network analysis results
        """
        try:
            await self._build_communication_network(emails)
            
            if not self.communication_graph:
                raise AnalyticsError("Communication graph not initialized")
            
            # Calculate network metrics
            total_nodes = self.communication_graph.number_of_nodes()
            total_edges = self.communication_graph.number_of_edges()
            
            if total_nodes == 0:
                return NetworkAnalysis(
                    total_nodes=0, total_edges=0, density=0.0,
                    average_clustering=0.0, diameter=None,
                    connected_components=0, top_communicators=[],
                    communication_clusters=[]
                )
            
            # Convert to undirected for some metrics
            undirected_graph = self.communication_graph.to_undirected()
            
            density = nx.density(self.communication_graph)
            average_clustering = nx.average_clustering(undirected_graph)
            
            # Calculate diameter for largest connected component
            diameter = None
            if nx.is_connected(undirected_graph):
                diameter = nx.diameter(undirected_graph)
            else:
                # Get largest connected component
                largest_cc = max(nx.connected_components(undirected_graph), key=len)
                if len(largest_cc) > 1:
                    subgraph = undirected_graph.subgraph(largest_cc)
                    diameter = nx.diameter(subgraph)
            
            connected_components = nx.number_connected_components(undirected_graph)
            
            # Calculate centrality metrics and identify top communicators
            top_communicators = await self._calculate_top_communicators(emails)
            
            # Detect communication clusters
            clusters = await self._detect_communication_clusters()
            
            return NetworkAnalysis(
                total_nodes=total_nodes,
                total_edges=total_edges,
                density=density,
                average_clustering=average_clustering,
                diameter=diameter,
                connected_components=connected_components,
                top_communicators=top_communicators,
                communication_clusters=clusters
            )
            
        except Exception as e:
            logger.error(f"Error building network graph: {e}")
            raise AnalyticsError(f"Network graph analysis failed: {e}")
    
    async def calculate_centrality_metrics(
        self, 
        email_address: str
    ) -> Dict[str, float]:
        """
        Calculate centrality metrics for a specific email address.
        
        Args:
            email_address: Email address to analyze
            
        Returns:
            Dictionary of centrality metrics
        """
        try:
            if not self.communication_graph or email_address not in self.communication_graph:
                return {}
            
            metrics = {}
            
            # Degree centrality
            if 'degree' in self.centrality_metrics:
                degree_centrality = nx.degree_centrality(self.communication_graph)
                metrics['degree_centrality'] = degree_centrality.get(email_address, 0.0)
            
            # Betweenness centrality
            if 'betweenness' in self.centrality_metrics:
                betweenness_centrality = nx.betweenness_centrality(self.communication_graph)
                metrics['betweenness_centrality'] = betweenness_centrality.get(email_address, 0.0)
            
            # Closeness centrality
            if 'closeness' in self.centrality_metrics:
                closeness_centrality = nx.closeness_centrality(self.communication_graph)
                metrics['closeness_centrality'] = closeness_centrality.get(email_address, 0.0)
            
            # Eigenvector centrality
            if 'eigenvector' in self.centrality_metrics:
                try:
                    eigenvector_centrality = nx.eigenvector_centrality(self.communication_graph)
                    metrics['eigenvector_centrality'] = eigenvector_centrality.get(email_address, 0.0)
                except nx.PowerIterationFailedConvergence:
                    metrics['eigenvector_centrality'] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating centrality metrics: {e}")
            return {}
    
    async def _build_communication_network(self, emails: List[EmailMessage]) -> None:
        """Build the communication network from emails."""
        if not self.communication_graph:
            self.communication_graph = nx.DiGraph()
        
        # Track interactions
        interactions = defaultdict(int)
        
        for email in emails:
            if not email.sender:
                continue
                
            sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
            
            # Add edges for each recipient
            all_recipients = []
            if email.to_recipients:
                all_recipients.extend([
                    r.email if isinstance(r, EmailAddress) else str(r) 
                    for r in email.to_recipients
                ])
            if email.cc_recipients:
                all_recipients.extend([
                    r.email if isinstance(r, EmailAddress) else str(r) 
                    for r in email.cc_recipients
                ])
            
            for recipient in all_recipients:
                if sender != recipient:  # Avoid self-loops
                    interactions[(sender, recipient)] += 1
        
        # Add edges with weights
        for (sender, recipient), weight in interactions.items():
            if weight >= self.min_interactions:
                self.communication_graph.add_edge(sender, recipient, weight=weight)
    
    async def _detect_frequent_pairs(self, emails: List[EmailMessage]) -> List[CommunicationPattern]:
        """Detect frequently communicating pairs."""
        patterns = []
        
        # Count interactions between pairs
        pair_interactions = defaultdict(int)
        
        for email in emails:
            if not email.sender:
                continue
                
            sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
            
            all_recipients = []
            if email.to_recipients:
                all_recipients.extend([
                    r.email if isinstance(r, EmailAddress) else str(r) 
                    for r in email.to_recipients
                ])
            
            for recipient in all_recipients:
                if sender != recipient:
                    pair_key = tuple(sorted([sender, recipient]))
                    pair_interactions[pair_key] += 1
        
        # Identify frequent pairs (top 10% or minimum threshold)
        if pair_interactions:
            threshold = max(5, np.percentile(list(pair_interactions.values()), 90))
            
            for (person1, person2), frequency in pair_interactions.items():
                if frequency >= threshold:
                    patterns.append(CommunicationPattern(
                        pattern_type="frequent_pair",
                        participants=[person1, person2],
                        frequency=frequency,
                        time_distribution={},
                        strength=frequency / max(pair_interactions.values()),
                        description=f"Frequent communication between {person1} and {person2}"
                    ))
        
        return patterns
    
    async def _detect_broadcast_patterns(self, emails: List[EmailMessage]) -> List[CommunicationPattern]:
        """Detect broadcast communication patterns."""
        patterns = []
        
        # Group emails by sender and look for large recipient lists
        sender_broadcasts = defaultdict(list)
        
        for email in emails:
            if not email.sender:
                continue
                
            sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
            recipient_count = len(email.to_recipients or []) + len(email.cc_recipients or [])
            
            if recipient_count >= 5:  # Threshold for broadcast
                sender_broadcasts[sender].append(recipient_count)
        
        # Identify frequent broadcasters
        for sender, broadcast_sizes in sender_broadcasts.items():
            if len(broadcast_sizes) >= 3:  # At least 3 broadcast emails
                avg_size = np.mean(broadcast_sizes)
                patterns.append(CommunicationPattern(
                    pattern_type="broadcast",
                    participants=[sender],
                    frequency=len(broadcast_sizes),
                    time_distribution={},
                    strength=min(1.0, avg_size / 20),  # Normalize by typical max
                    description=f"Broadcast pattern from {sender} (avg {avg_size:.1f} recipients)"
                ))
        
        return patterns
    
    async def _detect_response_chains(self, emails: List[EmailMessage]) -> List[CommunicationPattern]:
        """Detect email response chains."""
        patterns = []
        
        # Group emails by conversation ID or subject
        conversations = defaultdict(list)
        
        for email in emails:
            key = email.conversation_id or email.subject or "unknown"
            conversations[key].append(email)
        
        # Analyze conversations with multiple emails
        for conv_id, conv_emails in conversations.items():
            if len(conv_emails) >= 3:  # At least 3 emails in chain
                # Sort by date
                conv_emails.sort(key=lambda e: e.received_date or datetime.min)
                
                participants = set()
                for email in conv_emails:
                    if email.sender:
                        sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
                        participants.add(sender)
                
                if len(participants) >= 2:
                    patterns.append(CommunicationPattern(
                        pattern_type="response_chain",
                        participants=list(participants),
                        frequency=len(conv_emails),
                        time_distribution={},
                        strength=min(1.0, len(conv_emails) / 10),
                        description=f"Response chain with {len(participants)} participants"
                    ))
        
        return patterns
    
    async def _detect_time_patterns(self, emails: List[EmailMessage]) -> List[CommunicationPattern]:
        """Detect time-based communication patterns."""
        patterns = []
        
        # Analyze hourly distribution
        hourly_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        
        for email in emails:
            if email.received_date:
                hour = email.received_date.hour
                day = email.received_date.weekday()
                hourly_counts[hour] += 1
                daily_counts[day] += 1
        
        # Detect peak hours
        if hourly_counts:
            peak_hour = max(hourly_counts.keys(), key=lambda h: hourly_counts[h])
            peak_count = hourly_counts[peak_hour]
            avg_count = np.mean(list(hourly_counts.values()))
            
            if peak_count > avg_count * 1.5:  # 50% above average
                patterns.append(CommunicationPattern(
                    pattern_type="peak_hour",
                    participants=[],
                    frequency=peak_count,
                    time_distribution=dict(hourly_counts),
                    strength=peak_count / sum(hourly_counts.values()),
                    description=f"Peak communication at hour {peak_hour}"
                ))
        
        return patterns
    
    async def _calculate_top_communicators(
        self, 
        emails: List[EmailMessage]
    ) -> List[Tuple[str, CommunicationMetrics]]:
        """Calculate top communicators based on various metrics."""
        communicator_stats = defaultdict(lambda: {
            'sent': 0, 'received': 0, 'contacts': set(),
            'response_times': [], 'last_activity': None
        })
        
        # Collect statistics
        for email in emails:
            if not email.sender:
                continue
                
            sender = email.sender.email if isinstance(email.sender, EmailAddress) else str(email.sender)
            communicator_stats[sender]['sent'] += 1
            communicator_stats[sender]['last_activity'] = email.received_date
            
            # Track recipients as contacts
            all_recipients = []
            if email.to_recipients:
                all_recipients.extend([
                    r.email if isinstance(r, EmailAddress) else str(r) 
                    for r in email.to_recipients
                ])
            if email.cc_recipients:
                all_recipients.extend([
                    r.email if isinstance(r, EmailAddress) else str(r) 
                    for r in email.cc_recipients
                ])
            
            for recipient in all_recipients:
                communicator_stats[sender]['contacts'].add(recipient)
                communicator_stats[recipient]['received'] += 1
        
        # Calculate metrics and create top communicators list
        top_communicators = []
        
        for email_addr, stats in communicator_stats.items():
            if stats['sent'] + stats['received'] < self.min_interactions:
                continue
            
            # Calculate centrality if available
            centrality_score = 0.0
            if self.communication_graph and email_addr in self.communication_graph:
                centrality_metrics = await self.calculate_centrality_metrics(email_addr)
                centrality_score = centrality_metrics.get('degree_centrality', 0.0)
            
            metrics = CommunicationMetrics(
                total_emails_sent=stats['sent'],
                total_emails_received=stats['received'],
                unique_contacts=len(stats['contacts']),
                response_rate=0.0,  # Would need more complex analysis
                average_response_time_hours=0.0,  # Would need conversation threading
                communication_frequency=stats['sent'] + stats['received'],
                centrality_score=centrality_score
            )
            
            top_communicators.append((email_addr, metrics))
        
        # Sort by communication frequency and return top 10
        top_communicators.sort(key=lambda x: x[1].communication_frequency, reverse=True)
        return top_communicators[:10]
    
    async def _detect_communication_clusters(self) -> List[List[str]]:
        """Detect communication clusters using community detection."""
        if not self.communication_graph:
            return []
        
        try:
            # Convert to undirected for community detection
            undirected_graph = self.communication_graph.to_undirected()
            
            if undirected_graph.number_of_nodes() < 3:
                return []
            
            # Use Louvain algorithm for community detection
            import networkx.algorithms.community as nx_comm
            communities = nx_comm.louvain_communities(undirected_graph)
            
            # Convert to list of lists and filter small communities
            clusters = [list(community) for community in communities if len(community) >= 3]
            
            return clusters
            
        except Exception as e:
            logger.warning(f"Community detection failed: {e}")
            return []
