"""
Comprehensive Test Runner for TimeWarp IDE
Combines unit tests, integration tests, and coverage reporting
"""

import unittest
import sys
import os
import time
import json
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Try to import coverage for code coverage reporting
try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False
    print("⚠️ Coverage not available. Install with: pip install coverage")


class TimeWarpTestRunner:
    """Comprehensive test runner for TimeWarp IDE"""
    
    def __init__(self):
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'success_rate': 0.0,
            'execution_time': 0.0,
            'test_suites': [],
            'coverage': None
        }
        self.coverage_instance = None
        
    def setup_coverage(self):
        """Set up code coverage tracking"""
        if not COVERAGE_AVAILABLE:
            return False
            
        try:
            self.coverage_instance = coverage.Coverage(
                source=['core', 'features', 'tools'],
                omit=[
                    '*/tests/*',
                    '*/test_*',
                    '*_test.py',
                    '*/venv/*',
                    '*/.venv/*',
                    '*/env/*'
                ]
            )
            self.coverage_instance.start()
            return True
        except Exception as e:
            print(f"⚠️ Could not start coverage tracking: {e}")
            return False
    
    def stop_coverage(self):
        """Stop coverage tracking and generate report"""
        if not self.coverage_instance:
            return None
            
        try:
            self.coverage_instance.stop()
            self.coverage_instance.save()
            
            # Generate coverage report
            report_io = StringIO()
            self.coverage_instance.report(file=report_io, show_missing=True)
            report_text = report_io.getvalue()
            
            # Get coverage percentage
            total_coverage = self.coverage_instance.report(file=open(os.devnull, 'w'))
            
            return {
                'percentage': total_coverage,
                'report': report_text
            }
        except Exception as e:
            print(f"⚠️ Error generating coverage report: {e}")
            return None
    
    def discover_test_modules(self):
        """Discover all test modules"""
        test_modules = []
        test_dir = os.path.join(os.path.dirname(__file__))
        
        for file in os.listdir(test_dir):
            if file.startswith('test_') and file.endswith('.py') and file != 'test_runner.py':
                module_name = file[:-3]  # Remove .py extension
                test_modules.append(module_name)
        
        return test_modules
    
    def run_test_module(self, module_name):
        """Run tests from a specific module"""
        suite_result = {
            'module': module_name,
            'tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'failures': [],
            'errors_list': [],
            'execution_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # Import the test module
            module = __import__(f'tests.{module_name}', fromlist=[module_name])
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(module)
            
            # Run tests with custom result handler
            result = unittest.TestResult()
            suite.run(result)
            
            # Process results
            suite_result['tests'] = result.testsRun
            suite_result['passed'] = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
            suite_result['failed'] = len(result.failures)
            suite_result['errors'] = len(result.errors)
            suite_result['skipped'] = len(result.skipped)
            
            # Store failure and error details
            suite_result['failures'] = [
                {'test': str(test), 'traceback': traceback}
                for test, traceback in result.failures
            ]
            suite_result['errors_list'] = [
                {'test': str(test), 'traceback': traceback}
                for test, traceback in result.errors
            ]
            
        except Exception as e:
            suite_result['errors'] = 1
            suite_result['errors_list'] = [
                {'test': f'{module_name} import', 'traceback': str(e)}
            ]
        
        suite_result['execution_time'] = time.time() - start_time
        return suite_result
    
    def run_integration_tests(self):
        """Run existing integration tests"""
        suite_result = {
            'module': 'integration_tests',
            'tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'failures': [],
            'errors_list': [],
            'execution_time': 0.0
        }
        
        start_time = time.time()
        
        try:
            # Try to run the existing integration tests
            import integration_tests
            runner = integration_tests.IntegrationTestRunner()
            
            # Capture output
            output_capture = StringIO()
            with redirect_stdout(output_capture), redirect_stderr(output_capture):
                success = runner.run_comprehensive_tests()
            
            output = output_capture.getvalue()
            
            # Extract results from the integration test runner
            if hasattr(runner, 'results'):
                suite_result['tests'] = runner.results.get('total_tests', 0)
                suite_result['passed'] = runner.results.get('passed', 0)
                suite_result['failed'] = runner.results.get('failed', 0)
                suite_result['skipped'] = runner.results.get('skipped', 0)
            else:
                # Fallback based on success
                suite_result['tests'] = 1
                if success:
                    suite_result['passed'] = 1
                else:
                    suite_result['failed'] = 1
            
        except Exception as e:
            suite_result['errors'] = 1
            suite_result['errors_list'] = [
                {'test': 'integration_tests', 'traceback': str(e)}
            ]
        
        suite_result['execution_time'] = time.time() - start_time
        return suite_result
    
    def run_all_tests(self):
        """Run all available tests"""
        print("🧪 TimeWarp IDE - Comprehensive Test Suite")
        print("=" * 60)
        
        overall_start = time.time()
        
        # Setup coverage if available
        coverage_started = self.setup_coverage()
        if coverage_started:
            print("📊 Code coverage tracking enabled")
        
        # Discover and run unit tests
        test_modules = self.discover_test_modules()
        print(f"🔍 Discovered {len(test_modules)} test modules")
        
        for module_name in test_modules:
            print(f"\\n🧪 Running {module_name}...")
            suite_result = self.run_test_module(module_name)
            self.results['test_suites'].append(suite_result)
            
            # Update totals
            self.results['total_tests'] += suite_result['tests']
            self.results['passed'] += suite_result['passed']
            self.results['failed'] += suite_result['failed']
            self.results['errors'] += suite_result['errors']
            self.results['skipped'] += suite_result['skipped']
            
            # Print module results
            self.print_module_results(suite_result)
        
        # Run integration tests
        print("\\n🔗 Running integration tests...")
        integration_result = self.run_integration_tests()
        self.results['test_suites'].append(integration_result)
        
        # Update totals with integration results
        self.results['total_tests'] += integration_result['tests']
        self.results['passed'] += integration_result['passed']
        self.results['failed'] += integration_result['failed']
        self.results['errors'] += integration_result['errors']
        self.results['skipped'] += integration_result['skipped']
        
        self.print_module_results(integration_result)
        
        # Calculate final metrics
        self.results['execution_time'] = time.time() - overall_start
        total_executed = self.results['total_tests'] - self.results['skipped']
        if total_executed > 0:
            self.results['success_rate'] = (self.results['passed'] / total_executed) * 100
        
        # Stop coverage and generate report
        if coverage_started:
            self.results['coverage'] = self.stop_coverage()
        
        # Generate final report
        self.generate_final_report()
        
        # Save detailed results
        self.save_test_results()
        
        return self.results['failed'] == 0 and self.results['errors'] == 0
    
    def print_module_results(self, suite_result):
        """Print results for a single test module"""
        module = suite_result['module']
        tests = suite_result['tests']
        passed = suite_result['passed']
        failed = suite_result['failed']
        errors = suite_result['errors']
        skipped = suite_result['skipped']
        exec_time = suite_result['execution_time']
        
        if tests == 0:
            print(f"  ⏭️ {module}: No tests found")
            return
        
        print(f"  📊 {module}: {tests} tests, {passed} passed, {failed} failed, {errors} errors, {skipped} skipped ({exec_time:.2f}s)")
        
        # Show first few failures/errors for immediate feedback
        for failure in suite_result['failures'][:2]:
            print(f"    ❌ FAIL: {failure['test']}")
        
        for error in suite_result['errors_list'][:2]:
            print(f"    💥 ERROR: {error['test']}")
        
        if len(suite_result['failures']) > 2 or len(suite_result['errors_list']) > 2:
            print(f"    ... and {len(suite_result['failures']) + len(suite_result['errors_list']) - 4} more issues")
    
    def generate_final_report(self):
        """Generate final test report"""
        print("\\n" + "=" * 60)
        print("📊 FINAL TEST REPORT")
        print("=" * 60)
        
        total = self.results['total_tests']
        passed = self.results['passed']
        failed = self.results['failed']
        errors = self.results['errors']
        skipped = self.results['skipped']
        success_rate = self.results['success_rate']
        exec_time = self.results['execution_time']
        
        print(f"🎯 Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        print(f"⏭️ Skipped: {skipped}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️ Execution Time: {exec_time:.2f} seconds")
        
        # Coverage report
        if self.results['coverage'] and self.results['coverage']['percentage']:
            coverage_pct = self.results['coverage']['percentage']
            print(f"📊 Code Coverage: {coverage_pct:.1f}%")
        
        # Overall assessment
        print("\\n" + "-" * 60)
        if failed == 0 and errors == 0:
            print("🎉 ALL TESTS PASSED! TimeWarp IDE is ready for production.")
            if success_rate >= 95:
                print("💫 Excellent test coverage and quality!")
            elif success_rate >= 85:
                print("⭐ Good test coverage. Consider adding more tests.")
            else:
                print("📝 Test coverage could be improved.")
        else:
            print(f"⚠️ {failed + errors} TEST ISSUES FOUND")
            print("Please review and fix failing tests before production.")
            
            # Prioritize most critical issues
            if errors > 0:
                print(f"🚨 Priority: Fix {errors} ERROR(S) first (these prevent tests from running)")
            if failed > 0:
                print(f"🔧 Then fix {failed} FAILURE(S)")
        
        print("-" * 60)
    
    def save_test_results(self):
        """Save detailed test results to file"""
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_results')
        os.makedirs(results_dir, exist_ok=True)
        
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save JSON report
        json_file = os.path.join(results_dir, f'test_results_{timestamp}.json')
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"📄 Detailed results saved to: {json_file}")
        except Exception as e:
            print(f"⚠️ Could not save JSON results: {e}")
        
        # Save coverage HTML report if available
        if self.coverage_instance and COVERAGE_AVAILABLE:
            html_dir = os.path.join(results_dir, f'coverage_{timestamp}')
            try:
                self.coverage_instance.html_report(directory=html_dir)
                print(f"📊 Coverage HTML report: {html_dir}/index.html")
            except Exception as e:
                print(f"⚠️ Could not generate HTML coverage report: {e}")


def main():
    """Main function to run comprehensive tests"""
    print("🚀 Starting TimeWarp IDE Test Suite...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("⚠️ Python 3.7+ recommended for best test compatibility")
    
    # Run tests
    test_runner = TimeWarpTestRunner()
    success = test_runner.run_all_tests()
    
    # Exit with appropriate code
    if success:
        print("\\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\\n❌ Some tests failed. Review the report above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())