"""
Trend detection and analysis for email data.

This module provides comprehensive trend analysis capabilities including
time-series analysis, seasonal decomposition, and statistical anomaly detection.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from scipy import stats
from scipy.signal import find_peaks
import pandas as pd

from evolvishub_outlook_ingestor.core.data_models import EmailMessage
from evolvishub_outlook_ingestor.core.exceptions import AnalyticsError

logger = logging.getLogger(__name__)


@dataclass
class TrendPoint:
    """A single point in a trend analysis."""
    timestamp: datetime
    value: float
    trend_value: float
    seasonal_value: float
    residual_value: float


@dataclass
class TrendAnalysis:
    """Complete trend analysis results."""
    metric_name: str
    time_period: str
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    trend_strength: float  # 0.0 to 1.0
    seasonal_pattern: bool
    seasonal_period: Optional[int]
    data_points: List[TrendPoint]
    summary_statistics: Dict[str, float]
    anomalies: List[Tuple[datetime, float, str]]


@dataclass
class VolumeMetrics:
    """Email volume metrics."""
    total_emails: int
    emails_per_hour: float
    emails_per_day: float
    peak_hour: int
    peak_day: int
    variance: float
    growth_rate: float


@dataclass
class Anomaly:
    """Detected anomaly in email data."""
    timestamp: datetime
    metric_name: str
    actual_value: float
    expected_value: float
    deviation_score: float
    anomaly_type: str  # 'spike', 'drop', 'outlier'
    severity: str  # 'low', 'medium', 'high'
    description: str


class TrendDetector:
    """
    Detects trends and anomalies in email data using statistical analysis.
    
    Provides comprehensive trend analysis including:
    - Time-series decomposition
    - Seasonal pattern detection
    - Statistical anomaly detection
    - Volume trend analysis
    - Growth rate calculation
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the trend detector.
        
        Args:
            config: Configuration dictionary containing:
                - min_data_points: Minimum data points for analysis (default: 10)
                - anomaly_threshold: Z-score threshold for anomalies (default: 2.5)
                - seasonal_periods: List of periods to check for seasonality
                - smoothing_window: Window size for trend smoothing (default: 7)
        """
        self.config = config
        self.min_data_points = config.get('min_data_points', 10)
        self.anomaly_threshold = config.get('anomaly_threshold', 2.5)
        self.seasonal_periods = config.get('seasonal_periods', [7, 24, 168])  # daily, hourly, weekly
        self.smoothing_window = config.get('smoothing_window', 7)
        
    async def initialize(self) -> None:
        """Initialize the trend detector."""
        logger.info("Initializing TrendDetector")
        
    async def detect_volume_trends(
        self, 
        emails: List[EmailMessage],
        timeframe: str = "daily"
    ) -> TrendAnalysis:
        """
        Analyze email volume trends over time.
        
        Args:
            emails: List of email messages
            timeframe: Analysis timeframe ('hourly', 'daily', 'weekly')
            
        Returns:
            Trend analysis results
            
        Raises:
            AnalyticsError: If analysis fails
        """
        try:
            if len(emails) < self.min_data_points:
                raise AnalyticsError(f"Insufficient data points: {len(emails)} < {self.min_data_points}")
            
            # Group emails by time period
            time_series = await self._create_time_series(emails, timeframe)
            
            if len(time_series) < self.min_data_points:
                raise AnalyticsError(f"Insufficient time periods: {len(time_series)}")
            
            # Convert to pandas for analysis
            df = pd.DataFrame(list(time_series.items()), columns=['timestamp', 'count'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Perform trend decomposition
            trend_points = await self._decompose_time_series(df, timeframe)
            
            # Calculate trend direction and strength
            trend_direction, trend_strength = await self._calculate_trend_metrics(df['count'].values)
            
            # Detect seasonal patterns
            seasonal_pattern, seasonal_period = await self._detect_seasonality(df['count'].values)
            
            # Calculate summary statistics
            summary_stats = await self._calculate_summary_statistics(df['count'].values)
            
            # Detect anomalies
            anomalies = await self._detect_anomalies_in_series(df, 'volume')
            
            return TrendAnalysis(
                metric_name=f"email_volume_{timeframe}",
                time_period=timeframe,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                seasonal_pattern=seasonal_pattern,
                seasonal_period=seasonal_period,
                data_points=trend_points,
                summary_statistics=summary_stats,
                anomalies=anomalies
            )
            
        except Exception as e:
            logger.error(f"Error detecting volume trends: {e}")
            raise AnalyticsError(f"Volume trend analysis failed: {e}")
    
    async def identify_anomalies(
        self, 
        emails: List[EmailMessage],
        metrics: List[str] = None
    ) -> List[Anomaly]:
        """
        Identify anomalies in email metrics.
        
        Args:
            emails: List of email messages
            metrics: List of metrics to analyze (default: ['volume', 'response_time'])
            
        Returns:
            List of detected anomalies
        """
        try:
            if metrics is None:
                metrics = ['volume', 'response_time', 'attachment_size']
            
            all_anomalies = []
            
            for metric in metrics:
                if metric == 'volume':
                    anomalies = await self._detect_volume_anomalies(emails)
                elif metric == 'response_time':
                    anomalies = await self._detect_response_time_anomalies(emails)
                elif metric == 'attachment_size':
                    anomalies = await self._detect_attachment_anomalies(emails)
                else:
                    logger.warning(f"Unknown metric: {metric}")
                    continue
                
                all_anomalies.extend(anomalies)
            
            # Sort by severity and timestamp
            all_anomalies.sort(key=lambda x: (x.severity, x.timestamp), reverse=True)
            
            logger.info(f"Detected {len(all_anomalies)} anomalies across {len(metrics)} metrics")
            return all_anomalies
            
        except Exception as e:
            logger.error(f"Error identifying anomalies: {e}")
            raise AnalyticsError(f"Anomaly detection failed: {e}")
    
    async def calculate_growth_metrics(
        self, 
        emails: List[EmailMessage],
        period_days: int = 30
    ) -> Dict[str, float]:
        """
        Calculate growth metrics for email activity.
        
        Args:
            emails: List of email messages
            period_days: Period for growth calculation
            
        Returns:
            Dictionary of growth metrics
        """
        try:
            if not emails:
                return {}
            
            # Sort emails by date
            sorted_emails = sorted(
                [e for e in emails if e.received_date],
                key=lambda e: e.received_date
            )
            
            if len(sorted_emails) < 2:
                return {}
            
            # Split into periods
            latest_date = sorted_emails[-1].received_date
            cutoff_date = latest_date - timedelta(days=period_days)
            
            recent_emails = [e for e in sorted_emails if e.received_date >= cutoff_date]
            older_emails = [e for e in sorted_emails if e.received_date < cutoff_date]
            
            if not older_emails:
                return {'growth_rate': float('inf')}
            
            # Calculate metrics
            recent_count = len(recent_emails)
            older_count = len(older_emails)
            
            # Normalize by time period
            recent_days = (latest_date - cutoff_date).days or 1
            older_days = (cutoff_date - sorted_emails[0].received_date).days or 1
            
            recent_rate = recent_count / recent_days
            older_rate = older_count / older_days
            
            growth_rate = ((recent_rate - older_rate) / older_rate * 100) if older_rate > 0 else 0
            
            # Calculate additional metrics
            metrics = {
                'growth_rate_percent': growth_rate,
                'recent_volume': recent_count,
                'historical_volume': older_count,
                'recent_daily_average': recent_rate,
                'historical_daily_average': older_rate,
                'volume_ratio': recent_rate / older_rate if older_rate > 0 else 0
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating growth metrics: {e}")
            return {}
    
    async def _create_time_series(
        self, 
        emails: List[EmailMessage], 
        timeframe: str
    ) -> Dict[str, int]:
        """Create time series data from emails."""
        time_series = defaultdict(int)
        
        for email in emails:
            if not email.received_date:
                continue
            
            if timeframe == 'hourly':
                key = email.received_date.strftime('%Y-%m-%d %H:00')
            elif timeframe == 'daily':
                key = email.received_date.strftime('%Y-%m-%d')
            elif timeframe == 'weekly':
                # Get Monday of the week
                monday = email.received_date - timedelta(days=email.received_date.weekday())
                key = monday.strftime('%Y-%m-%d')
            else:
                key = email.received_date.strftime('%Y-%m-%d')
            
            time_series[key] += 1
        
        return dict(time_series)
    
    async def _decompose_time_series(
        self, 
        df: pd.DataFrame, 
        timeframe: str
    ) -> List[TrendPoint]:
        """Decompose time series into trend, seasonal, and residual components."""
        try:
            values = df['count'].values
            timestamps = df['timestamp'].values
            
            # Simple trend calculation using moving average
            window_size = min(self.smoothing_window, len(values) // 3)
            if window_size < 2:
                window_size = 2
            
            trend = np.convolve(values, np.ones(window_size)/window_size, mode='same')
            
            # Simple seasonal decomposition
            seasonal = np.zeros_like(values)
            if len(values) >= 14:  # Need enough data for seasonal analysis
                period = 7 if timeframe == 'daily' else 24 if timeframe == 'hourly' else 7
                if len(values) >= period * 2:
                    for i in range(len(values)):
                        seasonal_indices = [j for j in range(i % period, len(values), period)]
                        if len(seasonal_indices) > 1:
                            seasonal[i] = np.mean([values[j] for j in seasonal_indices])
            
            # Residual
            residual = values - trend - seasonal
            
            # Create trend points
            trend_points = []
            for i, timestamp in enumerate(timestamps):
                trend_points.append(TrendPoint(
                    timestamp=pd.to_datetime(timestamp).to_pydatetime(),
                    value=float(values[i]),
                    trend_value=float(trend[i]),
                    seasonal_value=float(seasonal[i]),
                    residual_value=float(residual[i])
                ))
            
            return trend_points
            
        except Exception as e:
            logger.warning(f"Time series decomposition failed: {e}")
            # Return simple trend points without decomposition
            trend_points = []
            for i, row in df.iterrows():
                trend_points.append(TrendPoint(
                    timestamp=row['timestamp'].to_pydatetime(),
                    value=float(row['count']),
                    trend_value=float(row['count']),
                    seasonal_value=0.0,
                    residual_value=0.0
                ))
            return trend_points
    
    async def _calculate_trend_metrics(self, values: np.ndarray) -> Tuple[str, float]:
        """Calculate trend direction and strength."""
        if len(values) < 2:
            return 'stable', 0.0
        
        # Linear regression to determine trend
        x = np.arange(len(values))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # Determine direction
        if abs(slope) < std_err:  # Not statistically significant
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        # Calculate strength (R-squared)
        strength = r_value ** 2
        
        return direction, strength
    
    async def _detect_seasonality(self, values: np.ndarray) -> Tuple[bool, Optional[int]]:
        """Detect seasonal patterns in the data."""
        if len(values) < 14:
            return False, None
        
        # Test different seasonal periods
        best_period = None
        best_score = 0
        
        for period in self.seasonal_periods:
            if len(values) < period * 2:
                continue
            
            # Calculate autocorrelation at this lag
            if period < len(values):
                correlation = np.corrcoef(values[:-period], values[period:])[0, 1]
                if not np.isnan(correlation) and correlation > best_score:
                    best_score = correlation
                    best_period = period
        
        # Consider seasonal if correlation > 0.3
        is_seasonal = best_score > 0.3
        
        return is_seasonal, best_period if is_seasonal else None
    
    async def _calculate_summary_statistics(self, values: np.ndarray) -> Dict[str, float]:
        """Calculate summary statistics for the time series."""
        return {
            'mean': float(np.mean(values)),
            'median': float(np.median(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'range': float(np.max(values) - np.min(values)),
            'coefficient_of_variation': float(np.std(values) / np.mean(values)) if np.mean(values) > 0 else 0,
            'skewness': float(stats.skew(values)),
            'kurtosis': float(stats.kurtosis(values))
        }
    
    async def _detect_anomalies_in_series(
        self, 
        df: pd.DataFrame, 
        metric_name: str
    ) -> List[Tuple[datetime, float, str]]:
        """Detect anomalies in a time series."""
        anomalies = []
        values = df['count'].values
        
        if len(values) < 3:
            return anomalies
        
        # Z-score based anomaly detection
        z_scores = np.abs(stats.zscore(values))
        
        for i, (_, row) in enumerate(df.iterrows()):
            if z_scores[i] > self.anomaly_threshold:
                anomaly_type = 'spike' if values[i] > np.mean(values) else 'drop'
                anomalies.append((
                    row['timestamp'].to_pydatetime(),
                    float(values[i]),
                    f"{anomaly_type} (z-score: {z_scores[i]:.2f})"
                ))
        
        return anomalies
    
    async def _detect_volume_anomalies(self, emails: List[EmailMessage]) -> List[Anomaly]:
        """Detect volume anomalies."""
        anomalies = []
        
        # Create hourly time series
        time_series = await self._create_time_series(emails, 'hourly')
        
        if len(time_series) < self.min_data_points:
            return anomalies
        
        values = np.array(list(time_series.values()))
        timestamps = [datetime.strptime(ts, '%Y-%m-%d %H:00') for ts in time_series.keys()]
        
        # Statistical anomaly detection
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        for i, (timestamp, value) in enumerate(zip(timestamps, values)):
            z_score = abs(value - mean_val) / std_val if std_val > 0 else 0
            
            if z_score > self.anomaly_threshold:
                severity = 'high' if z_score > 3 else 'medium' if z_score > 2 else 'low'
                anomaly_type = 'spike' if value > mean_val else 'drop'
                
                anomalies.append(Anomaly(
                    timestamp=timestamp,
                    metric_name='email_volume',
                    actual_value=float(value),
                    expected_value=float(mean_val),
                    deviation_score=float(z_score),
                    anomaly_type=anomaly_type,
                    severity=severity,
                    description=f"Email volume {anomaly_type}: {value} emails (expected ~{mean_val:.1f})"
                ))
        
        return anomalies
    
    async def _detect_response_time_anomalies(self, emails: List[EmailMessage]) -> List[Anomaly]:
        """Detect response time anomalies."""
        # This would require conversation threading to calculate response times
        # For now, return empty list as it requires more complex implementation
        return []
    
    async def _detect_attachment_anomalies(self, emails: List[EmailMessage]) -> List[Anomaly]:
        """Detect attachment size anomalies."""
        anomalies = []
        
        # Collect attachment sizes
        attachment_data = []
        for email in emails:
            if email.has_attachments and hasattr(email, 'attachments'):
                total_size = sum(att.size for att in email.attachments if hasattr(att, 'size') and att.size)
                if total_size > 0:
                    attachment_data.append((email.received_date or datetime.utcnow(), total_size))
        
        if len(attachment_data) < self.min_data_points:
            return anomalies
        
        sizes = np.array([size for _, size in attachment_data])
        
        # Log-transform sizes for better anomaly detection
        log_sizes = np.log1p(sizes)
        mean_log = np.mean(log_sizes)
        std_log = np.std(log_sizes)
        
        for timestamp, size in attachment_data:
            log_size = np.log1p(size)
            z_score = abs(log_size - mean_log) / std_log if std_log > 0 else 0
            
            if z_score > self.anomaly_threshold:
                severity = 'high' if z_score > 3 else 'medium' if z_score > 2 else 'low'
                
                anomalies.append(Anomaly(
                    timestamp=timestamp,
                    metric_name='attachment_size',
                    actual_value=float(size),
                    expected_value=float(np.expm1(mean_log)),
                    deviation_score=float(z_score),
                    anomaly_type='outlier',
                    severity=severity,
                    description=f"Unusual attachment size: {size/1024/1024:.1f}MB"
                ))
        
        return anomalies
