"""
Test Error Management System
"""

import unittest
from ..errors.error_manager import (
    ErrorManager, JAMESError, JAMESRuntimeError, JAMESSyntaxError,
    ErrorCode, ErrorSeverity, SourceLocation,
    create_syntax_error, create_runtime_error, create_type_error
)

class TestErrorManager(unittest.TestCase):
    """Test error management system"""
    
    def setUp(self):
        self.error_manager = ErrorManager()
    
    def test_error_creation(self):
        """Test basic error creation"""
        location = SourceLocation(10, 5, "test.james")
        error = JAMESError(
            code=ErrorCode.UNDEFINED_VARIABLE,
            severity=ErrorSeverity.ERROR,
            message="Variable 'x' is not defined",
            location=location,
            suggestions=["Define the variable before using it"]
        )
        
        self.assertEqual(error.code, ErrorCode.UNDEFINED_VARIABLE)
        self.assertEqual(error.severity, ErrorSeverity.ERROR)
        self.assertEqual(error.message, "Variable 'x' is not defined")
        self.assertEqual(error.location.line, 10)
        self.assertEqual(error.location.column, 5)
        self.assertEqual(len(error.suggestions), 1)
    
    def test_error_manager_add_error(self):
        """Test adding errors to manager"""
        location = SourceLocation(5, 1)
        
        error = self.error_manager.add_error(
            ErrorCode.INVALID_SYNTAX,
            "Missing semicolon",
            location,
            suggestions=["Add semicolon at end of statement"]
        )
        
        self.assertTrue(self.error_manager.has_errors())
        self.assertEqual(len(self.error_manager.errors), 1)
        self.assertEqual(error.code, ErrorCode.INVALID_SYNTAX)
    
    def test_error_manager_add_warning(self):
        """Test adding warnings to manager"""
        warning = self.error_manager.add_warning(
            ErrorCode.UNEXPECTED_TOKEN,
            "Unused variable 'temp'",
            SourceLocation(8, 3)
        )
        
        self.assertTrue(self.error_manager.has_warnings())
        self.assertEqual(len(self.error_manager.warnings), 1)
        self.assertEqual(warning.severity, ErrorSeverity.WARNING)
    
    def test_error_formatting(self):
        """Test error message formatting"""
        location = SourceLocation(15, 20, "example.james")
        error = JAMESError(
            code=ErrorCode.TYPE_MISMATCH,
            severity=ErrorSeverity.ERROR,
            message="Expected number, got string",
            location=location,
            suggestions=["Use VAL() to convert string to number"]
        )
        
        formatted = str(error)
        self.assertIn("E2002", formatted)  # Error code
        self.assertIn("ERROR", formatted)
        self.assertIn("Expected number, got string", formatted)
        self.assertIn("example.james:line 15, column 20", formatted)
        self.assertIn("Use VAL() to convert", formatted)
    
    def test_utility_functions(self):
        """Test error utility functions"""
        location = SourceLocation(1, 1)
        
        # Test syntax error creation
        syntax_error = create_syntax_error("Invalid statement", location)
        self.assertIsInstance(syntax_error, JAMESSyntaxError)
        self.assertEqual(syntax_error.error.code, ErrorCode.INVALID_SYNTAX)
        
        # Test runtime error creation
        runtime_error = create_runtime_error("Variable not found")
        self.assertIsInstance(runtime_error, JAMESError)
        
        # Test type error creation
        type_error = create_type_error("number", "string")
        self.assertIsInstance(type_error, JAMESTypeError)
        self.assertIn("Expected number, got string", type_error.error.message)
    
    def test_error_clearing(self):
        """Test clearing errors and warnings"""
        self.error_manager.add_error(ErrorCode.INVALID_SYNTAX, "Test error")
        self.error_manager.add_warning(ErrorCode.UNEXPECTED_TOKEN, "Test warning")
        
        self.assertTrue(self.error_manager.has_errors())
        self.assertTrue(self.error_manager.has_warnings())
        
        self.error_manager.clear()
        
        self.assertFalse(self.error_manager.has_errors())
        self.assertFalse(self.error_manager.has_warnings())
        self.assertEqual(len(self.error_manager.errors), 0)
        self.assertEqual(len(self.error_manager.warnings), 0)

if __name__ == '__main__':
    unittest.main()