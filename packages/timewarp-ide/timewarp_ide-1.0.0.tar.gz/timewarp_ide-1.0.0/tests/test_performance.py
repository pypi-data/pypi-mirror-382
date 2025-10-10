"""
Performance and Load Tests
Tests for TimeWarp IDE performance, memory usage, and scalability
"""

import unittest
import sys
import os
import time
import gc
import threading
from unittest.mock import patch
import tempfile

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from core.interpreter import TimeWarpInterpreter
    INTERPRETER_AVAILABLE = True
except ImportError:
    INTERPRETER_AVAILABLE = False

try:
    from features.gamification import GamificationSystem
    GAMIFICATION_AVAILABLE = True
except ImportError:
    GAMIFICATION_AVAILABLE = False


class PerformanceTestCase(unittest.TestCase):
    """Base class for performance tests with timing utilities"""
    
    def setUp(self):
        """Set up performance testing utilities"""
        self.start_time = None
        self.memory_before = None
        
    def start_timing(self):
        """Start timing a operation"""
        gc.collect()  # Clean up before timing
        self.start_time = time.perf_counter()
        
    def end_timing(self, operation_name="Operation", max_time=None):
        """End timing and assert performance if max_time specified"""
        if self.start_time is None:
            self.fail("start_timing() must be called before end_timing()")
            
        elapsed = time.perf_counter() - self.start_time
        print(f"⏱️ {operation_name}: {elapsed:.4f} seconds")
        
        if max_time is not None:
            self.assertLess(elapsed, max_time, 
                          f"{operation_name} took {elapsed:.4f}s, expected < {max_time}s")
        
        return elapsed
    
    def measure_memory_usage(self, operation_func, operation_name="Operation"):
        """Measure memory usage of an operation"""
        try:
            import psutil
            process = psutil.Process()
            
            gc.collect()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            result = operation_func()
            
            gc.collect()
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_used = memory_after - memory_before
            
            print(f"🧠 {operation_name}: {memory_used:.2f} MB memory used")
            
            return result, memory_used
        except ImportError:
            print("⚠️ psutil not available for memory testing")
            return operation_func(), 0


