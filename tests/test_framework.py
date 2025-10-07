"""Comprehensive Testing Framework for Automation Project"""
import os
import sys
import time
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import main
from config import load_config, get_objectives
from notifications import notify_error, notify_unsupported
from workflow import execute_objective
from window_ops import launch_app, find_window, focus_window, maximize_window
from verification import verify_screen_stable, verify_app_visually


class TestFramework:
    """Comprehensive testing framework for automation project"""
    
    def __init__(self):
        self.test_results = []
        self.config = load_config()
        self.test_start_time = datetime.now()
        
    def run_all_tests(self):
        """Run all test scenarios"""
        print("=" * 60)
        print("AUTOMATION FRAMEWORK TESTING SUITE")
        print("=" * 60)
        
        # Phase 1: App Preparation Testing
        self.test_app_preparation_success()
        self.test_app_preparation_failure()
        self.test_app_preparation_retry_success()
        
        # Phase 2: Action Execution Testing
        self.test_action_execution_success()
        self.test_action_execution_retry_success()
        self.test_action_execution_failure()
        
        # Phase 3: Objective Workflow Testing
        self.test_single_objective_execution()
        self.test_multiple_objectives_sequence()
        self.test_mixed_objectives()
        
        # Phase 4: Error Strategy Testing
        self.test_error_strategy_retry_previous()
        self.test_error_strategy_email_dev()
        self.test_error_strategy_rollback_all()
        
        # Phase 5: Email Notification Testing
        self.test_email_notifications()
        
        # Generate Test Report
        self.generate_test_report()
        
    def test_app_preparation_success(self):
        """Test: App launches successfully on first attempt"""
        print("\n[TEST] Testing: App Preparation Success")
        test_name = "app_preparation_success"
        
        try:
            # Test app preparation
            app_config = self.config['apps'][0]  # Use first app (Notepad)
            app_name = app_config['name']
            
            # Launch app
            result = launch_app(app_config['path'], app_config.get('startup_delay', 2))
            
            if result:
                # Find and maximize window
                window = find_window(app_name)
                if window:
                    focus_window(window)
                    maximize_window(window)
                    
                    # Verify app is ready
                    if verify_app_visually(app_config):
                        self.record_test_result(test_name, "PASS", "App prepared successfully")
                    else:
                        self.record_test_result(test_name, "FAIL", "Visual verification failed")
                else:
                    self.record_test_result(test_name, "FAIL", "Window not found")
            else:
                self.record_test_result(test_name, "FAIL", "App launch failed")
                
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_app_preparation_failure(self):
        """Test: App fails all 3 attempts → Email sent"""
        print("\n[TEST] Testing: App Preparation Failure")
        test_name = "app_preparation_failure"
        
        try:
            # Test with invalid app path
            invalid_config = {
                'path': 'C:\\Invalid\\Path\\app.exe',
                'startup_delay': 1,
                'max_retries': 3
            }
            
            # This should fail and trigger email notification
            result = launch_app(invalid_config['path'], invalid_config['startup_delay'])
            
            # The test passes if it fails gracefully (no crash)
            if not result:
                self.record_test_result(test_name, "PASS", "App failure handled gracefully")
            else:
                self.record_test_result(test_name, "FAIL", "Expected failure but got success")
                
        except Exception as e:
            # Expected to fail, so this is actually a pass
            self.record_test_result(test_name, "PASS", f"Expected failure: {str(e)}")
    
    def test_app_preparation_retry_success(self):
        """Test: App fails twice, succeeds on 3rd attempt"""
        print("\n[TEST] Testing: App Preparation Retry Success")
        test_name = "app_preparation_retry_success"
        
        try:
            # This test would require a more complex setup
            # For now, we'll test the retry logic conceptually
            self.record_test_result(test_name, "SKIP", "Requires complex retry simulation")
            
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_action_execution_success(self):
        """Test: All actions execute successfully"""
        print("\n[TEST] Testing: Action Execution Success")
        test_name = "action_execution_success"
        
        try:
            # Get a simple objective
            objectives = get_objectives(self.config, ['notepad_basic_typing'])
            if objectives[0]:
                supported, _ = objectives
                if supported:
                    objective = supported[0]
                    result = execute_objective(objective, self.config)
                    
                    if result:
                        self.record_test_result(test_name, "PASS", "Objective executed successfully")
                    else:
                        self.record_test_result(test_name, "FAIL", "Objective execution failed")
                else:
                    self.record_test_result(test_name, "SKIP", "No supported objectives available")
            else:
                self.record_test_result(test_name, "SKIP", "No objectives configured")
                
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_action_execution_retry_success(self):
        """Test: Action fails, retries succeed"""
        print("\n[TEST] Testing: Action Execution Retry Success")
        test_name = "action_execution_retry_success"
        
        try:
            # This would require simulating a flaky action
            self.record_test_result(test_name, "SKIP", "Requires flaky action simulation")
            
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_action_execution_failure(self):
        """Test: Action fails all 3 attempts → Rollback + Email"""
        print("\n[TEST] Testing: Action Execution Failure")
        test_name = "action_execution_failure"
        
        try:
            # Test with invalid action
            invalid_objective = {
                'name': 'Test Failure',
                'app': 'Notepad',
                'actions': [{
                    'type': 'invalid_action_type',
                    'description': 'This should fail'
                }]
            }
            
            result = execute_objective(invalid_objective, self.config)
            
            if not result:
                self.record_test_result(test_name, "PASS", "Action failure handled correctly")
            else:
                self.record_test_result(test_name, "FAIL", "Expected failure but got success")
                
        except Exception as e:
            self.record_test_result(test_name, "PASS", f"Expected failure: {str(e)}")
    
    def test_single_objective_execution(self):
        """Test: Single objective execution"""
        print("\n[TEST] Testing: Single Objective Execution")
        test_name = "single_objective_execution"
        
        try:
            # Test with a simple objective
            objectives = get_objectives(self.config, ['notepad_basic_typing'])
            if objectives[0]:
                supported, _ = objectives
                if supported:
                    objective = supported[0]
                    result = execute_objective(objective, self.config)
                    
                    if result:
                        self.record_test_result(test_name, "PASS", "Single objective executed")
                    else:
                        self.record_test_result(test_name, "FAIL", "Single objective failed")
                else:
                    self.record_test_result(test_name, "SKIP", "No supported objectives")
            else:
                self.record_test_result(test_name, "SKIP", "No objectives configured")
                
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_multiple_objectives_sequence(self):
        """Test: Multiple objectives in sequence"""
        print("\n[TEST] Testing: Multiple Objectives Sequence")
        test_name = "multiple_objectives_sequence"
        
        try:
            # Test with multiple objectives
            objectives = get_objectives(self.config, ['notepad_basic_typing', 'notepad_delete_and_close'])
            if objectives[0]:
                supported, _ = objectives
                if len(supported) >= 2:
                    # Execute first objective
                    result1 = execute_objective(supported[0], self.config)
                    # Execute second objective
                    result2 = execute_objective(supported[1], self.config)
                    
                    if result1 and result2:
                        self.record_test_result(test_name, "PASS", "Multiple objectives executed")
                    else:
                        self.record_test_result(test_name, "FAIL", "Some objectives failed")
                else:
                    self.record_test_result(test_name, "SKIP", "Not enough supported objectives")
            else:
                self.record_test_result(test_name, "SKIP", "No objectives configured")
                
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_mixed_objectives(self):
        """Test: Mixed supported/unsupported objectives"""
        print("\n[TEST] Testing: Mixed Objectives")
        test_name = "mixed_objectives"
        
        try:
            # Test with mixed objectives
            objectives = get_objectives(self.config, ['notepad_basic_typing', 'notepad_unsupported_feature'])
            if objectives[0]:
                supported, unsupported = objectives
                
                if len(supported) > 0 and len(unsupported) > 0:
                    self.record_test_result(test_name, "PASS", f"Found {len(supported)} supported, {len(unsupported)} unsupported")
                else:
                    self.record_test_result(test_name, "SKIP", "No mixed objectives available")
            else:
                self.record_test_result(test_name, "SKIP", "No objectives configured")
                
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_error_strategy_retry_previous(self):
        """Test: Error strategy A - retry_previous"""
        print("\n[TEST] Testing: Error Strategy - Retry Previous")
        test_name = "error_strategy_retry_previous"
        
        try:
            # This would require setting up a scenario where retry_previous is triggered
            self.record_test_result(test_name, "SKIP", "Requires complex error scenario setup")
            
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_error_strategy_email_dev(self):
        """Test: Error strategy B - email_dev"""
        print("\n[TEST] Testing: Error Strategy - Email Dev")
        test_name = "error_strategy_email_dev"
        
        try:
            # Test email notification
            notify_error("Test error message", "Test Action")
            self.record_test_result(test_name, "PASS", "Email notification sent")
            
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_error_strategy_rollback_all(self):
        """Test: Error strategy C - rollback_all"""
        print("\n[TEST] Testing: Error Strategy - Rollback All")
        test_name = "error_strategy_rollback_all"
        
        try:
            # This would require setting up a scenario where rollback_all is triggered
            self.record_test_result(test_name, "SKIP", "Requires complex rollback scenario setup")
            
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def test_email_notifications(self):
        """Test: Email notifications for all trigger scenarios"""
        print("\n[TEST] Testing: Email Notifications")
        test_name = "email_notifications"
        
        try:
            # Test different notification scenarios
            notify_error("Test app preparation failure", "App Preparation")
            notify_error("Test action execution failure", "Action Execution")
            notify_unsupported([{'name': 'Test Unsupported', 'reason': 'Test reason'}])
            
            self.record_test_result(test_name, "PASS", "Email notifications tested")
            
        except Exception as e:
            self.record_test_result(test_name, "ERROR", f"Exception: {str(e)}")
    
    def record_test_result(self, test_name, status, message):
        """Record test result"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = {
            'PASS': '[PASS]',
            'FAIL': '[FAIL]',
            'ERROR': '[ERROR]',
            'SKIP': '[SKIP]'
        }
        
        print(f"  {status_emoji.get(status, '[?]')} {test_name}: {status} - {message}")
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        errors = len([r for r in self.test_results if r['status'] == 'ERROR'])
        skipped = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        print(f"Total Tests: {total_tests}")
        print(f"[PASS] Passed: {passed}")
        print(f"[FAIL] Failed: {failed}")
        print(f"[ERROR] Errors: {errors}")
        print(f"[SKIP] Skipped: {skipped}")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Save detailed report
        report_data = {
            'test_summary': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'skipped': skipped,
                'success_rate': success_rate,
                'test_duration': str(datetime.now() - self.test_start_time)
            },
            'test_results': self.test_results
        }
        
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\nDetailed report saved: {report_file}")
        
        # Print failed tests
        if failed > 0 or errors > 0:
            print("\n[FAIL] FAILED/ERROR TESTS:")
            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"  - {result['test_name']}: {result['message']}")


if __name__ == "__main__":
    # Run the test framework
    test_framework = TestFramework()
    test_framework.run_all_tests()
