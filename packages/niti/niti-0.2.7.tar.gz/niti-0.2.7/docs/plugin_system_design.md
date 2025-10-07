# Niti Plugin System Design (Revised)

## Overview

The Niti plugin system allows users to extend the linter with project-specific rules without modifying the core codebase. This design follows Python best practices, primarily using setuptools entry points for plugin discovery and registration.

## Architecture

### 1. Plugin Structure

Each plugin is a standard Python package:

```
niti-vajra-plugin/
├── pyproject.toml         # Modern Python packaging
├── README.md
├── niti_vajra_plugin/
│   ├── __init__.py
│   ├── plugin.py          # Plugin entry point
│   └── rules/
│       ├── __init__.py
│       └── pch_rule.py    # Rule implementations
└── tests/
    └── test_rules.py
```

### 2. Core Components

#### 2.1 Plugin Interface (ABC)

```python
# niti/plugins/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Type
from ..rules.base import BaseRule
from ..core.severity import Severity

class PluginRuleDefinition:
    """Definition of a plugin rule."""
    def __init__(
        self,
        rule_id: str,
        rule_class: Type[BaseRule],
        default_severity: Severity = Severity.WARNING,
        default_enabled: bool = True,
        description: str = "",
    ):
        self.rule_id = rule_id
        self.rule_class = rule_class
        self.default_severity = default_severity
        self.default_enabled = default_enabled
        self.description = description

class NitiPlugin(ABC):
    """Abstract base class for all Niti plugins.
    
    Plugins must implement this interface to be recognized by Niti.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier (used for namespacing)."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version (for compatibility checking)."""
        pass
    
    @property
    def description(self) -> str:
        """Human-readable plugin description."""
        return ""
    
    @property
    def min_niti_version(self) -> str:
        """Minimum compatible Niti version."""
        return "1.0.0"
    
    @abstractmethod
    def get_rules(self) -> List[PluginRuleDefinition]:
        """Return list of rules provided by this plugin."""
        pass
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration.
        
        Called once during plugin loading.
        Config contains plugin-specific settings from .nitirc
        """
        pass
```

#### 2.2 Plugin Discovery and Loading

```python
# niti/plugins/loader.py
import importlib.metadata
import logging
from typing import Dict, List, Optional
from packaging import version

logger = logging.getLogger(__name__)

class PluginLoader:
    """Handles plugin discovery and loading via entry points."""
    
    ENTRY_POINT_GROUP = "niti.plugins"
    
    def __init__(self, niti_version: str):
        self.niti_version = niti_version
        self._plugins: Dict[str, NitiPlugin] = {}
        self._plugin_rules: Dict[str, PluginRuleDefinition] = {}
    
    def discover_plugins(self) -> List[str]:
        """Discover all installed plugins via entry points."""
        discovered = []
        
        # Use importlib.metadata for Python 3.8+
        entry_points = importlib.metadata.entry_points()
        if hasattr(entry_points, 'select'):
            # Python 3.10+
            plugin_eps = entry_points.select(group=self.ENTRY_POINT_GROUP)
        else:
            # Python 3.8-3.9
            plugin_eps = entry_points.get(self.ENTRY_POINT_GROUP, [])
        
        for entry_point in plugin_eps:
            discovered.append(entry_point.name)
            
        return discovered
    
    def load_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """Load a specific plugin by name."""
        try:
            # Load the entry point
            entry_points = importlib.metadata.entry_points()
            if hasattr(entry_points, 'select'):
                plugin_eps = entry_points.select(group=self.ENTRY_POINT_GROUP)
            else:
                plugin_eps = entry_points.get(self.ENTRY_POINT_GROUP, [])
            
            for entry_point in plugin_eps:
                if entry_point.name == plugin_name:
                    # Load the plugin class
                    plugin_class = entry_point.load()
                    plugin = plugin_class()
                    
                    # Version compatibility check
                    if not self._check_compatibility(plugin):
                        logger.error(
                            f"Plugin '{plugin.name}' requires Niti >= {plugin.min_niti_version}"
                        )
                        return False
                    
                    # Initialize plugin with config
                    plugin_config = config or {}
                    plugin.initialize(plugin_config)
                    
                    # Register plugin and its rules
                    self._register_plugin(plugin)
                    logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                    return True
                    
            logger.error(f"Plugin '{plugin_name}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            return False
    
    def _check_compatibility(self, plugin: NitiPlugin) -> bool:
        """Check if plugin is compatible with current Niti version."""
        min_version = version.parse(plugin.min_niti_version)
        current_version = version.parse(self.niti_version)
        return current_version >= min_version
    
    def _register_plugin(self, plugin: NitiPlugin) -> None:
        """Register a plugin and its rules."""
        self._plugins[plugin.name] = plugin
        
        # Register each rule with namespaced ID
        for rule_def in plugin.get_rules():
            namespaced_id = f"{plugin.name}/{rule_def.rule_id}"
            self._plugin_rules[namespaced_id] = rule_def
    
    def get_all_rules(self) -> Dict[str, PluginRuleDefinition]:
        """Get all rules from loaded plugins."""
        return self._plugin_rules.copy()
```