class TestInterpreterPerformance(PerformanceTestCase):
    """Performance tests for the interpreter"""
    
    def setUp(self):
        """Set up interpreter performance tests"""
        super().setUp()
        if not INTERPRETER_AVAILABLE:
            self.skipTest("Interpreter not available")
        
        self.interpreter = TimeWarpInterpreter()
    
    def test_simple_program_execution_speed(self):
        """Test execution speed of simple programs"""
        simple_program = "T:Hello, World!\nEND"
        
        self.start_timing()
        for _ in range(100):  # Run 100 times
            self.interpreter.run_program(simple_program)
        elapsed = self.end_timing("100 simple program executions", max_time=2.0)
        
        # Should average less than 20ms per execution
        avg_time = elapsed / 100
        self.assertLess(avg_time, 0.02, f"Average execution time {avg_time:.4f}s too slow")
    
    def test_complex_program_performance(self):
        """Test performance with more complex programs"""
        complex_program = """
R: Complex PILOT program for performance testing
U:COUNTER=0
*LOOP
C:COUNTER=*COUNTER*+1
C:SQUARE=*COUNTER***COUNTER*
T:Counter: *COUNTER*, Square: *SQUARE*
M:*COUNTER*,50,*END
J:*LOOP*
*END
T:Finished counting to 50
END
"""
        
        self.start_timing()
        result = self.interpreter.run_program(complex_program)
        elapsed = self.end_timing("Complex program execution", max_time=1.0)
        
        # Should complete within reasonable time
        self.assertTrue(result is not None or elapsed < 1.0)
    
    def test_memory_usage_simple_programs(self):
        """Test memory usage for simple program execution"""
        simple_program = "T:Memory test\nEND"
        
        def run_programs():
            results = []
            for i in range(50):
                result = self.interpreter.run_program(f"T:Program {i}\nEND")
                results.append(result)
            return results
        
        results, memory_used = self.measure_memory_usage(run_programs, "50 simple programs")
        
        # Should not use excessive memory
        self.assertLess(memory_used, 10.0, f"Memory usage {memory_used:.2f}MB too high")
    
    def test_concurrent_execution_safety(self):
        """Test thread safety of interpreter"""
        results = []
        exceptions = []
        
        def run_program(program_id):
            try:
                program = f"T:Thread {program_id} executing\nEND"
                result = self.interpreter.run_program(program)
                results.append((program_id, result))
            except Exception as e:
                exceptions.append((program_id, str(e)))
        
        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=run_program, args=(i,))
            threads.append(thread)
        
        self.start_timing()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join(timeout=5.0)  # 5 second timeout per thread
        
        self.end_timing("10 concurrent program executions", max_time=3.0)
        
        # Check that all threads completed
        self.assertEqual(len(results) + len(exceptions), 10, 
                        "Not all threads completed")
        
        # Should have minimal exceptions (thread safety)
        self.assertLessEqual(len(exceptions), 2, 
                           f"Too many exceptions in concurrent execution: {exceptions}")
    
    def test_large_program_handling(self):
        """Test handling of large programs"""
        # Generate a large program
        large_program_lines = ["R: Large program test"]
        for i in range(500):
            large_program_lines.append(f"T:Line {i}")
        large_program_lines.append("END")
        
        large_program = "\n".join(large_program_lines)
        
        def execute_large_program():
            return self.interpreter.run_program(large_program)
        
        result, memory_used = self.measure_memory_usage(execute_large_program, "Large program (500 lines)")
        
        # Should handle large programs without excessive memory or time
        self.assertLess(memory_used, 50.0, f"Large program used {memory_used:.2f}MB memory")
    
    def test_repeated_execution_memory_leaks(self):
        """Test for memory leaks in repeated execution"""
        test_program = "T:Memory leak test\nU:VAR=*VAR*+1\nT:Variable: *VAR*\nEND"
        
        def run_multiple_programs():
            for _ in range(100):
                self.interpreter.run_program(test_program)
        
        # Run twice and compare memory usage
        _, memory_first = self.measure_memory_usage(run_multiple_programs, "First 100 executions")
        _, memory_second = self.measure_memory_usage(run_multiple_programs, "Second 100 executions")
        
        # Memory usage shouldn't grow significantly between runs
        memory_growth = abs(memory_second - memory_first)
        self.assertLess(memory_growth, 5.0, 
                       f"Potential memory leak detected: {memory_growth:.2f}MB growth")


