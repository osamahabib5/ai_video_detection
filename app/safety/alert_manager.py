"""
Warehouse Safety Alert Manager
==============================
Logs safety violations and sends alerts (file, console, webhook).
Extensible for email/SMS/Slack integration.
"""
import json
import csv
import logging
from pathlib import Path
from datetime import datetime


class AlertManager:
    """Manages safety violation alerts and logging."""

    def __init__(self, output_dir, config=None):
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or {}
        self.violations = []
        self._alert_count = 0

        # Webhook URL for external notifications (Slack, Teams, etc.)
        self.webhook_url = self.config.get('webhook_url')

    def add_violations(self, frame_id, timestamp, violations):
        """Record violations for a single frame."""
        for v in violations:
            record = {
                'frame_id': frame_id,
                'timestamp': timestamp,
                'type': v['type'],
                'severity': v['severity'],
                'person': v['person'],
                'message': v['message'],
            }
            self.violations.append(record)
            self._alert_count += 1

            # Print console alert for HIGH/CRITICAL violations
            if v['severity'] in ('HIGH', 'CRITICAL'):
                self.logger.warning(
                    f"⚠️  {v['severity']} ALERT | Frame {frame_id} | {v['type']}: {v['message']}"
                )

    def save_violations_json(self, filename='violations.json'):
        """Save all violations to JSON."""
        path = self.output_dir / filename
        with open(path, 'w') as f:
            json.dump(self.violations, f, indent=2)
        return str(path)

    def save_violations_csv(self, filename='violations.csv'):
        """Save all violations to CSV."""
        path = self.output_dir / filename
        if not self.violations:
            return str(path)
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.violations[0].keys())
            writer.writeheader()
            writer.writerows(self.violations)
        return str(path)

    def get_summary(self):
        """Return summary of all violations."""
        if not self.violations:
            return {'total_violations': 0, 'by_type': {}, 'by_severity': {}}

        by_type = {}
        by_severity = {}
        for v in self.violations:
            by_type[v['type']] = by_type.get(v['type'], 0) + 1
            by_severity[v['severity']] = by_severity.get(v['severity'], 0) + 1

        return {
            'total_frames_with_violations': len(set(v['frame_id'] for v in self.violations)),
            'total_violations': len(self.violations),
            'by_type': by_type,
            'by_severity': by_severity,
        }

    def send_webhook_alert(self, violation):
        """Send a webhook notification (Slack, Teams, custom).
           Uncomment and configure webhook_url in config to enable."""
        if not self.webhook_url:
            return
        try:
            import requests
            payload = {
                'text': f"🚨 *{violation['severity']} SAFETY VIOLATION*\n"
                        f"Type: {violation['type']}\n"
                        f"Message: {violation['message']}\n"
                        f"Time: {violation['timestamp']}\n"
                        f"Frame: {violation['frame_id']}",
            }
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception as e:
            self.logger.error(f"Webhook failed: {e}")
