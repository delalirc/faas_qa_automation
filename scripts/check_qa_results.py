#!/usr/bin/env python3
"""
Check QA test results

Used by service pipelines to validate QA test results and fail if tests failed.
"""

import argparse
import sys
import os
import json

# Add framework to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framework.utils.test_orchestrator import TestOrchestrator


def main():
    parser = argparse.ArgumentParser(description='Check QA test results')
    parser.add_argument('--service', required=True, help='Service name')
    parser.add_argument('--build-num', required=True, help='Build number')
    parser.add_argument('--fail-on-failure', action='store_true', 
                       help='Exit with error code if tests failed')
    parser.add_argument('--output', help='Output file for results JSON')
    
    args = parser.parse_args()
    
    orchestrator = TestOrchestrator()
    
    # Find workflow
    workflow_id = orchestrator.find_workflow(
        service=args.service,
        build_num=args.build_num
    )
    
    if not workflow_id:
        print(f"ERROR: Could not find workflow for {args.service} build {args.build_num}")
        sys.exit(1)
    
    # Get test results
    results = orchestrator.get_test_results(workflow_id)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"QA Test Results for {args.service}")
    print(f"{'='*60}")
    print(f"Status: {results['status']}")
    print(f"Total Tests: {results['total_tests']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Duration: {results['duration']}s")
    print(f"{'='*60}\n")
    
    # Print job details
    if results['jobs']:
        print("Job Results:")
        for job in results['jobs']:
            status_icon = '✅' if job.get('status') == 'success' else '❌'
            print(f"  {status_icon} {job.get('name', 'Unknown')}: "
                  f"{job.get('status', 'unknown')} "
                  f"({job.get('passed', 0)}/{job.get('total', 0)} tests)")
    
    # Save results to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    # Fail if requested and tests failed
    if args.fail_on_failure and results['status'] != 'success':
        print(f"\n❌ QA tests failed. Deployment blocked.")
        print(f"Workflow ID: {workflow_id}")
        sys.exit(1)
    
    print(f"\n✅ QA tests completed successfully.")
    sys.exit(0)


if __name__ == '__main__':
    main()
