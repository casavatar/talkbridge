#!/usr/bin/env python3
"""
TalkBridge Security Monitor
===========================

Monitor authentication logs for suspicious activity and security threats.
"""

import re
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

from talkbridge.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SecurityEvent:
    """Represents a security event."""
    timestamp: datetime
    event_type: str
    username: str
    ip_address: str = "unknown"
    details: str = ""
    severity: str = "low"


class SecurityMonitor:
    """Monitor authentication logs for security threats."""

    def __init__(self, log_file: str = "data/logs/errors.log"):
        self.log_file = Path(log_file)
        self.suspicious_usernames = {
            'admin', 'administrator', 'root', 'test', 'guest', 'demo',
            'user', 'password', 'login', 'system', 'oracle', 'postgres',
            'mysql', 'sa', 'support', 'service', 'default'
        }
        self.events = []

    def analyze_logs(self, hours_back: int = 24) -> Dict[str, any]:
        """Analyze recent authentication logs."""
        if not self.log_file.exists():
            logger.warning(f"Log file not found: {self.log_file}")
            return {}

        cutoff_time = datetime.now() - timedelta(hours=hours_back)

        # Parse authentication events
        auth_events = self._parse_auth_events(cutoff_time)

        # Analyze patterns
        analysis = {
            'total_events': len(auth_events),
            'failed_attempts': self._count_failed_attempts(auth_events),
            'brute_force_attempts': self._detect_brute_force(auth_events),
            'suspicious_usernames': self._find_suspicious_usernames(auth_events),
            'frequent_failures': self._find_frequent_failures(auth_events),
            'test_data_in_logs': self._detect_test_data(auth_events),
            'recommendations': []
        }

        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)

        return analysis

    def _parse_auth_events(self, cutoff_time: datetime) -> List[SecurityEvent]:
        """Parse authentication events from log file."""
        events = []

        # Regex patterns for different log types
        patterns = {
            'auth_failed': re.compile(
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[ERROR\] .* Failed authentication attempt for user: (\w+)'
            ),
            'auth_timeout': re.compile(
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[ERROR\] .* Authentication timeout for user: (\w+)'
            ),
            'rate_limited': re.compile(
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[ERROR\] .* Rate limited authentication attempt for user: (\w+)'
            ),
            'test_errors': re.compile(
                r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[ERROR\] .* Test:'
            )
        }

        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    for event_type, pattern in patterns.items():
                        match = pattern.search(line)
                        if match:
                            timestamp_str = match.group(1)
                            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')

                            if timestamp >= cutoff_time:
                                username = match.group(2) if len(match.groups()) > 1 else "unknown"

                                event = SecurityEvent(
                                    timestamp=timestamp,
                                    event_type=event_type,
                                    username=username,
                                    details=line.strip(),
                                    severity=self._assess_severity(event_type, username)
                                )
                                events.append(event)

        except Exception as e:
            logger.error(f"Error parsing log file: {e}")

        return events

    def _assess_severity(self, event_type: str, username: str) -> str:
        """Assess the severity of a security event."""
        if event_type == 'test_errors':
            return "high"  # Test data in production logs
        elif username in self.suspicious_usernames:
            return "medium"
        elif event_type == 'rate_limited':
            return "high"
        elif event_type == 'auth_timeout':
            return "medium"
        else:
            return "low"

    def _count_failed_attempts(self, events: List[SecurityEvent]) -> Dict[str, int]:
        """Count failed authentication attempts by user."""
        failed_counts = Counter()

        for event in events:
            if event.event_type in ['auth_failed', 'auth_timeout']:
                failed_counts[event.username] += 1

        return dict(failed_counts)

    def _detect_brute_force(self, events: List[SecurityEvent]) -> Dict[str, any]:
        """Detect potential brute force attacks."""
        # Group events by username and time windows
        time_windows = defaultdict(list)  # username -> list of timestamps

        for event in events:
            if event.event_type in ['auth_failed', 'auth_timeout']:
                time_windows[event.username].append(event.timestamp)

        brute_force_candidates = {}

        for username, timestamps in time_windows.items():
            # Check for rapid succession of failed attempts
            timestamps.sort()
            rapid_attempts = 0

            for i in range(1, len(timestamps)):
                time_diff = (timestamps[i] - timestamps[i-1]).total_seconds()
                if time_diff < 60:  # Less than 1 minute between attempts
                    rapid_attempts += 1

            if rapid_attempts >= 3:  # 3+ attempts within minutes
                brute_force_candidates[username] = {
                    'total_attempts': len(timestamps),
                    'rapid_attempts': rapid_attempts,
                    'time_span': (timestamps[-1] - timestamps[0]).total_seconds() / 60,
                    'severity': 'high' if rapid_attempts >= 5 else 'medium'
                }

        return brute_force_candidates

    def _find_suspicious_usernames(self, events: List[SecurityEvent]) -> List[str]:
        """Find attempts on suspicious usernames."""
        suspicious_attempts = set()

        for event in events:
            if event.username in self.suspicious_usernames:
                suspicious_attempts.add(event.username)

        return list(suspicious_attempts)

    def _find_frequent_failures(self, events: List[SecurityEvent]) -> Dict[str, int]:
        """Find users with frequent authentication failures."""
        failure_counts = self._count_failed_attempts(events)

        # Return users with more than 3 failures
        return {user: count for user, count in failure_counts.items() if count > 3}

    def _detect_test_data(self, events: List[SecurityEvent]) -> List[str]:
        """Detect test data in production logs."""
        test_indicators = []

        for event in events:
            if event.event_type == 'test_errors':
                test_indicators.append(event.details)

        return test_indicators

    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate security recommendations based on analysis."""
        recommendations = []

        if analysis['test_data_in_logs']:
            recommendations.append(
                "CRITICAL: Remove test data from production logs. Test code should not run in production."
            )

        if analysis['brute_force_attempts']:
            recommendations.append(
                f"WARNING: Detected {len(analysis['brute_force_attempts'])} potential brute force attacks. "
                "Consider implementing CAPTCHA or temporary IP blocking."
            )

        if analysis['suspicious_usernames']:
            recommendations.append(
                f"ALERT: Authentication attempts on {len(analysis['suspicious_usernames'])} suspicious usernames: "
                f"{', '.join(analysis['suspicious_usernames'])}. Consider monitoring these more closely."
            )

        if analysis['frequent_failures']:
            high_failure_count = sum(1 for count in analysis['frequent_failures'].values() if count > 10)
            if high_failure_count > 0:
                recommendations.append(
                    f"WARNING: {high_failure_count} users with very high failure rates (>10 attempts). "
                    "Consider temporary account lockouts."
                )

        if not recommendations:
            recommendations.append("No immediate security concerns detected.")

        return recommendations


def main():
    """Run security analysis and generate report."""
    print("🔍 TalkBridge Security Monitor")
    print("=" * 50)

    monitor = SecurityMonitor()
    analysis = monitor.analyze_logs(hours_back=24)

    print(f"\n📊 Security Analysis (Last 24 Hours)")
    print(f"Total Events: {analysis['total_events']}")
    print(f"Failed Attempts: {len(analysis['failed_attempts'])}")
    print(f"Brute Force Attempts: {len(analysis['brute_force_attempts'])}")
    print(f"Suspicious Usernames: {len(analysis['suspicious_usernames'])}")

    if analysis['failed_attempts']:
        print(f"\n❌ Failed Authentication Attempts:")
        for username, count in analysis['failed_attempts'].items():
            print(f"   {username}: {count} attempts")

    if analysis['brute_force_attempts']:
        print(f"\n🚨 Potential Brute Force Attacks:")
        for username, details in analysis['brute_force_attempts'].items():
            print(f"   {username}: {details['total_attempts']} attempts in {details['time_span']:.1f} minutes")

    if analysis['suspicious_usernames']:
        print(f"\n⚠️  Suspicious Username Attempts:")
        for username in analysis['suspicious_usernames']:
            print(f"   {username}")

    if analysis['test_data_in_logs']:
        print(f"\n🧪 Test Data in Production Logs:")
        print(f"   Found {len(analysis['test_data_in_logs'])} test entries - REMOVE IMMEDIATELY")

    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"   {i}. {rec}")

    print("\n✅ Security analysis complete")


if __name__ == "__main__":
    main()