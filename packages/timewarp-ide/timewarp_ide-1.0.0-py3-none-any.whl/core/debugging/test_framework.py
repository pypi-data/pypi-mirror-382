"""
Testing Framework for TimeWarp IDE
Unit testing, test discovery, and coverage analysis tools
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import unittest
import sys
import os
import threading
import queue
import traceback
import importlib.util
from typing import Dict, List, Any, Optional, Callable, Set
from datetime import datetime
import json
import re

# Try to import coverage if available
try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    COVERAGE_AVAILABLE = False


class TestDiscovery:
    """Discovers and manages test files and test cases"""
    
    def __init__(self):
        self.test_files: List[str] = []
        self.test_suites: Dict[str, unittest.TestSuite] = {}
        self.test_methods: Dict[str, List[str]] = {}
        
    def discover_tests(self, start_dir: str, pattern: str = "test*.py") -> Dict[str, Any]:
        """Discover all test files in directory"""
        self.test_files.clear()
        self.test_suites.clear()
        self.test_methods.clear()
        
        discovery_results = {
            'files_found': 0,
            'test_classes': 0,
            'test_methods': 0,
            'errors': []
        }
        
        try:
            # Use unittest discovery
            loader = unittest.TestLoader()
            suite = loader.discover(start_dir, pattern=pattern)
            
            # Extract information from discovered tests
            self._extract_test_info(suite, discovery_results)
            
        except Exception as e:
            discovery_results['errors'].append(f"Discovery error: {str(e)}")
            
        return discovery_results
        
    def _extract_test_info(self, suite: unittest.TestSuite, results: Dict):
        """Extract test information from test suite"""
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                self._extract_test_info(test, results)
            elif isinstance(test, unittest.TestCase):
                # Get test file information
                test_file = test.__class__.__module__
                test_method = test._testMethodName
                test_class = test.__class__.__name__
                
                if test_file not in self.test_files:
                    self.test_files.append(test_file)
                    results['files_found'] += 1
                    
                if test_file not in self.test_methods:
                    self.test_methods[test_file] = []
                    
                test_full_name = f"{test_class}.{test_method}"
                if test_full_name not in self.test_methods[test_file]:
                    self.test_methods[test_file].append(test_full_name)
                    results['test_methods'] += 1
                    
    def get_test_methods(self, test_file: str) -> List[str]:
        """Get all test methods in a test file"""
        return self.test_methods.get(test_file, [])
        
    def get_all_tests(self) -> Dict[str, List[str]]:
        """Get all discovered tests"""
        return self.test_methods.copy()
        
    def create_test_suite(self, test_file: str, specific_tests: Optional[List[str]] = None) -> unittest.TestSuite:
        """Create a test suite for specific file/tests"""
        suite = unittest.TestSuite()
        
        try:
            # Import the test module
            spec = importlib.util.spec_from_file_location("test_module", test_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Add test classes to suite
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and issubclass(obj, unittest.TestCase):
                        if specific_tests:
                            # Add only specific test methods
                            for test_name in specific_tests:
                                if test_name.startswith(name + '.'):
                                    method_name = test_name.split('.', 1)[1]
                                    if hasattr(obj, method_name):
                                        suite.addTest(obj(method_name))
                        else:
                            # Add all tests from the class
                            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(obj))
                            
        except Exception as e:
            print(f"Error creating test suite for {test_file}: {e}")
            
        return suite


class TestRunner:
    """Runs tests and manages test execution"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()
        
        # Test execution state
        self.is_running = False
        self.current_run = None
        self.test_results = []
        self.discovery = TestDiscovery()
        
        # Coverage tracking
        self.coverage_data = None
        if COVERAGE_AVAILABLE:
            self.coverage_tracker = coverage.Coverage()
            
    def setup_ui(self):
        """Create the test runner interface"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Test Runner")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control panel
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Test directory selection
        dir_frame = ttk.Frame(control_frame)
        dir_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(dir_frame, text="Test Directory:").pack(side=tk.LEFT)
        self.test_dir_var = tk.StringVar(value=".")
        self.test_dir_entry = ttk.Entry(dir_frame, textvariable=self.test_dir_var, width=50)
        self.test_dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_test_directory).pack(side=tk.RIGHT)
        
        # Test pattern
        pattern_frame = ttk.Frame(control_frame)
        pattern_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(pattern_frame, text="Test Pattern:").pack(side=tk.LEFT)
        self.test_pattern_var = tk.StringVar(value="test*.py")
        ttk.Entry(pattern_frame, textvariable=self.test_pattern_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Discover Tests", command=self.discover_tests).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Run All Tests", command=self.run_all_tests).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Run Selected", command=self.run_selected_tests).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Stop Tests", command=self.stop_tests).pack(side=tk.LEFT, padx=2)
        
        # Coverage checkbox
        if COVERAGE_AVAILABLE:
            self.coverage_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(button_frame, text="Enable Coverage", variable=self.coverage_var).pack(side=tk.LEFT, padx=10)
        
        # Main content area
        content_frame = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - test tree
        left_frame = ttk.Frame(content_frame)
        content_frame.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Discovered Tests").pack(anchor=tk.W)
        
        self.test_tree = ttk.Treeview(left_frame, show='tree headings', selectmode='extended')
        self.test_tree.heading('#0', text='Test')
        self.test_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbar for test tree
        tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.test_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.test_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Right panel - results
        right_frame = ttk.Frame(content_frame)
        content_frame.add(right_frame, weight=2)
        
        # Results notebook
        self.results_notebook = ttk.Notebook(right_frame)
        self.results_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Test results tab
        self.results_frame = ttk.Frame(self.results_notebook)
        self.results_notebook.add(self.results_frame, text="Test Results")
        
        self.results_text = scrolledtext.ScrolledText(self.results_frame, wrap=tk.WORD, height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Coverage tab
        if COVERAGE_AVAILABLE:
            self.coverage_frame = ttk.Frame(self.results_notebook)
            self.results_notebook.add(self.coverage_frame, text="Coverage")
            
            self.coverage_text = scrolledtext.ScrolledText(self.coverage_frame, wrap=tk.WORD, height=20)
            self.coverage_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
    def browse_test_directory(self):
        """Browse for test directory"""
        directory = filedialog.askdirectory(initialdir=self.test_dir_var.get())
        if directory:
            self.test_dir_var.set(directory)
            
    def discover_tests(self):
        """Discover tests in the specified directory"""
        test_dir = self.test_dir_var.get()
        pattern = self.test_pattern_var.get()
        
        if not os.path.isdir(test_dir):
            messagebox.showerror("Error", f"Directory not found: {test_dir}")
            return
            
        # Clear existing test tree
        self.test_tree.delete(*self.test_tree.get_children())
        
        # Discover tests
        try:
            results = self.discovery.discover_tests(test_dir, pattern)
            
            # Populate test tree
            self._populate_test_tree()
            
            # Show discovery results
            summary = f"Test Discovery Results:\n"
            summary += f"Files found: {results['files_found']}\n"
            summary += f"Test methods: {results['test_methods']}\n"
            
            if results['errors']:
                summary += f"\nErrors:\n"
                for error in results['errors']:
                    summary += f"  {error}\n"
                    
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, summary)
            
        except Exception as e:
            messagebox.showerror("Discovery Error", f"Failed to discover tests: {str(e)}")
            
    def _populate_test_tree(self):
        """Populate the test tree with discovered tests"""
        all_tests = self.discovery.get_all_tests()
        
        for test_file, test_methods in all_tests.items():
            # Add file node
            file_node = self.test_tree.insert('', 'end', text=test_file, tags=('file',))
            
            # Group by test class
            class_nodes = {}
            for test_method in test_methods:
                if '.' in test_method:
                    class_name, method_name = test_method.split('.', 1)
                    
                    # Create class node if it doesn't exist
                    if class_name not in class_nodes:
                        class_nodes[class_name] = self.test_tree.insert(file_node, 'end', 
                                                                      text=class_name, tags=('class',))
                    
                    # Add method node
                    self.test_tree.insert(class_nodes[class_name], 'end', 
                                        text=method_name, tags=('method',),
                                        values=(test_file, test_method))
                                        
    def run_all_tests(self):
        """Run all discovered tests"""
        if not self.discovery.test_files:
            messagebox.showwarning("No Tests", "No tests discovered. Please discover tests first.")
            return
            
        self._run_tests(None)
        
    def run_selected_tests(self):
        """Run selected tests from the tree"""
        selected_items = self.test_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select tests to run.")
            return
            
        # Extract test information from selected items
        tests_to_run = []
        for item in selected_items:
            tags = self.test_tree.item(item, 'tags')
            if 'method' in tags:
                values = self.test_tree.item(item, 'values')
                if len(values) >= 2:
                    tests_to_run.append((values[0], values[1]))
                    
        if not tests_to_run:
            messagebox.showwarning("Invalid Selection", "Please select specific test methods.")
            return
            
        self._run_tests(tests_to_run)
        
    def _run_tests(self, specific_tests: Optional[List] = None):
        """Run tests in a separate thread"""
        if self.is_running:
            return
            
        self.is_running = True
        self.results_text.delete(1.0, tk.END)
        
        # Start coverage if enabled
        if COVERAGE_AVAILABLE and self.coverage_var.get():
            self.coverage_tracker = coverage.Coverage()
            self.coverage_tracker.start()
            
        # Run tests in thread
        thread = threading.Thread(target=self._test_worker, args=(specific_tests,))
        thread.daemon = True
        thread.start()
        
    def _test_worker(self, specific_tests: Optional[List]):
        """Test execution worker thread"""
        try:
            results = []
            
            if specific_tests:
                # Run specific tests
                for test_file, test_method in specific_tests:
                    suite = self.discovery.create_test_suite(test_file, [test_method])
                    result = self._run_test_suite(suite, f"{test_file}::{test_method}")
                    results.append(result)
            else:
                # Run all tests
                for test_file in self.discovery.test_files:
                    suite = self.discovery.create_test_suite(test_file)
                    result = self._run_test_suite(suite, test_file)
                    results.append(result)
                    
            # Stop coverage and generate report
            if COVERAGE_AVAILABLE and self.coverage_var.get():
                self.coverage_tracker.stop()
                self.coverage_tracker.save()
                self._generate_coverage_report()
                
            # Update UI with final results
            self.parent.after(0, self._update_final_results, results)
            
        except Exception as e:
            error_msg = f"Test execution error: {str(e)}\n{traceback.format_exc()}"
            self.parent.after(0, self._log_message, error_msg)
        finally:
            self.is_running = False
            
    def _run_test_suite(self, suite: unittest.TestSuite, name: str) -> Dict:
        """Run a test suite and return results"""
        # Capture output
        test_output = io.StringIO()
        runner = unittest.TextTestRunner(stream=test_output, verbosity=2)
        
        # Run tests
        result = runner.run(suite)
        
        # Process results
        test_result = {
            'name': name,
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
            'output': test_output.getvalue(),
            'failure_details': result.failures,
            'error_details': result.errors
        }
        
        # Update UI with intermediate results
        self.parent.after(0, self._update_test_result, test_result)
        
        return test_result
        
    def _update_test_result(self, result: Dict):
        """Update UI with test result"""
        message = f"\n=== {result['name']} ===\n"
        message += f"Tests run: {result['tests_run']}, "
        message += f"Failures: {result['failures']}, "
        message += f"Errors: {result['errors']}, "
        message += f"Skipped: {result['skipped']}\n"
        
        if result['failures']:
            message += "\nFAILURES:\n"
            for test, traceback_text in result['failure_details']:
                message += f"  {test}: {traceback_text}\n"
                
        if result['errors']:
            message += "\nERRORS:\n"
            for test, traceback_text in result['error_details']:
                message += f"  {test}: {traceback_text}\n"
                
        message += f"\nOutput:\n{result['output']}\n"
        
        self.results_text.insert(tk.END, message)
        self.results_text.see(tk.END)
        
    def _update_final_results(self, results: List[Dict]):
        """Update UI with final test results summary"""
        total_tests = sum(r['tests_run'] for r in results)
        total_failures = sum(r['failures'] for r in results)
        total_errors = sum(r['errors'] for r in results)
        total_skipped = sum(r['skipped'] for r in results)
        
        summary = f"\n{'='*50}\n"
        summary += f"FINAL RESULTS\n"
        summary += f"{'='*50}\n"
        summary += f"Total tests run: {total_tests}\n"
        summary += f"Failures: {total_failures}\n"
        summary += f"Errors: {total_errors}\n"
        summary += f"Skipped: {total_skipped}\n"
        summary += f"Success rate: {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%\n" if total_tests > 0 else "No tests run\n"
        
        self.results_text.insert(tk.END, summary)
        self.results_text.see(tk.END)
        
    def _generate_coverage_report(self):
        """Generate and display coverage report"""
        if not COVERAGE_AVAILABLE or not hasattr(self, 'coverage_frame'):
            return
            
        try:
            # Generate coverage report
            output = io.StringIO()
            self.coverage_tracker.report(file=output, show_missing=True)
            coverage_report = output.getvalue()
            
            # Display in coverage tab
            self.coverage_text.delete(1.0, tk.END)
            self.coverage_text.insert(1.0, coverage_report)
            
        except Exception as e:
            error_msg = f"Coverage report error: {str(e)}"
            self.coverage_text.delete(1.0, tk.END)
            self.coverage_text.insert(1.0, error_msg)
            
    def _log_message(self, message: str):
        """Log a message to the results"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_line = f"[{timestamp}] {message}\n"
        self.results_text.insert(tk.END, log_line)
        self.results_text.see(tk.END)
        
    def stop_tests(self):
        """Stop test execution"""
        self.is_running = False
        self._log_message("Test execution stopped by user")


