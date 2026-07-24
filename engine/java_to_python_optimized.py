"""
Optimized Java to Python Converter with Regex-based Pattern Matching
"""
import re
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Regex patterns for Java syntax elements
PATTERNS = {
    'print': re.compile(r'System\.out\.print(?:ln)?\((.*)\);?'),
    'variable': re.compile(r'(public\s+)?(static\s+)?(int|float|double|long|boolean|String|char)\s+(\w+)\s*=\s*(.+?)(?:;|$)'),
    'var_decl': re.compile(r'(public\s+)?(static\s+)?(int|float|double|long|boolean|String|char)\s+(\w+)(?:;|$)'),
    'if': re.compile(r'if\s*\((.*?)\)\s*\{?'),
    'else_if': re.compile(r'else\s+if\s*\((.*?)\)\s*\{?'),
    'else': re.compile(r'else\s*\{?'),
    'for_loop': re.compile(r'for\s*\(\s*(int|Integer)\s+(\w+)\s*=\s*(\d+);\s*\2\s*<\s*(\d+);\s*\2\+\+\s*\)'),
    'for_enhanced': re.compile(r'for\s*\(\s*(\w+)\s+(\w+)\s*:\s*(.+?)\s*\)'),
    'while': re.compile(r'while\s*\((.*?)\)\s*\{?'),
    'method': re.compile(r'(public\s+)?(static\s+)?(void|int|String|boolean|double|float)\s+(\w+)\s*\((.*?)\)'),
    'comment': re.compile(r'//.*$'),
}

# Java to Python type mappings
TYPE_MAPPINGS = {
    'int': 'int',
    'float': 'float',
    'double': 'float',
    'long': 'int',
    'boolean': 'bool',
    'String': 'str',
    'char': 'str',
    'void': 'None',
}

JAVA_TO_PYTHON_KEYWORDS = {
    'true': 'True',
    'false': 'False',
    'null': 'None',
}


def clean_line(line: str) -> str:
    """Remove trailing semicolons and clean line"""
    return line.rstrip().rstrip(';')


def convert_java_string(java_str: str) -> str:
    """Convert Java string literals to Python"""
    # Handle string concatenation
    java_str = re.sub(r'\s*\+\s*', ' + ', java_str)
    # Convert null to None
    java_str = re.sub(r'\bnull\b', 'None', java_str)
    return java_str


def convert_java_values(value: str) -> str:
    """Convert Java values to Python equivalents"""
    value = value.strip()
    
    # Replace Java keywords with Python equivalents
    for java_kw, py_kw in JAVA_TO_PYTHON_KEYWORDS.items():
        value = re.sub(rf'\b{java_kw}\b', py_kw, value)
    
    return value


def process_print_statement(line: str) -> Optional[str]:
    """Convert System.out.println/print to Python print"""
    match = PATTERNS['print'].search(line)
    if match:
        content = match.group(1).strip()
        content = convert_java_string(content)
        return f"print({content})"
    return None


def process_variable_declaration(line: str) -> Optional[str]:
    """Convert Java variable declaration to Python"""
    match = PATTERNS['variable'].search(line)
    if match:
        _, is_static, var_type, var_name, var_value = match.groups()
        var_value = convert_java_values(var_value.strip())
        return f"{var_name} = {var_value}"
    
    # Variable declaration without initialization
    match = PATTERNS['var_decl'].search(line)
    if match:
        _, is_static, var_type, var_name = match.groups()
        default_value = get_default_value(var_type)
        return f"{var_name} = {default_value}"
    
    return None


def process_if_statement(line: str) -> Optional[str]:
    """Convert if statement"""
    match = PATTERNS['if'].search(line)
    if match:
        condition = match.group(1).strip()
        condition = convert_java_values(condition)
        return f"if {condition}:"
    return None


def process_else_if_statement(line: str) -> Optional[str]:
    """Convert else if statement"""
    match = PATTERNS['else_if'].search(line)
    if match:
        condition = match.group(1).strip()
        condition = convert_java_values(condition)
        return f"elif {condition}:"
    return None