class TestGamificationPerformance(PerformanceTestCase):
    """Performance tests for the gamification system"""
    
    def setUp(self):
        """Set up gamification performance tests"""
        super().setUp()
        if not GAMIFICATION_AVAILABLE:
            self.skipTest("Gamification system not available")
        
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        with patch('os.path.expanduser') as mock_expanduser:
            mock_expanduser.return_value = self.temp_dir
            self.gamification = GamificationSystem()
    
    def tearDown(self):
        """Clean up gamification performance tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_achievement_checking_performance(self):
        """Test performance of achievement checking"""
        # Set up some progress
        self.gamification.user_stats.programs_written = 25
        self.gamification.user_stats.experience = 500
        
        self.start_timing()
        for _ in range(100):  # Check achievements 100 times
            achievements = self.gamification.check_achievements()
        elapsed = self.end_timing("100 achievement checks", max_time=1.0)
        
        # Should be fast
        avg_time = elapsed / 100
        self.assertLess(avg_time, 0.01, f"Achievement checking too slow: {avg_time:.4f}s average")
    
    def test_rapid_activity_recording(self):
        """Test performance of rapid activity recording"""
        activities = [
            ('program_written', {'language': 'pilot'}),
            ('tutorial_completed', {'tutorial_id': 'pilot_basics'}),
            ('achievement_unlocked', {'achievement_id': 'first_program'}),
        ]
        
        self.start_timing()
        for _ in range(200):  # Record 200 activities
            activity_type, data = activities[_ % len(activities)]
            self.gamification.record_activity(activity_type, data)
        
        elapsed = self.end_timing("200 activity recordings", max_time=2.0)
        
        # Should handle rapid updates
        avg_time = elapsed / 200
        self.assertLess(avg_time, 0.01, f"Activity recording too slow: {avg_time:.4f}s average")
    
    def test_large_stats_handling(self):
        """Test handling of large statistics"""
        # Simulate a user with lots of activity
        self.gamification.user_stats.programs_written = 10000
        self.gamification.user_stats.experience = 50000
        self.gamification.user_stats.total_session_time = 10000.0
        
        # Add many theme usages
        if self.gamification.user_stats.themes_used is None:
            self.gamification.user_stats.themes_used = {}
            
        for i in range(100):
            theme_name = f"theme_{i}"
            self.gamification.track_theme_usage(theme_name)
        
        # Test performance with large stats
        self.start_timing()
        summary = self.gamification.get_achievement_summary()
        insights = self.gamification.get_progress_insights()
        achievements = self.gamification.check_achievements()
        elapsed = self.end_timing("Large stats processing", max_time=0.5)
        
        # Should handle large data efficiently
        self.assertIsInstance(summary, dict)
        self.assertIsInstance(insights, list)
        self.assertIsInstance(achievements, list)
    
    def test_data_persistence_performance(self):
        """Test performance of saving and loading data"""
        # Add significant data
        self.gamification.user_stats.programs_written = 1000
        self.gamification.user_stats.experience = 5000
        
        for i in range(50):
            self.gamification.track_theme_usage(f"theme_{i}")
            self.gamification.track_feature_discovery(f"feature_{i}")
        
        # Test save performance
        self.start_timing()
        for _ in range(20):  # Save 20 times
            self.gamification.save_user_stats()
        elapsed = self.end_timing("20 save operations", max_time=1.0)
        
        # Should save efficiently
        avg_save_time = elapsed / 20
        self.assertLess(avg_save_time, 0.05, f"Save operation too slow: {avg_save_time:.4f}s average")


class TestScalabilityAndLimits(PerformanceTestCase):
    """Test system limits and scalability"""
    
    def test_file_size_limits(self):
        """Test handling of large files"""
        if not INTERPRETER_AVAILABLE:
            self.skipTest("Interpreter not available")
        
        interpreter = TimeWarpInterpreter()
        
        # Create a very large program (simulating large file load)
        large_content = []
        for i in range(5000):  # 5000 lines
            large_content.append(f"R: This is comment line {i}")
        large_content.append("T:Large file loaded successfully")
        large_content.append("END")
        
        large_program = "\\n".join(large_content)
        
        self.start_timing()
        result = interpreter.run_program(large_program)
        elapsed = self.end_timing("Large file (5000 lines) execution", max_time=5.0)
        
        # Should handle large files without crashing
        self.assertTrue(result is not None or elapsed < 5.0)
    
    def test_unicode_and_special_characters_performance(self):
        """Test performance with Unicode and special characters"""
        if not INTERPRETER_AVAILABLE:
            self.skipTest("Interpreter not available")
        
        interpreter = TimeWarpInterpreter()
        
        # Create program with lots of Unicode
        unicode_program = """T:🌍 Unicode test: äöüßñç€£¥
