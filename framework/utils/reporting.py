"""
Test Reporting and Dashboard

Generates reports and sends notifications for QA test results.
"""

import json
import os
import requests
from datetime import datetime
from typing import Dict, Optional
import xml.etree.ElementTree as ET


class QAReporter:
    """Generate and publish QA test reports"""
    
    def __init__(self):
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.dashboard_api = os.getenv('QA_DASHBOARD_API', '')
    
    def generate_service_report(
        self,
        service: str,
        environment: str,
        results_file: str,
        triggered_by: str = '',
        build_num: str = ''
    ) -> Dict:
        """
        Generate test report for a service
        
        Args:
            service: Service name
            environment: Environment tested
            results_file: Path to JUnit XML results file
            triggered_by: Service that triggered tests
            build_num: Build number
            
        Returns:
            Report dictionary
        """
        # Parse JUnit XML
        results = self._parse_junit_xml(results_file)
        
        report = {
            'service': service,
            'environment': environment,
            'timestamp': datetime.utcnow().isoformat(),
            'triggered_by': triggered_by,
            'build_num': build_num,
            'summary': {
                'total': results.get('total', 0),
                'passed': results.get('passed', 0),
                'failed': results.get('failed', 0),
                'skipped': results.get('skipped', 0),
            },
            'duration': results.get('duration', 0),
            'status': 'success' if results.get('failed', 0) == 0 else 'failed',
            'test_cases': results.get('test_cases', []),
        }
        
        return report
    
    def _parse_junit_xml(self, xml_file: str) -> Dict:
        """Parse JUnit XML test results"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            total = 0
            passed = 0
            failed = 0
            skipped = 0
            duration = 0.0
            test_cases = []
            
            for testsuite in root.findall('testsuite'):
                total += int(testsuite.get('tests', 0))
                failures = int(testsuite.get('failures', 0))
                errors = int(testsuite.get('errors', 0))
                skipped_count = int(testsuite.get('skipped', 0))
                
                failed += failures + errors
                skipped += skipped_count
                passed += total - failed - skipped
                duration += float(testsuite.get('time', 0))
                
                for testcase in testsuite.findall('testcase'):
                    test_cases.append({
                        'name': testcase.get('name'),
                        'classname': testcase.get('classname'),
                        'status': 'passed' if testcase.find('failure') is None else 'failed',
                    })
            
            return {
                'total': total,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'duration': duration,
                'test_cases': test_cases,
            }
        except Exception as e:
            print(f"Warning: Could not parse JUnit XML: {e}")
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'duration': 0,
                'test_cases': [],
            }
    
    def send_slack_notification(self, report: Dict):
        """Send test results to Slack"""
        if not self.slack_webhook:
            return
        
        service = report['service']
        status = report['status']
        summary = report['summary']
        
        if status == 'success':
            emoji = '✅'
            color = 'good'
        else:
            emoji = '❌'
            color = 'danger'
        
        payload = {
            'text': f'{emoji} QA Tests: {service}',
            'attachments': [{
                'color': color,
                'fields': [
                    {
                        'title': 'Status',
                        'value': status.upper(),
                        'short': True
                    },
                    {
                        'title': 'Environment',
                        'value': report['environment'],
                        'short': True
                    },
                    {
                        'title': 'Tests',
                        'value': f"{summary['passed']}/{summary['total']} passed",
                        'short': True
                    },
                    {
                        'title': 'Duration',
                        'value': f"{report['duration']:.1f}s",
                        'short': True
                    },
                ],
                'footer': f'Triggered by {report.get("triggered_by", "manual")}',
                'ts': int(datetime.utcnow().timestamp()),
            }]
        }
        
        if summary['failed'] > 0:
            payload['attachments'][0]['fields'].append({
                'title': 'Failures',
                'value': str(summary['failed']),
                'short': True
            })
        
        try:
            requests.post(self.slack_webhook, json=payload)
        except Exception as e:
            print(f"Warning: Could not send Slack notification: {e}")
    
    def publish_to_dashboard(self, report: Dict):
        """Publish report to QA dashboard"""
        if not self.dashboard_api:
            return
        
        try:
            requests.post(
                f'{self.dashboard_api}/reports',
                json=report,
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            print(f"Warning: Could not publish to dashboard: {e}")


def main():
    """CLI entry point for reporting"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate QA test report')
    parser.add_argument('--service', required=True)
    parser.add_argument('--environment', required=True)
    parser.add_argument('--results', required=True, help='JUnit XML results file')
    parser.add_argument('--triggered-by', default='')
    parser.add_argument('--build-num', default='')
    parser.add_argument('--slack', action='store_true', help='Send Slack notification')
    parser.add_argument('--dashboard', action='store_true', help='Publish to dashboard')
    
    args = parser.parse_args()
    
    reporter = QAReporter()
    
    report = reporter.generate_service_report(
        service=args.service,
        environment=args.environment,
        results_file=args.results,
        triggered_by=args.triggered_by,
        build_num=args.build_num
    )
    
    # Print report
    print(json.dumps(report, indent=2))
    
    # Send notifications
    if args.slack:
        reporter.send_slack_notification(report)
    
    if args.dashboard:
        reporter.publish_to_dashboard(report)
    
    # Exit with error if tests failed
    if report['status'] != 'success':
        import sys
        sys.exit(1)


if __name__ == '__main__':
    main()