#### 2.3 Entry Point Registration

Plugins register themselves via `pyproject.toml`:

```toml
# pyproject.toml for a plugin
[project]
name = "niti-vajra-plugin"
version = "1.0.0"
dependencies = ["niti>=1.0.0"]

[project.entry-points."niti.plugins"]
vajra = "niti_vajra_plugin.plugin:VajraPlugin"
```

Or via `setup.py`:

```python
# setup.py
setup(
    name="niti-vajra-plugin",
    entry_points={
        "niti.plugins": [
            "vajra = niti_vajra_plugin.plugin:VajraPlugin"
        ]
    }
)
```
S
### 3. Configuration

Plugin configuration in `.nitirc`:

```yaml
# Plugin configuration
plugins:
  # List of plugins to load (by entry point name)
  enabled:
    - vajra
    - my-team-rules
  
  # Plugin-specific configuration
  config:
    vajra:
      pch_path: "commons/PrecompiledHeaders.h"
      enforce_pch: true
    
# Rule configuration (including plugin rules)
rules:
  # Core rules
  naming-variable-case:
    enabled: true
    severity: error
    
  # Plugin rules use namespaced IDs
  vajra/include-missing-pch:
    enabled: true
    severity: error
  
  vajra/some-other-rule:
    enabled: false
```

### 4. Integration with Existing Systems

#### 4.1 Rule Registry Integration

```python
# niti/rules/registry.py (updated)
class RuleRegistry:
    """Registry for managing rule implementations and metadata."""
    
    def __init__(self):
        self._rules: Dict[str, Type["BaseRule"]] = {}
        self._plugin_loader: Optional[PluginLoader] = None
        # ... existing code ...
    
    def load_plugins(self, plugin_config: Dict[str, Any]) -> None:
        """Load configured plugins and their rules."""
        if not self._plugin_loader:
            from ..plugins.loader import PluginLoader
            self._plugin_loader = PluginLoader(__version__)
        
        enabled_plugins = plugin_config.get('enabled', [])
        plugin_configs = plugin_config.get('config', {})
        
        for plugin_name in enabled_plugins:
            config = plugin_configs.get(plugin_name, {})
            self._plugin_loader.load_plugin(plugin_name, config)
        
        # Register plugin rules
        for rule_id, rule_def in self._plugin_loader.get_all_rules().items():
            self.register_plugin_rule(rule_id, rule_def)
    
    def register_plugin_rule(self, rule_id: str, rule_def: PluginRuleDefinition) -> None:
        """Register a plugin rule."""
        # Create a dynamic RuleId for plugin rules
        self._rules[rule_id] = rule_def.rule_class
        # Handle severity and enabled state from config
```

#### 4.2 Engine Integration

```python
# niti/core/engine.py (updated)
class LintEngine:
    def __init__(self, config: LinterConfig):
        self.config = config
        self.registry = registry
        
        # Load plugins if configured
        if 'plugins' in config:
            self.registry.load_plugins(config['plugins'])
```

### 5. Example: Vajra Plugin Implementation

```python
# niti_vajra_plugin/plugin.py
from niti.plugins.base import NitiPlugin, PluginRuleDefinition
from niti.core.severity import Severity
from .rules.pch_rule import IncludeMissingPchRule

class VajraPlugin(NitiPlugin):
    """Vajra-specific linting rules for C++ projects."""
    
    @property
    def name(self) -> str:
        return "vajra"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    @property
    def description(self) -> str:
        return "Vajra-specific C++ linting rules including PCH enforcement"
    
    @property
    def min_niti_version(self) -> str:
        return "1.0.0"
    
    def __init__(self):
        self.config = {}
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        self.config = config
        # Pass config to rules that need it
        IncludeMissingPchRule.pch_path = config.get('pch_path', 'commons/PrecompiledHeaders.h')
    
    def get_rules(self) -> List[PluginRuleDefinition]:
        """Return Vajra-specific rules."""
        return [
            PluginRuleDefinition(
                rule_id="include-missing-pch",
                rule_class=IncludeMissingPchRule,
                default_severity=Severity.ERROR,
                default_enabled=True,
                description="Enforce precompiled header inclusion"
            ),
            # Add more Vajra-specific rules here
        ]
```

