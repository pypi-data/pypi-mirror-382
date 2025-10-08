"""
Advanced analytics engine for email data insights.

This module provides comprehensive analytics capabilities including
communication patterns, network analysis, trends, and business insights.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
import statistics

from evolvishub_outlook_ingestor.core.interfaces import IAnalyticsEngine, service_registry
from evolvishub_outlook_ingestor.core.data_models import EmailMessage, EmailAddress
from evolvishub_outlook_ingestor.core.exceptions import AnalyticsError


@dataclass
class CommunicationPattern:
    """Represents a communication pattern analysis result."""
    sender: str
    recipient: str
    email_count: int
    avg_response_time: Optional[float]
    communication_frequency: str
    relationship_strength: float


@dataclass
class TrendAnalysis:
    """Represents trend analysis results."""
    metric_name: str
    time_period: str
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: float  # 0.0 to 1.0
    data_points: List[Tuple[datetime, float]]
    forecast: Optional[List[Tuple[datetime, float]]]


@dataclass
class AnomalyDetection:
    """Represents anomaly detection results."""
    anomaly_type: str
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    timestamp: datetime
    affected_entities: List[str]
    confidence_score: float


class AnalyticsEngine(IAnalyticsEngine):
    """
    Advanced analytics engine for email data insights.
    
    This engine provides comprehensive analytics capabilities including:
    - Communication pattern analysis and network mapping
    - Time-based trend analysis and forecasting
    - Anomaly detection for unusual patterns
    - Business insights and KPI generation
    - Sentiment analysis across communications
    
    Example:
        ```python
        analytics = AnalyticsEngine({
            'enable_network_analysis': True,
            'enable_trend_analysis': True,
            'enable_anomaly_detection': True,
            'analysis_window_days': 30
        })
        
        await analytics.initialize()
        
        patterns = await analytics.analyze_communication_patterns(emails)
        insights = await analytics.generate_insights(emails)
        anomalies = await analytics.detect_anomalies(emails)
        ```
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.enable_network_analysis = config.get('enable_network_analysis', True)
        self.enable_trend_analysis = config.get('enable_trend_analysis', True)
        self.enable_anomaly_detection = config.get('enable_anomaly_detection', True)
        self.analysis_window_days = config.get('analysis_window_days', 30)
        self.min_emails_for_pattern = config.get('min_emails_for_pattern', 5)
        self.anomaly_threshold = config.get('anomaly_threshold', 2.0)  # Standard deviations
        
        # State management
        self.is_initialized = False
        self._communication_graph = defaultdict(lambda: defaultdict(list))
        self._email_metrics = defaultdict(list)
        self._baseline_metrics = {}
        
        # Analytics cache
        self._analysis_cache = {}
        self._cache_ttl = config.get('cache_ttl_minutes', 60)
        
        # Statistics
        self.stats = {
            'emails_analyzed': 0,
            'patterns_detected': 0,
            'anomalies_detected': 0,
            'insights_generated': 0
        }
    
    async def initialize(self) -> None:
        """Initialize the analytics engine."""
        if self.is_initialized:
            return
        
        try:
            self.logger.info("Initializing analytics engine")
            
            # Initialize analytics components
            if self.enable_network_analysis:
                await self._initialize_network_analysis()
            
            if self.enable_trend_analysis:
                await self._initialize_trend_analysis()
            
            if self.enable_anomaly_detection:
                await self._initialize_anomaly_detection()
            
            self.is_initialized = True
            self.logger.info("Analytics engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize analytics engine: {str(e)}")
            raise AnalyticsError(f"Analytics initialization failed: {str(e)}")
    
    async def analyze_communication_patterns(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """
        Analyze communication patterns from email data.
        
        Args:
            emails: List of email messages to analyze
            
        Returns:
            Dictionary containing communication pattern analysis
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Build communication graph
            communication_graph = defaultdict(lambda: defaultdict(int))
            response_times = defaultdict(list)
            
            # Sort emails by timestamp for response time analysis
            sorted_emails = sorted(emails, key=lambda e: e.received_date or datetime.min)
            
            for email in sorted_emails:
                if not email.sender or not email.sender.email:
                    continue
                
                sender = email.sender.email
                
                # Track communications to recipients
                for recipient in email.to_recipients + email.cc_recipients:
                    if recipient.email:
                        communication_graph[sender][recipient.email] += 1
                
                # Calculate response times for threaded conversations
                if email.in_reply_to:
                    # Find original email in the list
                    for orig_email in sorted_emails:
                        if (orig_email.message_id == email.in_reply_to and 
                            orig_email.received_date and email.received_date):
                            response_time = (email.received_date - orig_email.received_date).total_seconds()
                            response_times[sender].append(response_time)
                            break
            
            # Generate communication patterns
            patterns = []
            for sender, recipients in communication_graph.items():
                for recipient, count in recipients.items():
                    if count >= self.min_emails_for_pattern:
                        avg_response_time = None
                        if sender in response_times and response_times[sender]:
                            avg_response_time = statistics.mean(response_times[sender])
                        
                        # Determine communication frequency
                        frequency = self._categorize_frequency(count, len(emails))
                        
                        # Calculate relationship strength (0.0 to 1.0)
                        max_count = max(max(r.values()) for r in communication_graph.values())
                        relationship_strength = count / max_count if max_count > 0 else 0.0
                        
                        patterns.append(CommunicationPattern(
                            sender=sender,
                            recipient=recipient,
                            email_count=count,
                            avg_response_time=avg_response_time,
                            communication_frequency=frequency,
                            relationship_strength=relationship_strength
                        ))
            
            # Sort patterns by relationship strength
            patterns.sort(key=lambda p: p.relationship_strength, reverse=True)
            
            self.stats['emails_analyzed'] += len(emails)
            self.stats['patterns_detected'] += len(patterns)
            
            return {
                'total_patterns': len(patterns),
                'top_patterns': patterns[:20],  # Top 20 patterns
                'network_metrics': await self._calculate_network_metrics(communication_graph),
                'response_time_stats': await self._calculate_response_time_stats(response_times),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze communication patterns: {str(e)}")
            raise AnalyticsError(f"Communication pattern analysis failed: {str(e)}")
    
    async def generate_insights(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """
        Generate business insights from email data.
        
        Args:
            emails: List of email messages to analyze
            
        Returns:
            Dictionary containing generated insights
        """
        if not emails:
            return {'insights': [], 'summary': 'No emails to analyze'}
        
        try:
            insights = []
            
            # Email volume insights
            volume_insights = await self._analyze_email_volume(emails)
            insights.extend(volume_insights)
            
            # Time-based insights
            time_insights = await self._analyze_time_patterns(emails)
            insights.extend(time_insights)
            
            # Content insights
            content_insights = await self._analyze_content_patterns(emails)
            insights.extend(content_insights)
            
            # Collaboration insights
            collaboration_insights = await self._analyze_collaboration_patterns(emails)
            insights.extend(collaboration_insights)
            
            # Priority insights
            priority_insights = await self._analyze_priority_patterns(emails)
            insights.extend(priority_insights)
            
            self.stats['insights_generated'] += len(insights)
            
            return {
                'total_insights': len(insights),
                'insights': insights,
                'summary': await self._generate_insights_summary(insights),
                'analysis_period': {
                    'start': min(e.received_date for e in emails if e.received_date).isoformat(),
                    'end': max(e.received_date for e in emails if e.received_date).isoformat(),
                    'total_emails': len(emails)
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate insights: {str(e)}")
            raise AnalyticsError(f"Insights generation failed: {str(e)}")
    
    async def detect_anomalies(self, emails: List[EmailMessage]) -> List[Dict[str, Any]]:
        """
        Detect anomalies in email data patterns.
        
        Args:
            emails: List of email messages to analyze
            
        Returns:
            List of detected anomalies
        """
        if not self.enable_anomaly_detection or not emails:
            return []
        
        try:
            anomalies = []
            
            # Volume anomalies
            volume_anomalies = await self._detect_volume_anomalies(emails)
            anomalies.extend(volume_anomalies)
            
            # Time pattern anomalies
            time_anomalies = await self._detect_time_anomalies(emails)
            anomalies.extend(time_anomalies)
            
            # Sender behavior anomalies
            sender_anomalies = await self._detect_sender_anomalies(emails)
            anomalies.extend(sender_anomalies)
            
            # Content anomalies
            content_anomalies = await self._detect_content_anomalies(emails)
            anomalies.extend(content_anomalies)
            
            self.stats['anomalies_detected'] += len(anomalies)
            
            return [
                {
                    'type': anomaly.anomaly_type,
                    'description': anomaly.description,
                    'severity': anomaly.severity,
                    'timestamp': anomaly.timestamp.isoformat(),
                    'affected_entities': anomaly.affected_entities,
                    'confidence_score': anomaly.confidence_score
                }
                for anomaly in anomalies
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to detect anomalies: {str(e)}")
            raise AnalyticsError(f"Anomaly detection failed: {str(e)}")
    
    async def _initialize_network_analysis(self) -> None:
        """Initialize network analysis components."""
        self.logger.info("Initializing network analysis")
        # Initialize network analysis algorithms and data structures
    
    async def _initialize_trend_analysis(self) -> None:
        """Initialize trend analysis components."""
        self.logger.info("Initializing trend analysis")
        # Initialize trend analysis algorithms
    
    async def _initialize_anomaly_detection(self) -> None:
        """Initialize anomaly detection components."""
        self.logger.info("Initializing anomaly detection")
        # Initialize anomaly detection algorithms and baselines
    
    def _categorize_frequency(self, count: int, total_emails: int) -> str:
        """Categorize communication frequency."""
        ratio = count / total_emails if total_emails > 0 else 0
        
        if ratio >= 0.1:
            return "very_high"
        elif ratio >= 0.05:
            return "high"
        elif ratio >= 0.02:
            return "medium"
        elif ratio >= 0.01:
            return "low"
        else:
            return "very_low"
    
    async def _calculate_network_metrics(self, communication_graph: Dict) -> Dict[str, Any]:
        """Calculate network analysis metrics."""
        total_nodes = len(communication_graph)
        total_edges = sum(len(recipients) for recipients in communication_graph.values())
        
        # Calculate centrality metrics
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        
        for sender, recipients in communication_graph.items():
            out_degree[sender] = len(recipients)
            for recipient in recipients:
                in_degree[recipient] += 1
        
        return {
            'total_nodes': total_nodes,
            'total_edges': total_edges,
            'density': total_edges / (total_nodes * (total_nodes - 1)) if total_nodes > 1 else 0,
            'top_senders': sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_recipients': sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    async def _calculate_response_time_stats(self, response_times: Dict) -> Dict[str, Any]:
        """Calculate response time statistics."""
        all_times = []
        for times in response_times.values():
            all_times.extend(times)
        
        if not all_times:
            return {'avg_response_time': None, 'median_response_time': None}
        
        return {
            'avg_response_time': statistics.mean(all_times),
            'median_response_time': statistics.median(all_times),
            'min_response_time': min(all_times),
            'max_response_time': max(all_times),
            'total_responses': len(all_times)
        }
    
    async def _analyze_email_volume(self, emails: List[EmailMessage]) -> List[Dict[str, Any]]:
        """Analyze email volume patterns."""
        insights = []
        
        # Daily volume analysis
        daily_counts = defaultdict(int)
        for email in emails:
            if email.received_date:
                date_key = email.received_date.date()
                daily_counts[date_key] += 1
        
        if daily_counts:
            avg_daily = statistics.mean(daily_counts.values())
            max_daily = max(daily_counts.values())
            
            insights.append({
                'type': 'volume_analysis',
                'title': 'Daily Email Volume',
                'description': f'Average {avg_daily:.1f} emails per day, peak of {max_daily} emails',
                'metrics': {
                    'average_daily': avg_daily,
                    'peak_daily': max_daily,
                    'total_days': len(daily_counts)
                }
            })
        
        return insights
    
    async def _analyze_time_patterns(self, emails: List[EmailMessage]) -> List[Dict[str, Any]]:
        """Analyze time-based patterns."""
        insights = []
        
        # Hour of day analysis
        hourly_counts = defaultdict(int)
        for email in emails:
            if email.received_date:
                hour = email.received_date.hour
                hourly_counts[hour] += 1
        
        if hourly_counts:
            peak_hour = max(hourly_counts.items(), key=lambda x: x[1])
            
            insights.append({
                'type': 'time_pattern',
                'title': 'Peak Email Hours',
                'description': f'Most emails received at {peak_hour[0]}:00 ({peak_hour[1]} emails)',
                'metrics': {
                    'peak_hour': peak_hour[0],
                    'peak_count': peak_hour[1],
                    'hourly_distribution': dict(hourly_counts)
                }
            })
        
        return insights
    
    async def _analyze_content_patterns(self, emails: List[EmailMessage]) -> List[Dict[str, Any]]:
        """Analyze content patterns."""
        insights = []
        
        # Subject length analysis
        subject_lengths = [len(email.subject) for email in emails if email.subject]
        if subject_lengths:
            avg_length = statistics.mean(subject_lengths)
            
            insights.append({
                'type': 'content_pattern',
                'title': 'Subject Line Analysis',
                'description': f'Average subject length: {avg_length:.1f} characters',
                'metrics': {
                    'average_length': avg_length,
                    'min_length': min(subject_lengths),
                    'max_length': max(subject_lengths)
                }
            })
        
        return insights
    
    async def _analyze_collaboration_patterns(self, emails: List[EmailMessage]) -> List[Dict[str, Any]]:
        """Analyze collaboration patterns."""
        insights = []
        
        # Recipient count analysis
        recipient_counts = []
        for email in emails:
            total_recipients = len(email.to_recipients) + len(email.cc_recipients) + len(email.bcc_recipients)
            recipient_counts.append(total_recipients)
        
        if recipient_counts:
            avg_recipients = statistics.mean(recipient_counts)
            
            insights.append({
                'type': 'collaboration_pattern',
                'title': 'Collaboration Scope',
                'description': f'Average {avg_recipients:.1f} recipients per email',
                'metrics': {
                    'average_recipients': avg_recipients,
                    'max_recipients': max(recipient_counts),
                    'single_recipient_emails': sum(1 for count in recipient_counts if count == 1)
                }
            })
        
        return insights
    
    async def _analyze_priority_patterns(self, emails: List[EmailMessage]) -> List[Dict[str, Any]]:
        """Analyze priority and importance patterns."""
        insights = []
        
        # Importance distribution
        importance_counts = Counter(email.importance.value for email in emails if email.importance)
        
        if importance_counts:
            total = sum(importance_counts.values())
            high_importance_pct = (importance_counts.get('high', 0) / total) * 100
            
            insights.append({
                'type': 'priority_pattern',
                'title': 'Email Importance Distribution',
                'description': f'{high_importance_pct:.1f}% of emails marked as high importance',
                'metrics': {
                    'high_importance_percentage': high_importance_pct,
                    'importance_distribution': dict(importance_counts)
                }
            })
        
        return insights
    
    async def _generate_insights_summary(self, insights: List[Dict[str, Any]]) -> str:
        """Generate a summary of insights."""
        if not insights:
            return "No significant insights found in the analyzed email data."
        
        summary_parts = []
        
        # Group insights by type
        insight_types = defaultdict(list)
        for insight in insights:
            insight_types[insight['type']].append(insight)
        
        for insight_type, type_insights in insight_types.items():
            summary_parts.append(f"{len(type_insights)} {insight_type.replace('_', ' ')} insights")
        
        return f"Generated {len(insights)} insights: " + ", ".join(summary_parts)
    
    async def _detect_volume_anomalies(self, emails: List[EmailMessage]) -> List[AnomalyDetection]:
        """Detect volume-based anomalies."""
        anomalies = []
        
        # Daily volume anomaly detection
        daily_counts = defaultdict(int)
        for email in emails:
            if email.received_date:
                date_key = email.received_date.date()
                daily_counts[date_key] += 1
        
        if len(daily_counts) > 7:  # Need at least a week of data
            volumes = list(daily_counts.values())
            mean_volume = statistics.mean(volumes)
            std_volume = statistics.stdev(volumes) if len(volumes) > 1 else 0
            
            for date, count in daily_counts.items():
                if std_volume > 0:
                    z_score = abs(count - mean_volume) / std_volume
                    if z_score > self.anomaly_threshold:
                        severity = 'high' if z_score > 3.0 else 'medium'
                        anomalies.append(AnomalyDetection(
                            anomaly_type='volume_anomaly',
                            description=f'Unusual email volume on {date}: {count} emails (z-score: {z_score:.2f})',
                            severity=severity,
                            timestamp=datetime.combine(date, datetime.min.time()),
                            affected_entities=[str(date)],
                            confidence_score=min(z_score / 4.0, 1.0)
                        ))
        
        return anomalies
    
    async def _detect_time_anomalies(self, emails: List[EmailMessage]) -> List[AnomalyDetection]:
        """Detect time-based anomalies."""
        anomalies = []
        
        # Unusual sending times (e.g., very late at night)
        unusual_hours = []
        for email in emails:
            if email.received_date:
                hour = email.received_date.hour
                if hour < 6 or hour > 22:  # Outside normal business hours
                    unusual_hours.append((email.id, hour, email.received_date))
        
        if len(unusual_hours) > len(emails) * 0.1:  # More than 10% outside normal hours
            anomalies.append(AnomalyDetection(
                anomaly_type='time_anomaly',
                description=f'High volume of emails outside normal hours: {len(unusual_hours)} emails',
                severity='medium',
                timestamp=datetime.utcnow(),
                affected_entities=[email_id for email_id, _, _ in unusual_hours[:10]],
                confidence_score=len(unusual_hours) / len(emails)
            ))
        
        return anomalies
    
    async def _detect_sender_anomalies(self, emails: List[EmailMessage]) -> List[AnomalyDetection]:
        """Detect sender behavior anomalies."""
        anomalies = []
        
        # Sender volume anomalies
        sender_counts = defaultdict(int)
        for email in emails:
            if email.sender and email.sender.email:
                sender_counts[email.sender.email] += 1
        
        if sender_counts:
            volumes = list(sender_counts.values())
            mean_volume = statistics.mean(volumes)
            std_volume = statistics.stdev(volumes) if len(volumes) > 1 else 0
            
            for sender, count in sender_counts.items():
                if std_volume > 0:
                    z_score = abs(count - mean_volume) / std_volume
                    if z_score > self.anomaly_threshold and count > mean_volume:
                        anomalies.append(AnomalyDetection(
                            anomaly_type='sender_anomaly',
                            description=f'Unusual email volume from sender {sender}: {count} emails',
                            severity='medium',
                            timestamp=datetime.utcnow(),
                            affected_entities=[sender],
                            confidence_score=min(z_score / 4.0, 1.0)
                        ))
        
        return anomalies
    
    async def _detect_content_anomalies(self, emails: List[EmailMessage]) -> List[AnomalyDetection]:
        """Detect content-based anomalies."""
        anomalies = []
        
        # Subject length anomalies
        subject_lengths = [len(email.subject) for email in emails if email.subject]
        if len(subject_lengths) > 10:
            mean_length = statistics.mean(subject_lengths)
            std_length = statistics.stdev(subject_lengths)
            
            unusual_subjects = []
            for email in emails:
                if email.subject:
                    length = len(email.subject)
                    if std_length > 0:
                        z_score = abs(length - mean_length) / std_length
                        if z_score > self.anomaly_threshold:
                            unusual_subjects.append((email.id, length))
            
            if unusual_subjects:
                anomalies.append(AnomalyDetection(
                    anomaly_type='content_anomaly',
                    description=f'Unusual subject lengths detected in {len(unusual_subjects)} emails',
                    severity='low',
                    timestamp=datetime.utcnow(),
                    affected_entities=[email_id for email_id, _ in unusual_subjects[:10]],
                    confidence_score=len(unusual_subjects) / len(emails)
                ))
        
        return anomalies
    
    async def get_analytics_stats(self) -> Dict[str, Any]:
        """Get analytics engine statistics."""
        return {
            **self.stats,
            'is_initialized': self.is_initialized,
            'network_analysis_enabled': self.enable_network_analysis,
            'trend_analysis_enabled': self.enable_trend_analysis,
            'anomaly_detection_enabled': self.enable_anomaly_detection,
            'analysis_window_days': self.analysis_window_days
        }
