"""
Notification utilities for FAAS QA Testing
Sends notifications via Slack, email, etc.
"""

import os
import requests
from typing import Dict, Optional
from datetime import datetime


def send_slack_notification(service: str, results: Dict, webhook_url: Optional[str] = None):
    """
    Send test results to Slack
    
    Args:
        service: Service name
        results: Test results dictionary with 'status', 'passed', 'total', etc.
        webhook_url: Optional Slack webhook URL (defaults to SLACK_WEBHOOK_URL env var)
    """
    webhook = webhook_url or os.getenv('SLACK_WEBHOOK_URL')
    
    if not webhook:
        print("Warning: SLACK_WEBHOOK_URL not set, skipping Slack notification")
        return
    
    if results['status'] == 'success':
        emoji = '✅'
        color = 'good'
    else:
        emoji = '❌'
        color = 'danger'
    
    summary = results.get('summary', {})
    
    payload = {
        'text': f'{emoji} QA Tests: {service}',
        'attachments': [{
            'color': color,
            'fields': [
                {
                    'title': 'Status',
                    'value': results.get('status', 'unknown').upper(),
                    'short': True
                },
                {
                    'title': 'Environment',
                    'value': results.get('environment', 'unknown'),
                    'short': True
                },
                {
                    'title': 'Tests',
                    'value': f"{summary.get('passed', 0)}/{summary.get('total', 0)} passed",
                    'short': True
                },
                {
                    'title': 'Duration',
                    'value': f"{results.get('duration', 0):.1f}s",
                    'short': True
                },
            ],
            'footer': f'Triggered by {results.get("triggered_by", "manual")}',
            'ts': int(datetime.utcnow().timestamp()),
        }]
    }
    
    if summary.get('failed', 0) > 0:
        payload['attachments'][0]['fields'].append({
            'title': 'Failures',
            'value': str(summary.get('failed', 0)),
            'short': True
        })
    
    try:
        response = requests.post(webhook, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Warning: Could not send Slack notification: {e}")


def send_email_notification(service: str, results: Dict, recipients: Optional[list] = None):
    """
    Send test results via email
    
    Args:
        service: Service name
        results: Test results dictionary
        recipients: Optional list of email addresses (defaults to QA_TEAM_EMAIL env var)
    """
    # Placeholder for email notification
    # In production, this would use SES, SendGrid, or similar
    print(f"Email notification would be sent for {service}: {results.get('status')}")
    # TODO: Implement email sending via AWS SES or similar