```python
# niti_vajra_plugin/rules/pch_rule.py
from typing import Any, List
from niti.rules.base import BaseRule, AutofixResult
from niti.core.issue import LintIssue
from niti.core.severity import Severity

class IncludeMissingPchRule(BaseRule):
    """Rule to detect missing PrecompiledHeaders.h inclusion."""
    
    # Class variable to store PCH path from config
    pch_path = "commons/PrecompiledHeaders.h"
    
    def __init__(self):
        # Plugin rules don't use RuleId enum
        super().__init__(rule_id="vajra/include-missing-pch", severity=Severity.ERROR)
        self.supports_autofix = True
    
    def check(self, file_path: str, content: str, tree: Any, config: Any) -> List[LintIssue]:
        # Implementation moved from original rule
        # Use self.pch_path instead of hardcoded path
        # ... rest of implementation ...
```

### 6. CLI Integration

```python
# niti/cli.py (updated)
def add_plugin_arguments(parser):
    """Add plugin-related arguments."""
    plugin_group = parser.add_argument_group('Plugin Options')
    
    plugin_group.add_argument(
        '--list-plugins',
        action='store_true',
        help='List all available plugins'
    )
    
    plugin_group.add_argument(
        '--plugin',
        action='append',
        help='Enable specific plugin(s)'
    )
    
    plugin_group.add_argument(
        '--disable-plugin',
        action='append',
        help='Disable specific plugin(s)'
    )

def handle_plugin_commands(args, config):
    """Handle plugin-related commands."""
    if args.list_plugins:
        from niti.plugins.loader import PluginLoader
        loader = PluginLoader(__version__)
        plugins = loader.discover_plugins()
        print("Available plugins:")
        for plugin in plugins:
            print(f"  - {plugin}")
        return True
    
    # Override config with CLI options
    if args.plugin:
        config.setdefault('plugins', {})
        config['plugins']['enabled'] = args.plugin
    
    if args.disable_plugin:
        # Remove from enabled list
        pass
```

### 7. Error Handling and Isolation

```python
# niti/plugins/loader.py (additions)
class PluginLoader:
    def load_plugin_safe(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """Load plugin with error isolation."""
        try:
            return self.load_plugin(plugin_name, config)
        except Exception as e:
            logger.error(f"Plugin '{plugin_name}' failed to load: {e}")
            # Continue without the plugin
            return False
    
    def validate_plugin(self, plugin: NitiPlugin) -> List[str]:
        """Validate plugin implementation."""
        errors = []
        
        # Check required attributes
        if not plugin.name:
            errors.append("Plugin must have a name")
        
        # Check for rule ID conflicts
        for rule_def in plugin.get_rules():
            if '/' in rule_def.rule_id:
                errors.append(f"Rule ID '{rule_def.rule_id}' should not contain '/'")
        
        return errors
```

### 8. Benefits of This Design

1. **Standard Python Packaging**: Uses setuptools entry points, the de facto standard
2. **Easy Installation**: `pip install niti-vajra-plugin`
3. **Version Management**: Plugins can specify Niti version requirements
4. **Isolation**: Plugin failures don't crash the linter
5. **Discoverability**: Can list all installed plugins
6. **Configuration**: Flexible plugin and rule configuration
7. **Namespacing**: Prevents rule ID conflicts

### 9. Implementation Roadmap

1. **Phase 1: Core Infrastructure**
   - Create `niti/plugins/` package
   - Implement `NitiPlugin` ABC and `PluginLoader`
   - Add basic tests

2. **Phase 2: Integration**
   - Update `RuleRegistry` to support plugin rules
   - Modify `LintEngine` to load plugins
   - Update configuration handling

3. **Phase 3: Vajra Plugin**
   - Create separate `niti-vajra-plugin` package
   - Move `IncludeMissingPchRule` from core
   - Add tests and documentation

4. **Phase 4: CLI and Tooling**
   - Add plugin management CLI commands
   - Create plugin template/cookiecutter
   - Write plugin development guide

5. **Phase 5: Advanced Features**
   - Plugin dependency resolution
   - Plugin marketplace/registry
   - Performance optimizations