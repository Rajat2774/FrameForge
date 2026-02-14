import ast
from dataclasses import dataclass
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of code validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    scene_name: Optional[str] = None
    
    def __str__(self) -> str:
        status = "✓ VALID" if self.is_valid else "✗ INVALID"
        msg = f"{status}"
        if self.scene_name:
            msg += f" - Scene: {self.scene_name}"
        if self.errors:
            msg += f"\nErrors: {', '.join(self.errors)}"
        if self.warnings:
            msg += f"\nWarnings: {', '.join(self.warnings)}"
        return msg


class ManimCodeValidator:
    """
    Validates LLM-generated Manim code before execution.
    Uses AST parsing to ensure safety and correct structure.
    """

    # Security: Dangerous imports that could compromise system
    DANGEROUS_IMPORTS = {
        "os", "sys", "subprocess", "shutil", "pathlib",
        "socket", "requests", "urllib", "urllib3", "http",
        "ftplib", "smtplib", "pickle", "shelve",
        "importlib", "builtins", "__builtin__"
    }

    # Security: Dangerous built-in functions
    DANGEROUS_FUNCTIONS = {
        "eval", "exec", "__import__", "compile",
        "open", "input", "raw_input",
        "getattr", "setattr", "delattr",
        "globals", "locals", "vars"
    }
    
    # Dangerous attributes that could be abused
    DANGEROUS_ATTRIBUTES = {
        "__dict__", "__class__", "__bases__", "__subclasses__",
        "__globals__", "__code__", "__builtins__"
    }
    
    # Common method hallucinations by LLMs
    NONEXISTENT_METHODS = {
        "move_along_path",  # Use MoveAlongPath(obj, path) instead
        "animate_along_path",
        "follow_path",
        "trace_path"
    }

    REQUIRED_IMPORT = "from manim import *"
    
    MAX_CODE_LENGTH = 10000  # Maximum characters in code
    MAX_LOOP_DEPTH = 3  # Maximum nested loop depth

    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator.
        
        Args:
            strict_mode: If True, apply stricter validation rules
        """
        self.strict_mode = strict_mode
        logger.info(f"Initialized ManimCodeValidator (strict_mode={strict_mode})")

    def validate(self, code: str) -> ValidationResult:
        """
        Validate generated Manim code.
        
        Args:
            code: Python code string to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        errors = []
        warnings = []
        
        # Basic checks
        if not code or not code.strip():
            return ValidationResult(False, ["Code is empty"], [])
        
        if len(code) > self.MAX_CODE_LENGTH:
            errors.append(f"Code too long ({len(code)} > {self.MAX_CODE_LENGTH} chars)")
        
        if self.REQUIRED_IMPORT not in code:
            errors.append("Missing 'from manim import *' import")
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return ValidationResult(
                False,
                [f"Syntax error at line {e.lineno}: {e.msg}"],
                []
            )
        except Exception as e:
            return ValidationResult(
                False,
                [f"Failed to parse code: {str(e)}"],
                []
            )
        
        # Walk the AST and validate
        scene_name = None
        loop_depth = 0
        max_loop_depth_seen = 0
        
        for node in ast.walk(tree):
            # Check for dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.DANGEROUS_IMPORTS:
                        errors.append(f"Forbidden import: {alias.name}")
                    elif alias.name not in {"manim", "numpy", "math"}:
                        warnings.append(f"Unexpected import: {alias.name}")
            
            if isinstance(node, ast.ImportFrom):
                if node.module in self.DANGEROUS_IMPORTS:
                    errors.append(f"Forbidden import: {node.module}")
                elif node.module and node.module not in {"manim"}:
                    warnings.append(f"Unexpected import from: {node.module}")
            
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_FUNCTIONS:
                        errors.append(f"Forbidden function: {node.func.id}()")
            
            # Check for dangerous attribute access
            if isinstance(node, ast.Attribute):
                if node.attr in self.DANGEROUS_ATTRIBUTES:
                    errors.append(f"Forbidden attribute access: {node.attr}")
                
                # Check for common LLM hallucinations
                if node.attr in self.NONEXISTENT_METHODS:
                    errors.append(
                        f"Method '{node.attr}()' does not exist in Manim. "
                        f"Use MoveAlongPath(obj, path) instead of obj.animate.move_along_path()"
                    )
            
            # Check for file operations
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == "open":
                        errors.append("File operations not allowed")
            
            # Detect Scene class
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from Scene
                is_scene = False
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == "Scene":
                        is_scene = True
                        if scene_name is not None:
                            errors.append("Multiple Scene classes found (only one allowed)")
                        scene_name = node.name
                
                if is_scene:
                    # Validate Scene class structure
                    has_construct = False
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name == "construct":
                            has_construct = True
                            # Check if construct has self parameter
                            if not item.args.args or item.args.args[0].arg != "self":
                                errors.append("construct() must have 'self' as first parameter")
                    
                    if not has_construct:
                        errors.append(f"Scene '{scene_name}' missing construct() method")
            
            # Track loop depth
            if isinstance(node, (ast.For, ast.While)):
                loop_depth += 1
                max_loop_depth_seen = max(max_loop_depth_seen, loop_depth)
        
        # Check loop depth
        if max_loop_depth_seen > self.MAX_LOOP_DEPTH:
            warnings.append(
                f"Deep loop nesting detected (depth {max_loop_depth_seen}), "
                "may cause long render times"
            )
        
        # Validate Scene class was found
        if not scene_name:
            errors.append("No Scene class found")
        
        # Additional strict mode checks
        if self.strict_mode:
            self._strict_validation(code, tree, warnings)
        
        is_valid = len(errors) == 0
        
        result = ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            scene_name=scene_name
        )
        
        logger.info(f"Validation result: {result}")
        return result
    
    def _strict_validation(self, code: str, tree: ast.AST, warnings: List[str]):
        """Apply additional strict validation rules."""
        
        # Check for common anti-patterns
        if "while True" in code:
            warnings.append("Infinite loop detected (while True)")
        
        # Check for recursion
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            if child.func.id == node.name:
                                warnings.append(f"Recursive function detected: {node.name}()")
        
        # Check for very long animations
        wait_count = code.count("self.wait(")
        if wait_count > 20:
            warnings.append(f"Many wait() calls ({wait_count}), animation may be very long")


def validate_manim_code(code: str) -> ValidationResult:
    """
    Convenience function for validating Manim code.
    
    Args:
        code: Python code string to validate
        
    Returns:
        ValidationResult
    """
    validator = ManimCodeValidator()
    return validator.validate(code)