"""
Security Scan Module - Comprehensive Test Runner

Complete test suite runner including stress tests and integration tests.
"""

import pytest
import sys
import os
import time
from pathlib import Path
from typing import List, Dict, Any
import json

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend_app.security_scan.test_runner import run_basic_tests
from backend_app.security_scan.verify_installation import verify_installation


class ComprehensiveTestRunner:
    """Comprehensive test runner for security scan module."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.test_results = {
            'installation': {},
            'basic': {},
            'stress': {},
            'integration': {},
            'summary': {}
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all test suites and return comprehensive results.
        
        Returns:
            Dict[str, Any]: Complete test results
        """
        print("🧪 Starting Comprehensive Security Scan Module Tests")
        print("=" * 60)
        
        # 1. Installation Verification
        print("\n📦 Step 1: Installation Verification")
        print("-" * 40)
        self.test_results['installation'] = self._run_installation_tests()
        
        # 2. Basic Functionality Tests
        print("\n✅ Step 2: Basic Functionality Tests")
        print("-" * 40)
        self.test_results['basic'] = self._run_basic_tests()
        
        # 3. Stress Tests
        print("\n🔥 Step 3: Stress Tests")
        print("-" * 40)
        self.test_results['stress'] = self._run_stress_tests()
        
        # 4. Integration Tests
        print("\n🔗 Step 4: Integration Tests")
        print("-" * 40)
        self.test_results['integration'] = self._run_integration_tests()
        
        # 5. Generate Summary
        print("\n📊 Step 5: Generating Summary")
        print("-" * 40)
        self.test_results['summary'] = self._generate_summary()
        
        # 6. Save Results
        self._save_results()
        
        return self.test_results
    
    def _run_installation_tests(self) -> Dict[str, Any]:
        """Run installation verification tests."""
        start_time = time.time()
        
        try:
            # Run installation verification
            install_result = verify_installation()
            
            duration = time.time() - start_time
            
            return {
                'status': 'passed' if install_result['success'] else 'failed',
                'duration': duration,
                'details': install_result,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _run_basic_tests(self) -> Dict[str, Any]:
        """Run basic functionality tests."""
        start_time = time.time()
        
        try:
            # Run basic tests using pytest
            test_dir = Path(__file__).parent / 'tests'
            pytest_args = [
                str(test_dir),
                '-v',
                '--tb=short',
                '--json-report',
                '--json-report-file=report.json'
            ]
            
            # Run pytest
            exit_code = pytest.main(pytest_args)
            
            duration = time.time() - start_time
            
            return {
                'status': 'passed' if exit_code == 0 else 'failed',
                'duration': duration,
                'exit_code': exit_code,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _run_stress_tests(self) -> Dict[str, Any]:
        """Run stress tests."""
        start_time = time.time()
        
        try:
            # Run stress tests specifically
            stress_test_file = Path(__file__).parent / 'tests' / 'test_stress_tests.py'
            
            if not stress_test_file.exists():
                return {
                    'status': 'skipped',
                    'duration': 0,
                    'reason': 'Stress test file not found',
                    'timestamp': time.time()
                }
            
            pytest_args = [
                str(stress_test_file),
                '-v',
                '--tb=short',
                '-s',  # Don't capture output for stress tests
                '--maxfail=5'  # Stop after 5 failures
            ]
            
            exit_code = pytest.main(pytest_args)
            
            duration = time.time() - start_time
            
            return {
                'status': 'passed' if exit_code == 0 else 'failed',
                'duration': duration,
                'exit_code': exit_code,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        start_time = time.time()
        
        try:
            # Test DI container integration
            from backend_app.security_scan.di_container import (
                SecurityScanContainer,
                SecurityScanOrchestrator,
                configure_container,
                get_security_scan_orchestrator
            )
            
            # Configure container
            configure_container()
            
            # Create orchestrator
            orchestrator = get_security_scan_orchestrator()
            
            # Test orchestrator functionality
            status_info = orchestrator.get_scan_status()
            health_check = orchestrator.validate_system_health()
            
            duration = time.time() - start_time
            
            return {
                'status': 'passed' if health_check else 'failed',
                'duration': duration,
                'components': {
                    'container_configured': True,
                    'orchestrator_created': True,
                    'status_retrieved': status_info is not None,
                    'health_check_passed': health_check
                },
                'status_info': status_info,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'duration': time.time() - start_time,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary."""
        total_duration = sum(
            result.get('duration', 0) 
            for result in self.test_results.values() 
            if isinstance(result, dict)
        )
        
        passed_tests = sum(
            1 for result in self.test_results.values()
            if isinstance(result, dict) and result.get('status') == 'passed'
        )
        
        failed_tests = sum(
            1 for result in self.test_results.values()
            if isinstance(result, dict) and result.get('status') == 'failed'
        )
        
        skipped_tests = sum(
            1 for result in self.test_results.values()
            if isinstance(result, dict) and result.get('status') == 'skipped'
        )
        
        overall_status = 'passed' if failed_tests == 0 else 'failed'
        
        return {
            'overall_status': overall_status,
            'total_duration': total_duration,
            'test_summary': {
                'passed': passed_tests,
                'failed': failed_tests,
                'skipped': skipped_tests,
                'total': passed_tests + failed_tests + skipped_tests
            },
            'test_categories': list(self.test_results.keys()),
            'timestamp': time.time()
        }
    
    def _save_results(self):
        """Save test results to file."""
        results_file = Path(__file__).parent / 'comprehensive_test_results.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
    
    def print_report(self):
        """Print comprehensive test report."""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Overall Summary
        summary = self.test_results['summary']
        print(f"\n🎯 Overall Status: {summary['overall_status'].upper()}")
        print(f"⏱️  Total Duration: {summary['total_duration']:.2f} seconds")
        print(f"📊 Tests: {summary['test_summary']['passed']} passed, "
              f"{summary['test_summary']['failed']} failed, "
              f"{summary['test_summary']['skipped']} skipped")
        
        # Detailed Results
        for category, result in self.test_results.items():
            if category == 'summary':
                continue
                
            print(f"\n🔍 {category.upper()} TESTS:")
            print(f"   Status: {result.get('status', 'unknown').upper()}")
            print(f"   Duration: {result.get('duration', 0):.2f} seconds")
            
            if result.get('status') == 'failed':
                error = result.get('error', 'Unknown error')
                print(f"   Error: {error}")
            elif result.get('status') == 'passed':
                if 'components' in result:
                    components = result['components']
                    for component, status in components.items():
                        status_text = "✅" if status else "❌"
                        print(f"   {status_text} {component}: {status}")
        
        # Final Recommendation
        if summary['overall_status'] == 'passed':
            print(f"\n🎉 ALL TESTS PASSED! Security Scan Module is ready for production.")
        else:
            print(f"\n⚠️  SOME TESTS FAILED! Review the errors above before deployment.")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point for comprehensive testing."""
    runner = ComprehensiveTestRunner()
    results = runner.run_all_tests()
    runner.print_report()
    
    # Exit with appropriate code
    exit_code = 0 if results['summary']['overall_status'] == 'passed' else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()