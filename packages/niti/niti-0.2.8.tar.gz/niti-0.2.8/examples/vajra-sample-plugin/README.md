# Vajra Sample Plugin for Niti

This is a sample plugin demonstrating how to create custom linting rules for Niti using a custom plugin. The Vajra plugin serves as a reference implementation demonstrating best practices for extending Niti with custom rules.

## Overview 
Niti's plugin system allows you to extend the linter with custom C++ coding rules without modifying the core codebase. Plugins are discovered and loaded dynamically using Python's entry point mechanism.


## Features

This plugin provides 2 project Vajra specific linting rules:

1. **include-missing-pch**: Enforces that all C++ source files include the precompiled header
2. **file-include-strategy**: Suggests using forward declarations instead of includes when possible

## Installation

```bash
# Install the plugin
pip install -e .
```

## Configuration

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

### Key Components

1. **Plugin Class**: Inherits from `NitiPlugin` and defines available rules
2. **Rule Classes**: Inherit from `Rule` and implement the checking logic
3. **Entry Point**: Registered in `pyproject.toml` for discovery
4. **Configuration**: Optional plugin-specific settings


## Developing Plugins

### Step 1: Clone plugin
Copy the Vajra example plugin to the custom project directory

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

See the Niti Linter code for more complex rule examples

## Testing

The plugins should be tested by using comprehensive unit tests to ensure that the rules are doing what they're supposed to do

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