class CoverageAnalyzer:
    """Analyzes code coverage from test runs"""
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.setup_ui()
        self.coverage_data = None
        
    def setup_ui(self):
        """Create coverage analyzer interface"""
        # Main frame
        self.frame = ttk.LabelFrame(self.parent, text="Coverage Analyzer")
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if not COVERAGE_AVAILABLE:
            ttk.Label(self.frame, text="Coverage analysis requires the 'coverage' package.\nInstall with: pip install coverage").pack(padx=10, pady=20)
            return
            
        # Control panel
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Load Coverage Data", command=self.load_coverage_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Generate Report", command=self.generate_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Export HTML", command=self.export_html_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Clear Data", command=self.clear_data).pack(side=tk.LEFT, padx=2)
        
        # Coverage display
        self.coverage_notebook = ttk.Notebook(self.frame)
        self.coverage_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary tab
        summary_frame = ttk.Frame(self.coverage_notebook)
        self.coverage_notebook.add(summary_frame, text="Summary")
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, height=15)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Detailed report tab
        detail_frame = ttk.Frame(self.coverage_notebook)
        self.coverage_notebook.add(detail_frame, text="Detailed Report")
        
        self.detail_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD, height=15)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Missing lines tab
        missing_frame = ttk.Frame(self.coverage_notebook)
        self.coverage_notebook.add(missing_frame, text="Missing Coverage")
        
        self.missing_tree = ttk.Treeview(missing_frame, columns=('coverage', 'missing'), show='tree headings')
        self.missing_tree.heading('#0', text='File')
        self.missing_tree.heading('coverage', text='Coverage %')
        self.missing_tree.heading('missing', text='Missing Lines')
        self.missing_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def load_coverage_data(self):
        """Load coverage data from .coverage file"""
        if not COVERAGE_AVAILABLE:
            return
            
        try:
            self.coverage_data = coverage.Coverage()
            self.coverage_data.load()
            
            # Generate initial summary
            self.generate_report()
            
            self._log("Coverage data loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Coverage Error", f"Failed to load coverage data: {str(e)}")
            
    def generate_report(self):
        """Generate coverage reports"""
        if not self.coverage_data:
            messagebox.showwarning("No Data", "Please load coverage data first")
            return
            
        try:
            # Generate summary report
            summary_output = io.StringIO()
            self.coverage_data.report(file=summary_output)
            summary_report = summary_output.getvalue()
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary_report)
            
            # Generate detailed report
            detail_output = io.StringIO()
            self.coverage_data.report(file=detail_output, show_missing=True)
            detail_report = detail_output.getvalue()
            
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(1.0, detail_report)
            
            # Update missing lines tree
            self._update_missing_lines()
            
        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to generate report: {str(e)}")
            
    def _update_missing_lines(self):
        """Update missing lines tree view"""
        # Clear existing items
        for item in self.missing_tree.get_children():
            self.missing_tree.delete(item)
            
        if not self.coverage_data:
            return
            
        try:
            # Get coverage analysis for each file
            analysis = self.coverage_data.analysis2
            
            for filename in self.coverage_data.get_data().measured_files():
                try:
                    _, statements, excluded, missing, _, _ = analysis(filename)
                    
                    if statements:
                        coverage_percent = ((len(statements) - len(missing)) / len(statements)) * 100
                        missing_lines = ', '.join(map(str, sorted(missing)))
                        
                        self.missing_tree.insert('', 'end', text=filename.split('/')[-1],
                                               values=(f"{coverage_percent:.1f}%", missing_lines))
                except Exception:
                    continue  # Skip files that can't be analyzed
                    
        except Exception as e:
            print(f"Error updating missing lines: {e}")
            
    def export_html_report(self):
        """Export HTML coverage report"""
        if not self.coverage_data:
            messagebox.showwarning("No Data", "Please load coverage data first")
            return
            
        directory = filedialog.askdirectory(title="Select directory for HTML report")
        if directory:
            try:
                self.coverage_data.html_report(directory=directory)
                messagebox.showinfo("Export Complete", f"HTML report exported to {directory}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export HTML report: {str(e)}")
                
    def clear_data(self):
        """Clear all coverage data"""
        self.coverage_data = None
        
        # Clear all displays
        self.summary_text.delete(1.0, tk.END)
        self.detail_text.delete(1.0, tk.END)
        
        for item in self.missing_tree.get_children():
            self.missing_tree.delete(item)
            
        self._log("Coverage data cleared")
        
    def _log(self, message: str):
        """Log a message"""
        print(f"Coverage: {message}")  # For now, just print