"""
Test Standard Library
"""

import unittest
import math
from ..stdlib.core import StandardLibrary

class TestStandardLibrary(unittest.TestCase):
    """Test standard library functions and constants"""
    
    def setUp(self):
        self.stdlib = StandardLibrary()
    
    def test_mathematical_functions(self):
        """Test mathematical functions"""
        # Test basic math functions
        sin_func = self.stdlib.get_function("SIN")
        self.assertIsNotNone(sin_func)
        self.assertAlmostEqual(sin_func(math.pi/2), 1.0, places=10)
        
        sqrt_func = self.stdlib.get_function("SQRT")
        self.assertIsNotNone(sqrt_func)
        self.assertEqual(sqrt_func(16), 4.0)
        self.assertEqual(sqrt_func(25), 5.0)
        
        # Test error handling for invalid input
        with self.assertRaises(Exception):
            sqrt_func(-1)  # Should raise error for negative number
    
    def test_string_functions(self):
        """Test string manipulation functions"""
        len_func = self.stdlib.get_function("LEN")
        self.assertEqual(len_func("hello"), 5)
        self.assertEqual(len_func(""), 0)
        
        upper_func = self.stdlib.get_function("UPPER$")
        self.assertEqual(upper_func("hello"), "HELLO")
        
        left_func = self.stdlib.get_function("LEFT$")
        self.assertEqual(left_func("hello", 3), "hel")
        
        mid_func = self.stdlib.get_function("MID$")
        self.assertEqual(mid_func("hello", 2, 3), "ell")
    
    def test_type_conversion(self):
        """Test type conversion functions"""
        val_func = self.stdlib.get_function("VAL")
        self.assertEqual(val_func("123"), 123)
        self.assertEqual(val_func("123.45"), 123.45)
        self.assertEqual(val_func(""), 0)
        
        str_func = self.stdlib.get_function("STR$")
        self.assertEqual(str_func(123), "123")
        self.assertEqual(str_func(123.45), "123.45")
        
        int_func = self.stdlib.get_function("INT")
        self.assertEqual(int_func(123.67), 123)
        self.assertEqual(int_func("456"), 456)
    
    def test_constants(self):
        """Test mathematical constants"""
        pi = self.stdlib.get_constant("PI")
        self.assertAlmostEqual(pi, math.pi)
        
        e = self.stdlib.get_constant("E")
        self.assertAlmostEqual(e, math.e)
        
        true_val = self.stdlib.get_constant("TRUE")
        self.assertTrue(true_val)
        
        false_val = self.stdlib.get_constant("FALSE")
        self.assertFalse(false_val)
    
    def test_random_functions(self):
        """Test random number functions"""
        rnd_func = self.stdlib.get_function("RND")
        
        # Test that RND returns value between 0 and 1
        for _ in range(10):
            val = rnd_func()
            self.assertGreaterEqual(val, 0.0)
            self.assertLess(val, 1.0)
        
        randint_func = self.stdlib.get_function("RANDINT")
        
        # Test RANDINT returns integer in range
        for _ in range(10):
            val = randint_func(1, 10)
            self.assertIsInstance(val, int)
            self.assertGreaterEqual(val, 1)
            self.assertLessEqual(val, 10)
    
    def test_system_functions(self):
        """Test system functions"""
        time_func = self.stdlib.get_function("TIME$")
        time_str = time_func()
        self.assertIsInstance(time_str, str)
        self.assertRegex(time_str, r'\\d{2}:\\d{2}:\\d{2}')
        
        date_func = self.stdlib.get_function("DATE$")
        date_str = date_func()
        self.assertIsInstance(date_str, str)
        self.assertRegex(date_str, r'\\d{4}-\\d{2}-\\d{2}')
    
    def test_array_functions(self):
        """Test array/list functions"""
        reverse_func = self.stdlib.get_function("REVERSE")
        result = reverse_func([1, 2, 3, 4])
        self.assertEqual(list(result), [4, 3, 2, 1])
        
        sort_func = self.stdlib.get_function("SORT")
        result = sort_func([3, 1, 4, 1, 5])
        self.assertEqual(result, [1, 1, 3, 4, 5])
    
    def test_custom_function_registration(self):
        """Test registering custom functions"""
        def custom_double(x):
            return x * 2
        
        # Register function
        self.stdlib.register_function("DOUBLE", custom_double)
        
        # Test it works
        double_func = self.stdlib.get_function("DOUBLE")
        self.assertIsNotNone(double_func)
        self.assertEqual(double_func(5), 10)
        
        # Test overwrite protection
        with self.assertRaises(ValueError):
            self.stdlib.register_function("DOUBLE", custom_double)
        
        # Test overwrite allowed
        self.stdlib.register_function("DOUBLE", lambda x: x * 3, overwrite=True)
        triple_func = self.stdlib.get_function("DOUBLE")
        self.assertEqual(triple_func(5), 15)
    
    def test_error_handling(self):
        """Test error handling in functions"""
        # Test undefined constant
        with self.assertRaises(Exception):
            self.stdlib.get_constant("UNDEFINED_CONSTANT")
        
        # Test division by zero in safe functions
        log_func = self.stdlib.get_function("LOG")
        with self.assertRaises(Exception):
            log_func(0)  # log(0) should raise error
        
        # Test invalid type conversion
        int_func = self.stdlib.get_function("INT")
        with self.assertRaises(Exception):
            int_func("not_a_number")

if __name__ == '__main__':
    unittest.main()