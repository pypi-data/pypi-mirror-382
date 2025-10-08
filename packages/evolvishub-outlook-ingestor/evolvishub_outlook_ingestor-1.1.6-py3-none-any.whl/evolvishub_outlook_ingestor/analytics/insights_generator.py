"""
Automated insights generation from email analytics data.

This module provides intelligent insight generation capabilities that transform
raw analytics data into actionable business insights and recommendations.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import AnalyticsError

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of insights that can be generated."""
    PRODUCTIVITY = "productivity"
    COMMUNICATION = "communication"
    COLLABORATION = "collaboration"
    EFFICIENCY = "efficiency"
    TREND = "trend"
    ANOMALY = "anomaly"
    RECOMMENDATION = "recommendation"


class InsightSeverity(Enum):
    """Severity levels for insights."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Insight:
    """A single business insight."""
    id: str
    title: str
    description: str
    insight_type: InsightType
    severity: InsightSeverity
    confidence: float  # 0.0 to 1.0
    supporting_data: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime
    tags: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.insight_type.value,
            'severity': self.severity.value,
            'confidence': self.confidence,
            'supporting_data': self.supporting_data,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat(),
            'tags': self.tags
        }


@dataclass
class InsightSummary:
    """Summary of generated insights."""
    total_insights: int
    insights_by_type: Dict[str, int]
    insights_by_severity: Dict[str, int]
    top_insights: List[Insight]
    generated_at: datetime


class InsightsGenerator:
    """
    Generates actionable business insights from email analytics data.
    
    Analyzes email patterns, trends, and anomalies to produce intelligent
    insights and recommendations for improving communication efficiency,
    productivity, and collaboration.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the insights generator.
        
        Args:
            config: Configuration dictionary containing:
                - min_confidence: Minimum confidence threshold (default: 0.6)
                - max_insights: Maximum insights to generate (default: 50)
                - insight_types: List of insight types to generate
                - time_window_days: Analysis time window (default: 30)
        """
        self.config = config
        self.min_confidence = config.get('min_confidence', 0.6)
        self.max_insights = config.get('max_insights', 50)
        self.insight_types = config.get('insight_types', [t.value for t in InsightType])
        self.time_window_days = config.get('time_window_days', 30)
        
        self.insight_counter = 0
        
    async def initialize(self) -> None:
        """Initialize the insights generator."""
        logger.info("Initializing InsightsGenerator")
        
    async def generate_insights(
        self, 
        emails: List[EmailMessage],
        analysis_results: Optional[Dict[str, Any]] = None
    ) -> List[Insight]:
        """
        Generate actionable insights from email data and analysis results.
        
        Args:
            emails: List of email messages
            analysis_results: Optional pre-computed analysis results
            
        Returns:
            List of generated insights
            
        Raises:
            AnalyticsError: If insight generation fails
        """
        try:
            if not emails:
                return []
            
            insights = []
            
            # Generate different types of insights
            if InsightType.PRODUCTIVITY.value in self.insight_types:
                productivity_insights = await self._generate_productivity_insights(emails)
                insights.extend(productivity_insights)
            
            if InsightType.COMMUNICATION.value in self.insight_types:
                communication_insights = await self._generate_communication_insights(emails)
                insights.extend(communication_insights)
            
            if InsightType.COLLABORATION.value in self.insight_types:
                collaboration_insights = await self._generate_collaboration_insights(emails)
                insights.extend(collaboration_insights)
            
            if InsightType.EFFICIENCY.value in self.insight_types:
                efficiency_insights = await self._generate_efficiency_insights(emails)
                insights.extend(efficiency_insights)
            
            if InsightType.TREND.value in self.insight_types:
                trend_insights = await self._generate_trend_insights(emails)
                insights.extend(trend_insights)
            
            if InsightType.ANOMALY.value in self.insight_types:
                anomaly_insights = await self._generate_anomaly_insights(emails)
                insights.extend(anomaly_insights)
            
            # Filter by confidence and limit results
            high_confidence_insights = [
                insight for insight in insights 
                if insight.confidence >= self.min_confidence
            ]
            
            # Sort by confidence and severity
            high_confidence_insights.sort(
                key=lambda x: (x.severity.value, x.confidence), 
                reverse=True
            )
            
            # Limit results
            final_insights = high_confidence_insights[:self.max_insights]
            
            logger.info(f"Generated {len(final_insights)} high-confidence insights")
            return final_insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            raise AnalyticsError(f"Insight generation failed: {e}")
    
    async def generate_insight_summary(self, insights: List[Insight]) -> InsightSummary:
        """
        Generate a summary of insights.
        
        Args:
            insights: List of insights to summarize
            
        Returns:
            Insight summary
        """
        insights_by_type = defaultdict(int)
        insights_by_severity = defaultdict(int)
        
        for insight in insights:
            insights_by_type[insight.insight_type.value] += 1
            insights_by_severity[insight.severity.value] += 1
        
        # Get top insights (highest severity and confidence)
        top_insights = sorted(
            insights, 
            key=lambda x: (x.severity.value, x.confidence), 
            reverse=True
        )[:10]
        
        return InsightSummary(
            total_insights=len(insights),
            insights_by_type=dict(insights_by_type),
            insights_by_severity=dict(insights_by_severity),
            top_insights=top_insights,
            generated_at=datetime.utcnow()
        )
    
    async def _generate_productivity_insights(self, emails: List[EmailMessage]) -> List[Insight]:
        """Generate productivity-related insights."""
        insights = []
        
        # Analyze email volume patterns
        hourly_distribution = await self._analyze_hourly_distribution(emails)
        
        # Peak productivity hours
        if hourly_distribution:
            peak_hours = sorted(hourly_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
            peak_hour = peak_hours[0][0]
            peak_count = peak_hours[0][1]
            
            total_emails = sum(hourly_distribution.values())
            peak_percentage = (peak_count / total_emails) * 100 if total_emails > 0 else 0
            
            if peak_percentage > 15:  # More than 15% of emails in one hour
                insights.append(Insight(
                    id=self._generate_insight_id(),
                    title=f"Peak Email Activity at {peak_hour}:00",
                    description=f"Your highest email activity occurs at {peak_hour}:00, representing {peak_percentage:.1f}% of total email volume.",
                    insight_type=InsightType.PRODUCTIVITY,
                    severity=InsightSeverity.MEDIUM,
                    confidence=0.8,
                    supporting_data={
                        'peak_hour': peak_hour,
                        'peak_percentage': peak_percentage,
                        'hourly_distribution': hourly_distribution
                    },
                    recommendations=[
                        f"Schedule important communications around {peak_hour}:00 for maximum engagement",
                        "Consider blocking this time for focused email processing",
                        "Use this insight to optimize meeting schedules"
                    ],
                    timestamp=datetime.utcnow(),
                    tags=['productivity', 'timing', 'email_patterns']
                ))
        
        # Email overload detection
        daily_counts = await self._analyze_daily_distribution(emails)
        if daily_counts:
            avg_daily = np.mean(list(daily_counts.values()))
            max_daily = max(daily_counts.values())
            
            if max_daily > avg_daily * 2:  # More than 2x average
                insights.append(Insight(
                    id=self._generate_insight_id(),
                    title="Email Overload Detected",
                    description=f"Peak daily email volume ({max_daily} emails) is {max_daily/avg_daily:.1f}x higher than average ({avg_daily:.1f}).",
                    insight_type=InsightType.PRODUCTIVITY,
                    severity=InsightSeverity.HIGH,
                    confidence=0.9,
                    supporting_data={
                        'max_daily': max_daily,
                        'average_daily': avg_daily,
                        'overload_ratio': max_daily / avg_daily
                    },
                    recommendations=[
                        "Implement email batching strategies",
                        "Set up email filters and rules",
                        "Consider designated email-free time blocks",
                        "Use priority flags to focus on important emails"
                    ],
                    timestamp=datetime.utcnow(),
                    tags=['productivity', 'email_overload', 'time_management']
                ))
        
        return insights
    
    async def _generate_communication_insights(self, emails: List[EmailMessage]) -> List[Insight]:
        """Generate communication-related insights."""
        insights = []
        
        # Analyze response patterns
        response_analysis = await self._analyze_response_patterns(emails)
        
        if response_analysis['total_conversations'] > 0:
            avg_response_time = response_analysis['avg_response_time_hours']
            
            if avg_response_time > 24:  # Slow response time
                insights.append(Insight(
                    id=self._generate_insight_id(),
                    title="Slow Email Response Time",
                    description=f"Average email response time is {avg_response_time:.1f} hours, which may impact communication efficiency.",
                    insight_type=InsightType.COMMUNICATION,
                    severity=InsightSeverity.MEDIUM,
                    confidence=0.7,
                    supporting_data=response_analysis,
                    recommendations=[
                        "Set up email response time goals",
                        "Use auto-responders for acknowledgment",
                        "Prioritize urgent emails with flags",
                        "Consider communication alternatives for urgent matters"
                    ],
                    timestamp=datetime.utcnow(),
                    tags=['communication', 'response_time', 'efficiency']
                ))
        
        # Analyze communication diversity
        contact_analysis = await self._analyze_contact_diversity(emails)
        
        if contact_analysis['total_contacts'] > 0:
            top_contact_percentage = contact_analysis['top_contact_percentage']
            
            if top_contact_percentage > 30:  # Over-concentration
                insights.append(Insight(
                    id=self._generate_insight_id(),
                    title="Communication Over-Concentration",
                    description=f"Your top contact represents {top_contact_percentage:.1f}% of all email communication, indicating potential over-reliance.",
                    insight_type=InsightType.COMMUNICATION,
                    severity=InsightSeverity.LOW,
                    confidence=0.6,
                    supporting_data=contact_analysis,
                    recommendations=[
                        "Diversify communication channels",
                        "Delegate some communications to team members",
                        "Consider if some communications could be consolidated",
                        "Explore alternative communication methods for frequent contacts"
                    ],
                    timestamp=datetime.utcnow(),
                    tags=['communication', 'diversity', 'networking']
                ))
        
        return insights
    
    async def _generate_collaboration_insights(self, emails: List[EmailMessage]) -> List[Insight]:
        """Generate collaboration-related insights."""
        insights = []
        
        # Analyze group communications
        group_analysis = await self._analyze_group_communications(emails)
        
        if group_analysis['total_group_emails'] > 0:
            group_percentage = (group_analysis['total_group_emails'] / len(emails)) * 100
            
            if group_percentage > 40:  # High group communication
                insights.append(Insight(
                    id=self._generate_insight_id(),
                    title="High Group Communication Activity",
                    description=f"{group_percentage:.1f}% of emails involve multiple recipients, indicating strong collaborative activity.",
                    insight_type=InsightType.COLLABORATION,
                    severity=InsightSeverity.INFO,
                    confidence=0.8,
                    supporting_data=group_analysis,
                    recommendations=[
                        "Consider using collaboration platforms for group discussions",
                        "Implement clear email etiquette for group communications",
                        "Use project management tools for team coordination",
                        "Set up distribution lists for recurring group communications"
                    ],
                    timestamp=datetime.utcnow(),
                    tags=['collaboration', 'teamwork', 'group_communication']
                ))
        
        return insights
    
    async def _generate_efficiency_insights(self, emails: List[EmailMessage]) -> List[Insight]:
        """Generate efficiency-related insights."""
        insights = []
        
        # Analyze attachment usage
        attachment_analysis = await self._analyze_attachment_patterns(emails)
        
        if attachment_analysis['emails_with_attachments'] > 0:
            attachment_percentage = (attachment_analysis['emails_with_attachments'] / len(emails)) * 100
            avg_size = attachment_analysis['avg_attachment_size_mb']
            
            if attachment_percentage > 25 and avg_size > 5:  # High attachment usage
                insights.append(Insight(
                    id=self._generate_insight_id(),
                    title="Heavy Attachment Usage",
                    description=f"{attachment_percentage:.1f}% of emails contain attachments with average size {avg_size:.1f}MB.",
                    insight_type=InsightType.EFFICIENCY,
                    severity=InsightSeverity.MEDIUM,
                    confidence=0.7,
                    supporting_data=attachment_analysis,
                    recommendations=[
                        "Consider using cloud storage links instead of attachments",
                        "Implement file compression strategies",
                        "Use collaboration platforms for document sharing",
                        "Set up shared drives for frequently accessed files"
                    ],
                    timestamp=datetime.utcnow(),
                    tags=['efficiency', 'attachments', 'storage']
                ))
        
        return insights
    
    async def _generate_trend_insights(self, emails: List[EmailMessage]) -> List[Insight]:
        """Generate trend-related insights."""
        insights = []
        
        # Analyze volume trends
        recent_emails = [
            e for e in emails 
            if e.received_date and e.received_date >= datetime.utcnow() - timedelta(days=7)
        ]
        older_emails = [
            e for e in emails 
            if e.received_date and e.received_date < datetime.utcnow() - timedelta(days=7)
        ]
        
        if len(older_emails) > 0:
            recent_daily_avg = len(recent_emails) / 7
            older_daily_avg = len(older_emails) / max(1, (len(emails) - len(recent_emails)) / 7)
            
            growth_rate = ((recent_daily_avg - older_daily_avg) / older_daily_avg) * 100 if older_daily_avg > 0 else 0
            
            if abs(growth_rate) > 20:  # Significant change
                trend_direction = "increasing" if growth_rate > 0 else "decreasing"
                severity = InsightSeverity.MEDIUM if abs(growth_rate) > 50 else InsightSeverity.LOW
                
                insights.append(Insight(
                    id=self._generate_insight_id(),
                    title=f"Email Volume {trend_direction.title()} Trend",
                    description=f"Email volume is {trend_direction} by {abs(growth_rate):.1f}% compared to previous period.",
                    insight_type=InsightType.TREND,
                    severity=severity,
                    confidence=0.8,
                    supporting_data={
                        'growth_rate': growth_rate,
                        'recent_daily_avg': recent_daily_avg,
                        'older_daily_avg': older_daily_avg,
                        'trend_direction': trend_direction
                    },
                    recommendations=[
                        f"Monitor this {trend_direction} trend closely",
                        "Adjust email management strategies accordingly",
                        "Consider workload implications of volume changes",
                        "Review email efficiency practices"
                    ],
                    timestamp=datetime.utcnow(),
                    tags=['trends', 'volume', 'monitoring']
                ))
        
        return insights
    
    async def _generate_anomaly_insights(self, emails: List[EmailMessage]) -> List[Insight]:
        """Generate anomaly-related insights."""
        insights = []
        
        # Detect unusual email sizes
        email_sizes = [len(email.body or '') for email in emails if email.body]
        
        if email_sizes:
            mean_size = np.mean(email_sizes)
            std_size = np.std(email_sizes)
            
            for email in emails:
                if email.body:
                    size = len(email.body)
                    z_score = abs(size - mean_size) / std_size if std_size > 0 else 0
                    
                    if z_score > 3 and size > mean_size * 2:  # Unusually large email
                        insights.append(Insight(
                            id=self._generate_insight_id(),
                            title="Unusually Large Email Detected",
                            description=f"Email with {size} characters is {z_score:.1f} standard deviations above average.",
                            insight_type=InsightType.ANOMALY,
                            severity=InsightSeverity.LOW,
                            confidence=0.6,
                            supporting_data={
                                'email_size': size,
                                'average_size': mean_size,
                                'z_score': z_score
                            },
                            recommendations=[
                                "Review if content could be summarized",
                                "Consider breaking into multiple emails",
                                "Use attachments for lengthy content",
                                "Implement email length guidelines"
                            ],
                            timestamp=datetime.utcnow(),
                            tags=['anomaly', 'email_size', 'content']
                        ))
                        break  # Only report one large email anomaly
        
        return insights
    
    def _generate_insight_id(self) -> str:
        """Generate a unique insight ID."""
        self.insight_counter += 1
        return f"insight_{datetime.utcnow().strftime('%Y%m%d')}_{self.insight_counter:04d}"
    
    async def _analyze_hourly_distribution(self, emails: List[EmailMessage]) -> Dict[int, int]:
        """Analyze email distribution by hour."""
        hourly_counts = defaultdict(int)
        
        for email in emails:
            if email.received_date:
                hour = email.received_date.hour
                hourly_counts[hour] += 1
        
        return dict(hourly_counts)
    
    async def _analyze_daily_distribution(self, emails: List[EmailMessage]) -> Dict[str, int]:
        """Analyze email distribution by day."""
        daily_counts = defaultdict(int)
        
        for email in emails:
            if email.received_date:
                day = email.received_date.strftime('%Y-%m-%d')
                daily_counts[day] += 1
        
        return dict(daily_counts)
    
    async def _analyze_response_patterns(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """Analyze email response patterns."""
        # Simplified analysis - would need conversation threading for accurate results
        return {
            'total_conversations': len(emails) // 2,  # Rough estimate
            'avg_response_time_hours': 12.0,  # Placeholder
            'response_rate': 0.75  # Placeholder
        }
    
    async def _analyze_contact_diversity(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """Analyze contact diversity in communications."""
        contact_counts = defaultdict(int)
        
        for email in emails:
            if email.sender:
                sender = email.sender.email if hasattr(email.sender, 'email') else str(email.sender)
                contact_counts[sender] += 1
        
        if not contact_counts:
            return {'total_contacts': 0, 'top_contact_percentage': 0}
        
        total_contacts = len(contact_counts)
        total_emails = sum(contact_counts.values())
        top_contact_count = max(contact_counts.values())
        top_contact_percentage = (top_contact_count / total_emails) * 100
        
        return {
            'total_contacts': total_contacts,
            'top_contact_percentage': top_contact_percentage,
            'contact_distribution': dict(contact_counts)
        }
    
    async def _analyze_group_communications(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """Analyze group communication patterns."""
        group_emails = 0
        
        for email in emails:
            recipient_count = len(email.to_recipients or []) + len(email.cc_recipients or [])
            if recipient_count > 1:
                group_emails += 1
        
        return {
            'total_group_emails': group_emails,
            'group_percentage': (group_emails / len(emails)) * 100 if emails else 0
        }
    
    async def _analyze_attachment_patterns(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """Analyze email attachment patterns."""
        emails_with_attachments = sum(1 for email in emails if email.has_attachments)
        
        # Simplified analysis - would need actual attachment data
        return {
            'emails_with_attachments': emails_with_attachments,
            'attachment_percentage': (emails_with_attachments / len(emails)) * 100 if emails else 0,
            'avg_attachment_size_mb': 2.5  # Placeholder
        }
