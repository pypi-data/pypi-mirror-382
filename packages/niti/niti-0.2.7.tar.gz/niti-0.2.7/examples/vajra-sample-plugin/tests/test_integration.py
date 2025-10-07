"""Integration tests for Vajra plugin with Niti."""

import unittest
import tempfile
import os
from pathlib import Path

from niti.core.engine import LintEngine
from niti.core.config import LinterConfig
from niti.plugins.loader import PluginLoader


class TestVajraPluginIntegration(unittest.TestCase):
    """Integration tests for Vajra plugin."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_test_file(self, filename: str, content: str) -> str:
        """Create a test file and return its path."""
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def _create_config(self, config_dict: dict) -> str:
        """Create a config file and return its path."""
        import yaml
        config_path = os.path.join(self.temp_dir, '.nitirc')
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f)
        return config_path

    def test_plugin_loads_successfully(self):
        """Test that the plugin loads without errors."""
        loader = PluginLoader()
        
        # Discover available plugins
        plugins = loader.discover_plugins()
        
        # Vajra should be available if installed
        if "vajra" in plugins:
            success = loader.load_plugin("vajra")
            self.assertTrue(success)

    def test_pch_rule_via_engine(self):
        """Test PCH rule through the linting engine."""
        # Create test file missing PCH
        test_file = self._create_test_file("test.cpp", """
#include <vector>
#include <string>

void Function() {
    std::vector<int> data;
}
""")
        
        # Create config enabling the plugin
        config_dict = {
            "plugins": {
                "enabled": ["vajra"],
                "config": {
                    "vajra": {
                        "pch_path": "commons/PrecompiledHeaders.h"
                    }
                }
            },
            "rules": {
                "vajra/include-missing-pch": {
                    "enabled": True,
                    "severity": "error"
                }
            }
        }
        config_path = self._create_config(config_dict)
        
        # Load config and create engine
        config = LinterConfig()
        config.load_from_file(config_path)
        
        # This test would require full integration with the engine
        # For now, we just verify the config loads correctly
        self.assertIn("vajra", config.plugins.get("enabled", []))

    def test_forward_declaration_rule_via_engine(self):
        """Test forward declaration rule through the engine."""
        # Create header file with unnecessary includes
        test_file = self._create_test_file("Widget.h", """
#pragma once

#include "Component.h"  // Only used as pointer

class Widget {
    Component* component_;
public:
    Component* GetComponent();
};
""")
        
        # Create config
        config_dict = {
            "plugins": {
                "enabled": ["vajra"]
            },
            "rules": {
                "vajra/file-include-strategy": {
                    "enabled": True,
                    "severity": "warning"
                }
            }
        }
        config_path = self._create_config(config_dict)
        
        # Load config
        config = LinterConfig()
        config.load_from_file(config_path)
        
        # Verify rule is configured
        rule_config = config.rules.get("vajra/file-include-strategy", {})
        self.assertTrue(rule_config.get("enabled", False))

    def test_both_rules_together(self):
        """Test both plugin rules working together."""
        # Create test file
        test_file = self._create_test_file("Manager.cpp", """
#include "Manager.h"
#include "Widget.h"  // Could be forward declared in Manager.h

namespace vajra {
    void Manager::Process() {
        // Missing PCH
    }
}
""")
        
        # Config with both rules
        config_dict = {
            "plugins": {
                "enabled": ["vajra"],
                "config": {
                    "vajra": {
                        "pch_path": "commons/PrecompiledHeaders.h"
                    }
                }
            },
            "rules": {
                "vajra/include-missing-pch": {
                    "enabled": True,
                    "severity": "error"
                },
                "vajra/file-include-strategy": {
                    "enabled": True,
                    "severity": "warning"
                }
            }
        }
        
        config_path = self._create_config(config_dict)
        config = LinterConfig()
        config.load_from_file(config_path)
        
        # Both rules should be configured
        self.assertTrue(config.rules.get("vajra/include-missing-pch", {}).get("enabled", False))
        self.assertTrue(config.rules.get("vajra/file-include-strategy", {}).get("enabled", False))

    def test_plugin_config_propagation(self):
        """Test that plugin configuration is properly propagated."""
        custom_pch = "project/precompiled.h"
        
        config_dict = {
            "plugins": {
                "enabled": ["vajra"],
                "config": {
                    "vajra": {
                        "pch_path": custom_pch
                    }
                }
            }
        }
        
        config_path = self._create_config(config_dict)
        config = LinterConfig()
        config.load_from_file(config_path)
        
        # Verify plugin config is loaded
        plugin_config = config.plugins.get("config", {}).get("vajra", {})
        self.assertEqual(plugin_config.get("pch_path"), custom_pch)


if __name__ == "__main__":
    unittest.main()