def process_else_statement(line: str) -> Optional[str]:
    """Convert else statement"""
    match = PATTERNS['else'].search(line)
    if match:
        return "else:"
    return None


def process_for_loop(line: str) -> Optional[str]:
    """Convert for loop"""
    # C-style for loop
    match = PATTERNS['for_loop'].search(line)
    if match:
        var, start, end = match.groups()[1:4]
        return f"for {var} in range({start}, {end}):"
    
    # Enhanced for loop
    match = PATTERNS['for_enhanced'].search(line)
    if match:
        var_type, var_name, iterable = match.groups()
        iterable = convert_java_values(iterable.strip())
        return f"for {var_name} in {iterable}:"
    
    return None


def process_while_loop(line: str) -> Optional[str]:
    """Convert while loop"""
    match = PATTERNS['while'].search(line)
    if match:
        condition = match.group(1).strip()
        condition = convert_java_values(condition)
        return f"while {condition}:"
    return None


def process_method_definition(line: str) -> Optional[str]:
    """Convert method definition"""
    match = PATTERNS['method'].search(line)
    if match:
        _, is_static, return_type, method_name, params = match.groups()
        # Simple conversion - doesn't handle parameter types
        params_list = [p.split()[-1].strip() for p in params.split(',') if p.strip()]
        params_str = ', '.join(params_list) if params_list else ''
        return f"def {method_name}({params_str}):"
    return None


def get_default_value(var_type: str) -> str:
    """Get default value for Java type"""
    defaults = {
        'int': '0',
        'float': '0.0',
        'double': '0.0',
        'long': '0',
        'boolean': 'False',
        'String': '""',
        'char': '""',
    }
    return defaults.get(var_type, 'None')


def convert(code: str) -> str:
    """
    Convert Java code to Python
    
    Args:
        code: Java source code as string
        
    Returns:
        Python source code as string
    """
    if not code or not code.strip():
        logger.warning("Empty code provided for conversion")
        return ""
    
    lines = code.split("\n")
    output = []
    indent_level = 0
    
    for i, line in enumerate(lines, 1):
        try:
            stripped = line.strip()
            
            # Skip empty lines and closing braces
            if not stripped or stripped == "}":
                if stripped == "}":
                    indent_level = max(0, indent_level - 1)
                continue
            
            # Skip comments
            if stripped.startswith("//"):
                output.append(f"# {stripped[2:].strip()}")
                continue
            
            # Skip import statements for now (can be enhanced)
            if stripped.startswith("import "):
                output.append(f"# {stripped}")
                continue
            
            converted_line = None
            
            # Try conversions in order of specificity
            if "System.out.print" in stripped:
                converted_line = process_print_statement(stripped)
            
            elif "else if" in stripped:
                converted_line = process_else_if_statement(stripped)
            
            elif stripped.startswith("if"):
                converted_line = process_if_statement(stripped)
            
            elif stripped.startswith("else"):
                converted_line = process_else_statement(stripped)
            
            elif "while" in stripped:
                converted_line = process_while_loop(stripped)
            
            elif "for" in stripped:
                converted_line = process_for_loop(stripped)
            
            elif "(" in stripped and ")" in stripped and "def" not in converted_line if converted_line else False:
                converted_line = process_method_definition(stripped)
            
            elif any(var_type in stripped for var_type in ['int', 'String', 'float', 'double', 'boolean']):
                converted_line = process_variable_declaration(stripped)
            
            else:
                # Default: clean the line
                converted_line = clean_line(stripped)
            
            if converted_line:
                # Add indentation
                indent = "    " * indent_level
                output.append(indent + converted_line)
                
                # Increase indent for lines ending with ':'
                if converted_line.endswith(":"):
                    indent_level += 1
            
        except Exception as e:
            logger.warning(f"Error converting line {i}: {e}")
            # Add line as-is in comment form
            output.append(f"# ERROR: {line}")
    
    return "\n".join(output)
