"""Tests for the Vajra plugin itself."""

import unittest
from typing import Dict, Any

from niti_vajra_plugin.plugin import VajraPlugin
from niti.core.issue import Severity


class TestVajraPlugin(unittest.TestCase):
    """Test cases for the VajraPlugin class."""

    def setUp(self):
        """Set up test fixtures."""
        self.plugin = VajraPlugin()

    def test_plugin_metadata(self):
        """Test plugin metadata properties."""
        self.assertEqual(self.plugin.name, "vajra")
        self.assertEqual(self.plugin.version, "0.1.0")
        self.assertEqual(self.plugin.min_niti_version, "0.1.0")
        self.assertIn("Vajra", self.plugin.description)

    def test_get_rules(self):
        """Test that plugin provides expected rules."""
        rules = self.plugin.get_rules()
        
        # Should have exactly 2 rules
        self.assertEqual(len(rules), 2)
        
        # Check rule IDs
        rule_ids = [rule.id for rule in rules]
        self.assertIn("include-missing-pch", rule_ids)
        self.assertIn("file-include-strategy", rule_ids)
        
        # Check rule properties
        for rule_def in rules:
            self.assertIsNotNone(rule_def.rule_class)
            self.assertIsInstance(rule_def.severity, Severity)
            self.assertIsInstance(rule_def.enabled, bool)

    def test_pch_rule_definition(self):
        """Test PCH rule definition."""
        rules = self.plugin.get_rules()
        pch_rule = next(r for r in rules if r.id == "include-missing-pch")
        
        self.assertEqual(pch_rule.severity, Severity.ERROR)
        self.assertTrue(pch_rule.enabled)
        self.assertEqual(pch_rule.rule_class.__name__, "PrecompiledHeaderRule")

    def test_forward_declaration_rule_definition(self):
        """Test forward declaration rule definition."""
        rules = self.plugin.get_rules()
        fd_rule = next(r for r in rules if r.id == "file-include-strategy")
        
        self.assertEqual(fd_rule.severity, Severity.WARNING)
        self.assertFalse(fd_rule.enabled)  # Disabled by default as it's noisy
        self.assertEqual(fd_rule.rule_class.__name__, "ForwardDeclarationRule")

    def test_configure(self):
        """Test plugin configuration."""
        config = {
            "pch_path": "custom/pch.h",
            "other_option": "value"
        }
        
        # Should not raise any exceptions
        self.plugin.configure(config)
        
        # Configuration should be stored
        self.assertEqual(self.plugin._config, config)

    def test_configure_empty(self):
        """Test plugin with empty configuration."""
        self.plugin.configure({})
        self.assertEqual(self.plugin._config, {})

    def test_configure_none(self):
        """Test plugin with None configuration."""
        self.plugin.configure(None)
        self.assertIsNone(self.plugin._config)

    def test_rules_receive_configuration(self):
        """Test that rules receive plugin configuration."""
        config = {"pch_path": "custom/pch.h"}
        self.plugin.configure(config)
        
        rules = self.plugin.get_rules()
        pch_rule_def = next(r for r in rules if r.id == "include-missing-pch")
        
        # Instantiate the rule with config
        rule_instance = pch_rule_def.rule_class(self.plugin._config)
        
        # Check that the rule received the configuration
        self.assertEqual(rule_instance.pch_path, "custom/pch.h")

    def test_rule_independence(self):
        """Test that rules work independently."""
        rules = self.plugin.get_rules()
        
        # Each rule should be independently instantiable
        for rule_def in rules:
            if rule_def.id == "include-missing-pch":
                instance = rule_def.rule_class({"pch_path": "test.h"})
            else:
                instance = rule_def.rule_class()
            
            # Should have required attributes
            self.assertTrue(hasattr(instance, 'check'))
            self.assertTrue(hasattr(instance, 'id'))
            self.assertTrue(hasattr(instance, 'severity'))


if __name__ == "__main__":
    unittest.main()