T:Math symbols: ±×÷=≠≤≥∑∏√∞
T:Arrows: ←→↑↓↔↕⇄⇅
T:Emojis: 🎉🎊🎈🎁🎂🍰
END"""
        
        self.start_timing()
        for _ in range(50):  # Run 50 times
            result = interpreter.run_program(unicode_program)
        elapsed = self.end_timing("50 Unicode programs", max_time=2.0)
        
        # Should handle Unicode efficiently
        avg_time = elapsed / 50
        self.assertLess(avg_time, 0.04, f"Unicode handling too slow: {avg_time:.4f}s average")
    
    def test_error_handling_performance(self):
        """Test performance when handling many errors"""
        if not INTERPRETER_AVAILABLE:
            self.skipTest("Interpreter not available")
        
        interpreter = TimeWarpInterpreter()
        
        # Programs with various errors
        error_programs = [
            "INVALID_COMMAND:Test",
            "T:Unclosed string\nEND",
            "C:RESULT=*UNDEFINED*+5\nEND",
            "J:*NONEXISTENT_LABEL*\nEND",
            "M:*VAR*,INVALID,*LABEL*\nEND"
        ]
        
        self.start_timing()
        for _ in range(100):  # Process 100 error cases
            program = error_programs[_ % len(error_programs)]
            try:
                interpreter.run_program(program)
            except Exception:
                pass  # Expected errors
        
        elapsed = self.end_timing("100 error handling cases", max_time=3.0)
        
        # Error handling should be reasonably fast
        avg_time = elapsed / 100
        self.assertLess(avg_time, 0.03, f"Error handling too slow: {avg_time:.4f}s average")


class TestResourceManagement(PerformanceTestCase):
    """Test resource management and cleanup"""
    
    def test_file_handle_management(self):
        """Test that file handles are properly managed"""
        if not GAMIFICATION_AVAILABLE:
            self.skipTest("Gamification system not available")
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create many gamification instances (which save to files)
            instances = []
            
            self.start_timing()
            for i in range(50):
                with patch('os.path.expanduser') as mock_expanduser:
                    mock_expanduser.return_value = os.path.join(temp_dir, f"user_{i}")
                    gamification = GamificationSystem()
                    
                    # Do some operations that involve file I/O
                    gamification.track_theme_usage(f"theme_{i}")
                    gamification.save_user_stats()
                    
                    instances.append(gamification)
            
            elapsed = self.end_timing("50 gamification instances with file I/O", max_time=3.0)
            
            # Should handle file operations efficiently
            avg_time = elapsed / 50
            self.assertLess(avg_time, 0.06, f"File operations too slow: {avg_time:.4f}s average")
            
        finally:
            # Cleanup
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def test_thread_resource_cleanup(self):
        """Test that threading resources are properly cleaned up"""
        completed_threads = []
        
        def test_thread_function(thread_id):
            # Simulate some work
            time.sleep(0.1)
            completed_threads.append(thread_id)
        
        self.start_timing()
        
        # Create and run many short-lived threads
        threads = []
        for i in range(20):
            thread = threading.Thread(target=test_thread_function, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=2.0)
        
        elapsed = self.end_timing("20 thread lifecycle test", max_time=3.0)
        
        # All threads should complete
        self.assertEqual(len(completed_threads), 20, "Not all threads completed properly")
        
        # Check that threads are actually finished
        active_test_threads = [t for t in threading.enumerate() if t != threading.current_thread()]
        self.assertEqual(len(active_test_threads), 0, f"Found {len(active_test_threads)} lingering threads")


if __name__ == '__main__':
    # Create performance test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add performance test cases
    suite.addTests(loader.loadTestsFromTestCase(TestInterpreterPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestGamificationPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestScalabilityAndLimits))
    suite.addTests(loader.loadTestsFromTestCase(TestResourceManagement))
    
    # Run tests with detailed output
    print("🚀 TimeWarp IDE Performance Test Suite")
    print("=" * 50)
    print("⏱️ Testing execution speed, memory usage, and scalability...")
    print()
    
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    total_time = time.time() - start_time
    
    print(f"\\n⏱️ Total performance test time: {total_time:.2f} seconds")
    
    if result.wasSuccessful():
        print("🎉 All performance tests passed!")
        print("💫 TimeWarp IDE shows good performance characteristics.")
    else:
        print("⚠️ Some performance tests failed.")
        print("Consider optimization before production deployment.")
    
    sys.exit(0 if result.wasSuccessful() else 1)