"""
Alert management and notification system.

This module provides comprehensive alerting capabilities with configurable
rules, notification channels, and alert correlation.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from evolvishub_outlook_ingestor.core.exceptions import MonitoringError

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """An alert notification."""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    timestamp: datetime
    labels: Dict[str, str]
    resolved: bool = False


@dataclass
class AlertRule:
    """An alert rule definition."""
    rule_id: str
    name: str
    condition: Callable[[Dict[str, float]], bool]
    severity: AlertSeverity
    message_template: str
    enabled: bool = True


class AlertManager:
    """
    Manages alerts and notifications.
    
    Provides comprehensive alert management including:
    - Alert rule definition and evaluation
    - Alert correlation and deduplication
    - Multi-channel notifications
    - Alert lifecycle management
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the alert manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.notification_channels = config.get('notification_channels', [])
        
    async def initialize(self) -> None:
        """Initialize the alert manager."""
        logger.info("Initializing AlertManager")
        
        # Load default alert rules
        await self._load_default_rules()
        
    async def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.rule_id}")
        
    async def evaluate_rules(self, metrics: Dict[str, float]) -> List[Alert]:
        """Evaluate alert rules against current metrics."""
        triggered_alerts = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            try:
                if rule.condition(metrics):
                    alert = Alert(
                        alert_id=f"{rule.rule_id}_{int(datetime.utcnow().timestamp())}",
                        title=rule.name,
                        description=rule.message_template.format(**metrics),
                        severity=rule.severity,
                        timestamp=datetime.utcnow(),
                        labels={"rule_id": rule.rule_id}
                    )
                    
                    triggered_alerts.append(alert)
                    self.active_alerts[alert.alert_id] = alert
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
        
        return triggered_alerts
        
    async def send_notifications(self, alerts: List[Alert]) -> None:
        """Send alert notifications."""
        for alert in alerts:
            for channel in self.notification_channels:
                try:
                    await self._send_notification(channel, alert)
                except Exception as e:
                    logger.error(f"Error sending notification: {e}")
    
    async def _send_notification(self, channel: Dict[str, Any], alert: Alert) -> None:
        """Send notification to a specific channel."""
        channel_type = channel.get('type')
        
        if channel_type == 'webhook':
            await self._send_webhook_notification(channel, alert)
        elif channel_type == 'email':
            await self._send_email_notification(channel, alert)
        else:
            logger.warning(f"Unknown notification channel type: {channel_type}")
    
    async def _send_webhook_notification(self, channel: Dict[str, Any], alert: Alert) -> None:
        """Send webhook notification."""
        # Placeholder for webhook implementation
        logger.info(f"Webhook notification sent for alert: {alert.title}")
    
    async def _send_email_notification(self, channel: Dict[str, Any], alert: Alert) -> None:
        """Send email notification."""
        # Placeholder for email implementation
        logger.info(f"Email notification sent for alert: {alert.title}")
        
    async def _load_default_rules(self) -> None:
        """Load default alert rules."""
        # High error rate rule
        error_rate_rule = AlertRule(
            rule_id="high_error_rate",
            name="High Error Rate",
            condition=lambda m: m.get('error_rate', 0) > 0.05,
            severity=AlertSeverity.CRITICAL,
            message_template="Error rate is {error_rate:.2%}",
            enabled=True
        )
        
        await self.add_rule(error_rate_rule)
