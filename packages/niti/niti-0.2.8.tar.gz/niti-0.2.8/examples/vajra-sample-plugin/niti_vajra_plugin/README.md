# Niti Plugin Development Guide

This document provides comprehensive guidance on developing custom plugins for Niti, the C++ linter. The Vajra plugin serves as a reference implementation demonstrating best practices for extending Niti with custom rules.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Plugin Architecture](#plugin-architecture)
4. [Creating a Plugin](#creating-a-plugin)
5. [Writing Custom Rules](#writing-custom-rules)
6. [Plugin Configuration](#plugin-configuration)
7. [Testing Your Plugin](#testing-your-plugin)
8. [Publishing Your Plugin](#publishing-your-plugin)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Overview

Niti's plugin system allows you to extend the linter with custom C++ coding rules without modifying the core codebase. Plugins are discovered and loaded dynamically using Python's entry point mechanism.

### Key Features

- **Namespace Isolation**: Plugin rules are automatically namespaced (e.g., `vajra/include-missing-pch`)
- **Version Compatibility**: Specify minimum Niti version requirements
- **Configuration Support**: Plugin-specific settings via `.nitirc`
- **Error Isolation**: Plugin failures don't crash the main linter
- **Standard Python Packaging**: Use familiar tools like pip and pyproject.toml

## Quick Start

### Installing a Plugin

```bash
# Install from PyPI
pip install niti-vajra-plugin

# Install from source
pip install -e ./path/to/plugin
```

### Enabling a Plugin

Add to your `.nitirc`:

```yaml
plugins:
  enabled:
    - vajra  # Plugin name from entry point
  config:
    vajra:
      # Plugin-specific configuration
      pch_path: "commons/PrecompiledHeaders.h"

rules:
  # Enable/disable specific plugin rules
  vajra/include-missing-pch:
    enabled: true
    severity: error
  vajra/avoid-forward-declarations:
    enabled: false
```

### Using the Plugin

```bash
# Run Niti with plugins enabled
niti src/main.cpp

# The plugin rules will be applied automatically
```

## Plugin Architecture

### Directory Structure

```
my-niti-plugin/
├── pyproject.toml              # Package configuration with entry point
├── README.md                   # Plugin documentation
├── LICENSE                     # Plugin license
├── src/
│   └── my_niti_plugin/
│       ├── __init__.py
│       ├── plugin.py          # Main plugin class
│       └── rules/             # Rule implementations
│           ├── __init__.py
│           ├── rule1.py
│           └── rule2.py
└── tests/                     # Plugin tests
    ├── __init__.py
    └── test_rules.py
```

### Key Components

1. **Plugin Class**: Inherits from `NitiPlugin` and defines available rules
2. **Rule Classes**: Inherit from `Rule` and implement the checking logic
3. **Entry Point**: Registered in `pyproject.toml` for discovery
4. **Configuration**: Optional plugin-specific settings

## Creating a Plugin

### Step 1: Set Up Project Structure

Create a new directory and initialize the project:

```bash
mkdir niti-my-plugin
cd niti-my-plugin
mkdir -p src/niti_my_plugin/rules
touch src/niti_my_plugin/__init__.py
touch src/niti_my_plugin/plugin.py
touch src/niti_my_plugin/rules/__init__.py
```

### Step 2: Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "niti-my-plugin"
version = "0.1.0"
description = "Custom rules for Niti C++ linter"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
dependencies = [
    "niti>=0.1.0",  # Minimum Niti version
]

[project.entry-points."niti.plugins"]
my_plugin = "niti_my_plugin.plugin:MyPlugin"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
"*" = ["py.typed"]
```

### Step 3: Implement the Plugin Class

Create `src/niti_my_plugin/plugin.py`:

```python
"""Main plugin implementation for My Plugin."""
from typing import Dict, List, Optional, Any

from niti.plugins.base import NitiPlugin, PluginRuleDefinition
from niti.core.issue import Severity

# Import your rule classes
from .rules.example_rule import ExampleRule
from .rules.another_rule import AnotherRule


class MyPlugin(NitiPlugin):
    """My custom Niti plugin."""
    
    def __init__(self):
        """Initialize the plugin."""
        super().__init__()
        self._config: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Return the plugin name."""
        return "my_plugin"
    
    @property
    def version(self) -> str:
        """Return the plugin version."""
        return "0.1.0"
    
    @property
    def min_niti_version(self) -> Optional[str]:
        """Return minimum required Niti version."""
        return "0.1.0"
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the plugin with user settings.
        
        Args:
            config: Plugin configuration from .nitirc
        """
        self._config = config
    
    def get_rules(self) -> List[PluginRuleDefinition]:
        """Return list of rules provided by this plugin.
        
        Returns:
            List of rule definitions
        """
        return [
            PluginRuleDefinition(
                id="example-rule",
                rule_class=ExampleRule,
                severity=Severity.WARNING,
                enabled=True
            ),
            PluginRuleDefinition(
                id="another-rule", 
                rule_class=AnotherRule,
                severity=Severity.ERROR,
                enabled=True
            ),
        ]
```

## Writing Custom Rules

### Basic Rule Structure

Create `src/niti_my_plugin/rules/example_rule.py`:

```python
"""Example rule implementation."""
from typing import List, Optional

from tree_sitter import Node

from niti.rules.base import Rule
from niti.core.issue import Issue, Severity


class ExampleRule(Rule):
    """Example rule that checks for specific patterns."""
    
    def __init__(self):
        """Initialize the rule."""
        super().__init__(
            id="example-rule",
            name="Example Rule", 
            description="Checks for example patterns in C++ code",
            severity=Severity.WARNING
        )
    
    def check(self, node: Node, source_code: bytes) -> List[Issue]:
        """Check the AST node for rule violations.
        
        Args:
            node: Tree-sitter AST node to check
            source_code: Original source code bytes
            
        Returns:
            List of issues found
        """
        issues = []
        
        # Example: Check for specific node types
        if node.type == "function_definition":
            # Get function name
            name_node = self._find_child_by_type(node, "function_declarator")
            if name_node:
                func_name = self._get_node_text(name_node, source_code)
                
                # Example rule: Function names should not start with underscore
                if func_name.startswith("_"):
                    issues.append(
                        Issue(
                            rule_id=self.id,
                            message=f"Function '{func_name}' should not start with underscore",
                            file_path="",  # Will be set by the engine
                            line_number=node.start_point[0] + 1,
                            column_number=node.start_point[1] + 1,
                            severity=self.severity
                        )
                    )
        
        # Recursively check children
        for child in node.children:
            issues.extend(self.check(child, source_code))
        
        return issues
    
    def _find_child_by_type(self, node: Node, type_name: str) -> Optional[Node]:
        """Find first child node of given type."""
        for child in node.children:
            if child.type == type_name:
                return child
            # Recursively search in children
            found = self._find_child_by_type(child, type_name)
            if found:
                return found
        return None
    
    def _get_node_text(self, node: Node, source_code: bytes) -> str:
        """Extract text from a node."""
        return source_code[node.start_byte:node.end_byte].decode('utf-8')
```

### Advanced Rule Example

Here's a more complex rule that uses plugin configuration:

```python
"""Rule that checks for precompiled header inclusion."""
from typing import List, Dict, Any, Optional

from tree_sitter import Node

from niti.rules.base import Rule
from niti.core.issue import Issue, Severity


class PrecompiledHeaderRule(Rule):
    """Ensures all source files include the precompiled header."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the rule with configuration."""
        super().__init__(
            id="include-missing-pch",
            name="Missing Precompiled Header",
            description="Ensures precompiled header is included",
            severity=Severity.ERROR
        )
        self.config = config or {}
        self.pch_path = self.config.get("pch_path", "pch.h")
    
    def check(self, node: Node, source_code: bytes) -> List[Issue]:
        """Check if precompiled header is included."""
        issues = []
        
        # Only check at the root level
        if node.parent is not None:
            return issues
        
        # Look for include directives
        includes = self._find_all_includes(node, source_code)
        
        # Check if PCH is included
        pch_included = any(
            self.pch_path in include_path 
            for include_path in includes
        )
        
        if not pch_included and self._is_source_file(source_code):
            issues.append(
                Issue(
                    rule_id=self.id,
                    message=f"Missing precompiled header: {self.pch_path}",
                    file_path="",
                    line_number=1,
                    column_number=1,
                    severity=self.severity
                )
            )
        
        return issues
    
    def _find_all_includes(self, node: Node, source_code: bytes) -> List[str]:
        """Find all include directives in the file."""
        includes = []
        
        if node.type == "preproc_include":
            # Extract the included file path
            for child in node.children:
                if child.type in ["string_literal", "system_lib_string"]:
                    include_text = source_code[child.start_byte:child.end_byte].decode('utf-8')
                    # Remove quotes
                    include_path = include_text.strip('"<>')
                    includes.append(include_path)
        
        # Recursively check children
        for child in node.children:
            includes.extend(self._find_all_includes(child, source_code))
        
        return includes
    
    def _is_source_file(self, source_code: bytes) -> bool:
        """Determine if this is a source file (not a header)."""
        # Simple heuristic: look for main function or class implementations
        code_str = source_code.decode('utf-8', errors='ignore')
        return "int main(" in code_str or "::" in code_str
```

## Plugin Configuration

### Configuration Schema

Plugins can accept configuration through `.nitirc`:

```yaml
plugins:
  enabled:
    - my_plugin
  config:
    my_plugin:
      # Plugin-specific settings
      option1: "value1"
      option2: 42
      paths:
        - "src/"
        - "include/"

rules:
  # Configure individual plugin rules
  my_plugin/example-rule:
    enabled: true
    severity: error
  my_plugin/another-rule:
    enabled: false
```

### Accessing Configuration in Rules

Rules can receive configuration through their constructor:

```python
class ConfigurableRule(Rule):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            id="configurable-rule",
            name="Configurable Rule",
            description="A rule that uses configuration",
            severity=Severity.WARNING
        )
        self.config = config or {}
        
        # Access plugin configuration
        self.custom_option = self.config.get("custom_option", "default")
        self.threshold = self.config.get("threshold", 10)
```

## Testing Your Plugin

### Unit Testing Rules

Create `tests/test_rules.py`:

```python
"""Tests for plugin rules."""
import unittest
from tree_sitter import Parser, Language

from niti_my_plugin.rules.example_rule import ExampleRule


class TestExampleRule(unittest.TestCase):
    """Test cases for ExampleRule."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.rule = ExampleRule()
        # Initialize tree-sitter parser
        CPP_LANGUAGE = Language("path/to/tree-sitter-cpp.so", "cpp")
        self.parser = Parser()
        self.parser.set_language(CPP_LANGUAGE)
    
    def test_detects_underscore_functions(self):
        """Test that functions starting with underscore are detected."""
        code = b"""
        void _privateFunction() {
            // This should trigger the rule
        }
        
        void publicFunction() {
            // This should not trigger the rule
        }
        """
        
        tree = self.parser.parse(code)
        issues = self.rule.check(tree.root_node, code)
        
        self.assertEqual(len(issues), 1)
        self.assertIn("should not start with underscore", issues[0].message)
    
    def test_no_false_positives(self):
        """Test that valid code doesn't trigger issues."""
        code = b"""
        void validFunction() {
            int _localVar = 42;  // Local variables are OK
        }
        """
        
        tree = self.parser.parse(code)
        issues = self.rule.check(tree.root_node, code)
        
        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
```

### Integration Testing

Test your plugin with actual Niti:

```python
"""Integration tests for the plugin."""
import tempfile
import subprocess
from pathlib import Path


def test_plugin_integration():
    """Test that the plugin works with Niti."""
    # Create a test file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
        f.write("""
        void _badFunction() {
            // This should be caught by our plugin
        }
        """)
        test_file = f.name
    
    # Create a .nitirc configuration
    config = """
    plugins:
      enabled:
        - my_plugin
    rules:
      my_plugin/example-rule:
        enabled: true
    """
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.nitirc', delete=False) as f:
        f.write(config)
        config_file = f.name
    
    try:
        # Run Niti with the plugin
        result = subprocess.run(
            ['niti', '--config', config_file, test_file],
            capture_output=True,
            text=True
        )
        
        # Check that our rule was triggered
        assert "should not start with underscore" in result.stdout
        assert result.returncode != 0  # Should fail due to issues
        
    finally:
        # Cleanup
        Path(test_file).unlink()
        Path(config_file).unlink()
```

## Publishing Your Plugin

### Preparing for Release

1. **Update Version**: Update version in `pyproject.toml`
2. **Write Documentation**: Create comprehensive README.md
3. **Add License**: Include appropriate license file
4. **Test Thoroughly**: Ensure all tests pass

### Building the Package

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# This creates:
# dist/niti_my_plugin-0.1.0-py3-none-any.whl
# dist/niti_my_plugin-0.1.0.tar.gz
```

### Publishing to PyPI

```bash
# Test on TestPyPI first
twine upload --repository testpypi dist/*

# Install from TestPyPI to verify
pip install --index-url https://test.pypi.org/simple/ niti-my-plugin

# Publish to PyPI
twine upload dist/*
```

## Best Practices

### 1. Rule Design

- **Single Responsibility**: Each rule should check for one specific issue
- **Clear Messages**: Provide actionable error messages with context
- **Performance**: Avoid expensive operations in hot paths
- **Configurability**: Make rules flexible with configuration options

### 2. Error Handling

```python
def check(self, node: Node, source_code: bytes) -> List[Issue]:
    """Robust rule implementation."""
    issues = []
    
    try:
        # Your rule logic here
        if self._should_check_node(node):
            issue = self._check_specific_pattern(node, source_code)
            if issue:
                issues.append(issue)
    except Exception as e:
        # Log error but don't crash
        import logging
        logging.error(f"Error in rule {self.id}: {e}")
    
    # Always continue checking children
    for child in node.children:
        issues.extend(self.check(child, source_code))
    
    return issues
```

### 3. Performance Optimization

- **Early Returns**: Skip processing when possible
- **Cache Results**: Store expensive computations
- **Limit Traversal**: Use targeted searches instead of full traversal

```python
class OptimizedRule(Rule):
    def __init__(self):
        super().__init__(...)
        self._cache = {}
    
    def check(self, node: Node, source_code: bytes) -> List[Issue]:
        # Early return for irrelevant nodes
        if node.type not in ["function_definition", "class_specifier"]:
            return []
        
        # Use caching for expensive operations
        cache_key = (node.start_byte, node.end_byte)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        issues = self._perform_check(node, source_code)
        self._cache[cache_key] = issues
        return issues
```

### 4. Documentation

Always include:
- **Rule Rationale**: Why this rule exists
- **Examples**: Good and bad code samples
- **Configuration**: Available options and their effects
- **Performance Impact**: Expected overhead

## Troubleshooting

### Common Issues

#### Plugin Not Found

```
Error: Plugin 'my_plugin' not found
```

**Solution**: Ensure the plugin is installed and the entry point name matches:
```bash
pip list | grep niti-my-plugin
pip show niti-my-plugin | grep Entry
```

#### Configuration Not Applied

**Solution**: Check the plugin name in `.nitirc` matches the entry point:
```yaml
plugins:
  enabled:
    - my_plugin  # Must match entry point name, not package name
```

#### Rule Not Running

**Solution**: Verify the rule is enabled and properly registered:
```yaml
rules:
  my_plugin/example-rule:  # Note the namespace prefix
    enabled: true
```

### Debug Mode

Enable verbose logging to troubleshoot:

```bash
# Set environment variable
export NITI_LOG_LEVEL=DEBUG

# Run Niti
niti --verbose src/main.cpp
```

### Getting Help

- **Issue Tracker**: Report bugs on the plugin's GitHub repository
- **Niti Documentation**: Check the main Niti docs for API changes
- **Community**: Join the Niti community discussions

## Example: Vajra Plugin

The Vajra plugin included in this repository demonstrates these concepts:

1. **Precompiled Header Rule**: Ensures PCH is included in source files
2. **Forward Declaration Rule**: Warns about unnecessary forward declarations
3. **Configuration**: Uses `pch_path` from plugin config
4. **Testing**: Includes comprehensive test suite

Study the Vajra plugin source code for a complete example of a production-ready Niti plugin.

---

For more information about Niti, visit the [main documentation](https://github.com/your-org/niti).