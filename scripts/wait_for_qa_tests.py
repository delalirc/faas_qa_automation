#!/usr/bin/env python3
"""
Wait for QA tests to complete

Used by service pipelines to wait for centralized QA tests to finish.
Exits with code 0 if tests pass, 1 if they fail.
"""

import argparse
import sys
import os

# Add framework to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framework.utils.test_orchestrator import TestOrchestrator


def main():
    parser = argparse.ArgumentParser(description='Wait for QA test completion')
    parser.add_argument('--service', required=True, help='Service name')
    parser.add_argument('--build-num', required=True, help='Build number')
    parser.add_argument('--timeout', type=int, default=1800, help='Timeout in seconds')
    
    args = parser.parse_args()
    
    orchestrator = TestOrchestrator()
    
    # Find workflow for this service and build
    print(f"Looking for QA tests for {args.service} (build {args.build_num})...")
    workflow_id = orchestrator.find_workflow(
        service=args.service,
        build_num=args.build_num
    )
    
    if not workflow_id:
        print(f"ERROR: Could not find workflow for {args.service} build {args.build_num}")
        print("This might mean:")
        print("  1. Tests haven't started yet (wait a moment and try again)")
        print("  2. Build number doesn't match")
        print("  3. Service name is incorrect")
        sys.exit(1)
    
    print(f"Found workflow: {workflow_id}")
    print(f"Waiting for tests to complete (timeout: {args.timeout}s)...")
    
    # Wait for completion
    try:
        workflow = orchestrator.wait_for_tests(workflow_id, args.timeout)
        
        status = workflow['status']
        print(f"\nTest workflow status: {status}")
        
        if status == 'success':
            print(f"✅ QA tests passed for {args.service}")
            sys.exit(0)
        else:
            print(f"❌ QA tests failed for {args.service}")
            print(f"Workflow URL: {workflow.get('url', 'N/A')}")
            sys.exit(1)
            
    except TimeoutError as e:
        print(f"ERROR: {e}")
        print(f"Tests are taking longer than expected.")
        print(f"Check CircleCI dashboard for workflow: {workflow_id}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
