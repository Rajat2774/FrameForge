import unittest
from validator import ManimCodeValidator, ValidationResult


class TestManimCodeValidator(unittest.TestCase):
    """Test suite for ManimCodeValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = ManimCodeValidator(strict_mode=True)
    
    def test_valid_simple_code(self):
        """Test validation of simple valid code."""
        code = """from manim import *

class SimpleScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()
"""
        result = self.validator.validate(code)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.scene_name, "SimpleScene")
        self.assertEqual(len(result.errors), 0)
    
    def test_missing_import(self):
        """Test detection of missing import."""
        code = """class SimpleScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()
"""
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertIn("Missing 'from manim import *'", result.errors)
    
    def test_dangerous_import_os(self):
        """Test detection of dangerous import (os)."""
        code = """from manim import *
import os

class BadScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()
"""
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertIn("Forbidden import: os", result.errors)
    
    def test_dangerous_function_eval(self):
        """Test detection of dangerous function (eval)."""
        code = """from manim import *

class BadScene(Scene):
    def construct(self):
        x = eval("1+1")
        circle = Circle()
        self.play(Create(circle))
        self.wait()
"""
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertIn("Forbidden function: eval()", result.errors)
    
    def test_dangerous_function_open(self):
        """Test detection of file operations."""
        code = """from manim import *

class BadScene(Scene):
    def construct(self):
        f = open("test.txt", "w")
        circle = Circle()
        self.play(Create(circle))
        self.wait()
"""
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any("open" in error.lower() for error in result.errors)
        )
    
    def test_no_scene_class(self):
        """Test detection of missing Scene class."""
        code = """from manim import *

def my_function():
    circle = Circle()
    return circle
"""
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertIn("No Scene class found", result.errors)
    
    def test_missing_construct_method(self):
        """Test detection of missing construct method."""
        code = """from manim import *

class BadScene(Scene):
    def render(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()
"""
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any("construct" in error for error in result.errors)
        )
    
    def test_empty_code(self):
        """Test validation of empty code."""
        result = self.validator.validate("")
        self.assertFalse(result.is_valid)
        self.assertIn("Code is empty", result.errors)
    
    def test_syntax_error(self):
        """Test detection of syntax errors."""
        code = """from manim import *

class BadScene(Scene):
    def construct(self):
        circle = Circle(
        self.play(Create(circle))
        self.wait()
"""
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any("Syntax error" in error for error in result.errors)
        )
    
    def test_multiple_scenes(self):
        """Test detection of multiple Scene classes."""
        code = """from manim import *

class Scene1(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()

class Scene2(Scene):
    def construct(self):
        square = Square()
        self.play(Create(square))
        self.wait()
"""
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any("Multiple Scene" in error for error in result.errors)
        )
    
    def test_dangerous_attribute_access(self):
        """Test detection of dangerous attribute access."""
        code = """from manim import *

class BadScene(Scene):
    def construct(self):
        x = self.__dict__
        circle = Circle()
        self.play(Create(circle))
        self.wait()
"""
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any("__dict__" in error for error in result.errors)
        )
    
    def test_code_too_long(self):
        """Test detection of code that's too long."""
        code = "from manim import *\n" + "# comment\n" * 10000
        result = self.validator.validate(code)
        self.assertFalse(result.is_valid)
        self.assertTrue(
            any("too long" in error.lower() for error in result.errors)
        )
    
    def test_valid_with_warnings(self):
        """Test code that's valid but has warnings."""
        code = """from manim import *

class LongScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
""" + "        self.wait(1)\n" * 25  # Many wait calls
        
        result = self.validator.validate(code)
        self.assertTrue(result.is_valid)
        self.assertTrue(len(result.warnings) > 0)
    
    def test_non_strict_mode(self):
        """Test validator in non-strict mode."""
        validator = ManimCodeValidator(strict_mode=False)
        code = """from manim import *

class SimpleScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()
"""
        result = validator.validate(code)
        self.assertTrue(result.is_valid)


if __name__ == "__main__":
    unittest.main()