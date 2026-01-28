"""
Test Orchestration Service

Manages triggering and monitoring centralized QA tests from service pipelines.
"""

import requests
import time
import os
from typing import Dict, Optional, List
from datetime import datetime


class TestOrchestrator:
    """Orchestrates test execution for services"""
    
    def __init__(self):
        self.circleci_token = os.getenv('CIRCLECI_API_TOKEN')
        self.circleci_api = 'https://circleci.com/api/v2'
        self.project_slug = 'gh/retail-capital/faas_qa_automation'
    
    def trigger_service_tests(
        self,
        service: str,
        test_suite: str = 'integration',
        environment: str = 'dev',
        triggered_by: str = '',
        build_num: str = '',
        commit_sha: str = ''
    ) -> Dict:
        """
        Trigger QA tests for a specific service
        
        Args:
            service: Service name (e.g., 'offer', 'contract')
            test_suite: Test suite to run ('integration', 'e2e', 'smoke', 'financial')
            environment: Target environment ('dev', 'uat', 'prod')
            triggered_by: Service that triggered the tests
            build_num: Build number from triggering service
            commit_sha: Commit SHA from triggering service
            
        Returns:
            Pipeline information including pipeline_id
        """
        if not self.circleci_token:
            raise ValueError("CIRCLECI_API_TOKEN environment variable is required")
        
        payload = {
            'parameters': {
                'service': service,
                'test_suite': test_suite,
                'environment': environment,
                'triggered_by': triggered_by,
                'build_num': build_num,
                'commit_sha': commit_sha,
            }
        }
        
        response = requests.post(
            f'{self.circleci_api}/project/{self.project_slug}/pipeline',
            headers={
                'Circle-Token': self.circleci_token,
                'Content-Type': 'application/json',
            },
            json=payload
        )
        
        response.raise_for_status()
        return response.json()
    
    def find_workflow(
        self,
        service: str,
        build_num: str,
        timeout: int = 60
    ) -> Optional[str]:
        """
        Find workflow ID for a service and build number
        
        Args:
            service: Service name
            build_num: Build number from triggering service
            timeout: How long to search (seconds)
            
        Returns:
            Workflow ID if found, None otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Get recent pipelines
            response = requests.get(
                f'{self.circleci_api}/project/{self.project_slug}/pipeline',
                headers={'Circle-Token': self.circleci_token},
                params={'page-token': None}
            )
            
            pipelines = response.json().get('items', [])
            
            for pipeline in pipelines:
                # Check if this pipeline matches
                params = pipeline.get('parameters', {})
                if (params.get('service') == service and 
                    params.get('build_num') == build_num):
                    # Get workflow for this pipeline
                    workflows = self._get_pipeline_workflows(pipeline['id'])
                    if workflows:
                        return workflows[0]['id']
            
            time.sleep(5)  # Poll every 5 seconds
        
        return None
    
    def _get_pipeline_workflows(self, pipeline_id: str) -> List[Dict]:
        """Get workflows for a pipeline"""
        response = requests.get(
            f'{self.circleci_api}/pipeline/{pipeline_id}/workflow',
            headers={'Circle-Token': self.circleci_token}
        )
        return response.json().get('items', [])
    
    def wait_for_tests(
        self,
        workflow_id: str,
        timeout: int = 1800  # 30 minutes
    ) -> Dict:
        """
        Wait for test workflow to complete
        
        Args:
            workflow_id: Workflow ID to wait for
            timeout: Maximum time to wait (seconds)
            
        Returns:
            Workflow status information
            
        Raises:
            TimeoutError: If tests don't complete within timeout
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(
                f'{self.circleci_api}/workflow/{workflow_id}',
                headers={'Circle-Token': self.circleci_token}
            )
            
            workflow = response.json()
            status = workflow['status']
            
            if status in ['success', 'failed', 'error', 'canceled']:
                return workflow
            
            time.sleep(10)  # Poll every 10 seconds
        
        raise TimeoutError(f"Tests did not complete within {timeout} seconds")
    
    def get_test_results(self, workflow_id: str) -> Dict:
        """
        Get test results from a workflow
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Test results summary
        """
        # Get all jobs in workflow
        response = requests.get(
            f'{self.circleci_api}/workflow/{workflow_id}/job',
            headers={'Circle-Token': self.circleci_token}
        )
        
        jobs = response.json().get('items', [])
        
        results = {
            'workflow_id': workflow_id,
            'status': 'unknown',
            'jobs': [],
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'duration': 0,
        }
        
        for job in jobs:
            job_results = self._get_job_test_results(job['job_number'])
            results['jobs'].append(job_results)
            results['total_tests'] += job_results.get('total', 0)
            results['passed'] += job_results.get('passed', 0)
            results['failed'] += job_results.get('failed', 0)
            results['duration'] += job_results.get('duration', 0)
        
        # Determine overall status
        if results['failed'] > 0:
            results['status'] = 'failed'
        elif all(j.get('status') == 'success' for j in results['jobs']):
            results['status'] = 'success'
        else:
            results['status'] = 'partial'
        
        return results
    
    def _get_job_test_results(self, job_number: int) -> Dict:
        """
        Get test results from a specific job
        
        Args:
            job_number: CircleCI job number
            
        Returns:
            Job test results
        """
        # In a real implementation, this would:
        # 1. Get job artifacts
        # 2. Download test results (JUnit XML or JSON)
        # 3. Parse results
        # 4. Return summary
        
        # For now, return basic structure
        return {
            'job_number': job_number,
            'status': 'success',
            'total': 0,
            'passed': 0,
            'failed': 0,
            'duration': 0,
        }
