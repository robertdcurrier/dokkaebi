"""
Alert Manager - Notifications when tendies are ready
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class Alert:
    """Alert data structure"""
    timestamp: datetime
    ticker: str
    alert_type: str
    message: str
    score: float
    metadata: Dict


class AlertManager:
    """
    Manages alerts and notifications
    """
    
    def __init__(self, log_file: str = 'alerts.json'):
        self.log_file = Path(log_file)
        self.alerts: List[Alert] = []
        self.load_alerts()
    
    def send_alert(self, message: str, ticker: str = '', 
                  alert_type: str = 'INFO', score: float = 0,
                  metadata: Optional[Dict] = None):
        """Send an alert"""
        alert = Alert(
            timestamp=datetime.now(),
            ticker=ticker,
            alert_type=alert_type,
            message=message,
            score=score,
            metadata=metadata or {}
        )
        
        # Print to console with formatting
        self._print_alert(alert)
        
        # Store alert
        self.alerts.append(alert)
        
        # Save to file
        self.save_alerts()
        
        # Could also send to Discord, Telegram, email, etc.
        if alert_type in ['EXTREME', 'HIGH']:
            self._send_urgent_notification(alert)
    
    def _print_alert(self, alert: Alert):
        """Print alert to console with formatting"""
        symbols = {
            'EXTREME': '🚨🔥',
            'HIGH': '🚨',
            'MEDIUM': '⚠️',
            'LOW': 'ℹ️',
            'INFO': 'ℹ️'
        }
        
        symbol = symbols.get(alert.alert_type, 'ℹ️')
        
        print(f"\n{symbol} [{alert.timestamp.strftime('%H:%M:%S')}] {alert.alert_type}")
        if alert.ticker:
            print(f"   Ticker: {alert.ticker}")
        if alert.score:
            print(f"   Score: {alert.score:.1f}")
        print(f"   {alert.message}")
        
        if alert.metadata:
            for key, value in alert.metadata.items():
                print(f"   {key}: {value}")
    
    def _send_urgent_notification(self, alert: Alert):
        """Send urgent notifications (Discord, Telegram, etc.)"""
        # Placeholder for webhook integrations
        # Example: Discord webhook
        # webhook_url = "YOUR_DISCORD_WEBHOOK_URL"
        # requests.post(webhook_url, json={"content": alert.message})
        pass
    
    def save_alerts(self):
        """Save alerts to file"""
        alerts_data = []
        for alert in self.alerts[-1000:]:  # Keep last 1000 alerts
            alerts_data.append({
                'timestamp': alert.timestamp.isoformat(),
                'ticker': alert.ticker,
                'alert_type': alert.alert_type,
                'message': alert.message,
                'score': alert.score,
                'metadata': alert.metadata
            })
        
        with open(self.log_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
    
    def load_alerts(self):
        """Load alerts from file"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    alerts_data = json.load(f)
                
                self.alerts = []
                for data in alerts_data:
                    self.alerts.append(Alert(
                        timestamp=datetime.fromisoformat(data['timestamp']),
                        ticker=data['ticker'],
                        alert_type=data['alert_type'],
                        message=data['message'],
                        score=data['score'],
                        metadata=data.get('metadata', {})
                    ))
            except Exception as e:
                print(f"Error loading alerts: {e}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get alerts from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [a for a in self.alerts if a.timestamp > cutoff]
    
    def get_ticker_alerts(self, ticker: str) -> List[Alert]:
        """Get all alerts for a specific ticker"""
        return [a for a in self.alerts if a.ticker == ticker]