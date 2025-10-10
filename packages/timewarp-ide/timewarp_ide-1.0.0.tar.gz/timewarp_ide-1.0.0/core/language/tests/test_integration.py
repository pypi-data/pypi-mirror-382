"""
TimeWarp IDE Integration Tests
Test the complete refactored system working together
"""

import unittest
import sys
import os

# Add the parent directory to the path to import JAMES modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class TestJamesIntegration(unittest.TestCase):
    """Integration tests for TimeWarp IDE refactored system"""
    
    def test_system_imports(self):
        """Test that all major components can be imported"""
        try:
            from core.language.errors.error_manager import ErrorManager, JAMESError
            from core.language.stdlib.core import StandardLibrary
            from core.language.runtime.engine import RuntimeEngine, ExecutionContext
            from core.language.plugins.manager import PluginManager
            
            # Test basic instantiation
            error_manager = ErrorManager()
            self.assertIsNotNone(error_manager)
            
            stdlib = StandardLibrary()
            self.assertIsNotNone(stdlib)
            
            runtime = RuntimeEngine()
            self.assertIsNotNone(runtime)
            
            plugin_manager = PluginManager()
            self.assertIsNotNone(plugin_manager)
            
        except ImportError as e:
            self.fail(f"Failed to import core components: {e}")
    
    def test_error_system_basic(self):
        """Test basic error system functionality"""
        from core.language.errors.error_manager import ErrorManager, ErrorCode, ErrorSeverity
        
        manager = ErrorManager()
        error = manager.add_error(
            ErrorCode.UNDEFINED_VARIABLE,
            "Test error message"
        )
        
        self.assertTrue(manager.has_errors())
        self.assertEqual(len(manager.errors), 1)
        self.assertEqual(error.message, "Test error message")
    
    def test_stdlib_basic(self):
        """Test basic standard library functionality"""
        from core.language.stdlib.core import StandardLibrary
        
        stdlib = StandardLibrary()
        
        # Test function registration
        self.assertIsNotNone(stdlib.get_function("ABS"))
        self.assertIsNotNone(stdlib.get_function("SIN"))
        
        # Test constant access
        pi_val = stdlib.get_constant("PI")
        self.assertAlmostEqual(pi_val, 3.14159, places=4)
    
    def test_runtime_basic(self):
        """Test basic runtime functionality"""
        from core.language.runtime.engine import RuntimeEngine, ExecutionMode
        
        runtime = RuntimeEngine()
        
        # Test variable operations
        runtime.set_variable("test_var", 42)
        value = runtime.get_variable("test_var")
        self.assertEqual(value, 42)
        
        # Test mode switching
        runtime.set_mode(ExecutionMode.BASIC)
        self.assertEqual(runtime.context.mode, ExecutionMode.BASIC)
    
    def test_plugin_system_basic(self):
        """Test basic plugin system functionality"""
        from core.language.plugins.manager import PluginManager
        from core.language.plugins.base import MathLibraryPlugin
        
        plugin_manager = PluginManager()
        
        # Test plugin registration (builtin plugins should be loaded)
        plugins = plugin_manager.list_plugins()
        self.assertGreater(len(plugins), 0)
        
        # Test enabling plugins
        results = plugin_manager.enable_all_plugins()
        self.assertIsInstance(results, dict)
    
    def test_modular_architecture(self):
        """Test that the modular architecture works correctly"""
        # Test that components can work together
        from core.language.errors.error_manager import ErrorManager
        from core.language.stdlib.core import StandardLibrary
        from core.language.runtime.engine import RuntimeEngine, ExecutionContext
        
        # Create integrated system
        runtime = RuntimeEngine()
        context = runtime.context
        
        # Test that runtime has error manager
        self.assertIsNotNone(context.error_manager)
        
        # Test that runtime has stdlib
        self.assertIsNotNone(context.stdlib)
        
        # Test that stdlib has functions
        self.assertGreater(len(context.stdlib.functions), 0)
    
    def test_comprehensive_workflow(self):
        """Test a complete workflow from parsing to execution"""
        from core.language.runtime.engine import RuntimeEngine
        from core.language.compiler.lexer import EnhancedLexer, TokenType
        
        # Test lexer
        lexer = EnhancedLexer()
        tokens = lexer.tokenize("x = 5 + 3")
        
        self.assertGreater(len(tokens), 0)
        
        # Check we got expected tokens
        token_types = [token.type for token in tokens]
        self.assertIn(TokenType.IDENTIFIER, token_types)
        self.assertIn(TokenType.ASSIGN, token_types)
        self.assertIn(TokenType.NUMBER, token_types)
        
        # Test runtime execution of simple operations
        runtime = RuntimeEngine()
        
        # Test calling stdlib functions
        result = runtime.call_function("ABS", -5)
        self.assertEqual(result, 5)
        
        result = runtime.call_function("MAX", 3, 7)
        self.assertEqual(result, 7)

def run_all_tests():
    """Run all tests and return results"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add integration tests
    suite.addTest(unittest.makeSuite(TestJamesIntegration))
    
    # Add individual component tests if they exist
    try:
        from .test_errors import TestErrorManager
        suite.addTest(unittest.makeSuite(TestErrorManager))
    except ImportError:
        print("Warning: test_errors module not available")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Run integration tests
    success = run_all_tests()
    
    if success:
        print("\\n✅ All tests passed!")
        print("\\n🎉 TimeWarp IDE refactoring completed successfully!")
        print("\\nNew architecture features:")
        print("  • Modular error handling system")
        print("  • Enhanced standard library")
        print("  • Flexible runtime engine")
        print("  • Improved compiler with optimization")
        print("  • Extensible plugin architecture")
        print("  • Comprehensive testing suite")
    else:
        print("\\n❌ Some tests failed - see output above")
        sys.exit(1)