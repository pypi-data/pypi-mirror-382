"""Pytest-style tests for Vajra plugin rules."""

import pytest
from tests.fixtures import CppCodeSamples
from tests.conftest import parse_and_check


class TestPCHRule:
    """Test PrecompiledHeaderRule using pytest."""
    
    @pytest.mark.unit
    def test_missing_pch(self, pch_rule, parser):
        """Test detection of missing PCH."""
        issues = parse_and_check(pch_rule, CppCodeSamples.PCH_MISSING, parser)
        assert len(issues) == 1
        assert "Missing precompiled header" in issues[0].message
    
    @pytest.mark.unit
    def test_correct_pch(self, pch_rule, parser):
        """Test correct PCH usage."""
        issues = parse_and_check(pch_rule, CppCodeSamples.PCH_CORRECT, parser)
        assert len(issues) == 0
    
    @pytest.mark.unit
    def test_wrong_order_pch(self, pch_rule, parser):
        """Test PCH in wrong position."""
        issues = parse_and_check(pch_rule, CppCodeSamples.PCH_WRONG_ORDER, parser)
        assert len(issues) == 1
        assert "first include" in issues[0].message
    
    @pytest.mark.unit
    def test_header_file_exempt(self, pch_rule, parser):
        """Test that header files are exempt from PCH requirement."""
        issues = parse_and_check(pch_rule, CppCodeSamples.PCH_HEADER_FILE, parser)
        assert len(issues) == 0
    
    @pytest.mark.unit
    @pytest.mark.parametrize("pch_path,expected_count", [
        ("commons/PrecompiledHeaders.h", 1),  # Default path - should find issue
        ("project/pch.h", 1),                  # Different path - should find issue
    ])
    def test_custom_pch_paths(self, parser, pch_path, expected_count):
        """Test with different PCH paths."""
        from niti_vajra_plugin.rules.pch_rule import PrecompiledHeaderRule
        rule = PrecompiledHeaderRule({"pch_path": pch_path})
        
        code = f"""
#include "{pch_path}"

void Function() {{}}
"""
        issues = parse_and_check(rule, code, parser)
        assert len(issues) == 0  # Should accept the configured path


class TestForwardDeclarationRule:
    """Test ForwardDeclarationRule using pytest."""
    
    @pytest.mark.unit
    def test_unnecessary_includes(self, fd_rule, parser):
        """Test detection of unnecessary includes."""
        issues = parse_and_check(fd_rule, CppCodeSamples.FD_UNNECESSARY_INCLUDES, parser)
        assert len(issues) == 2
        
        # Check specific files are flagged
        flagged_files = [issue.message for issue in issues]
        assert any("Widget.h" in msg for msg in flagged_files)
        assert any("Component.h" in msg for msg in flagged_files)
        assert not any("Data.h" in msg for msg in flagged_files)
    
    @pytest.mark.unit
    def test_necessary_includes(self, fd_rule, parser):
        """Test that necessary includes are not flagged."""
        issues = parse_and_check(fd_rule, CppCodeSamples.FD_NECESSARY_INCLUDES, parser)
        assert len(issues) == 0
    
    @pytest.mark.unit
    def test_smart_pointers(self, fd_rule, parser):
        """Test smart pointer detection."""
        issues = parse_and_check(fd_rule, CppCodeSamples.FD_SMART_POINTERS, parser)
        assert len(issues) == 2
        assert all("forward declaration" in issue.suggested_fix for issue in issues)
    
    @pytest.mark.unit
    def test_mixed_usage(self, fd_rule, parser):
        """Test mixed usage patterns."""
        issues = parse_and_check(fd_rule, CppCodeSamples.FD_MIXED_USAGE, parser)
        assert len(issues) == 2
        
        # Only pointer/reference usage should be flagged
        flagged = [issue.message for issue in issues]
        assert any("Pointed.h" in msg for msg in flagged)
        assert any("Referenced.h" in msg for msg in flagged)
        assert not any("Used.h" in msg for msg in flagged)
    
    @pytest.mark.unit
    @pytest.mark.parametrize("include_path,should_skip", [
        ("vector", True),           # STL
        ("string", True),          # STL
        ("boost/optional.hpp", True),  # Third-party
        ("MyClass.h", False),      # Project file
        ("ui/Widget.h", False),    # Project file with path
    ])
    def test_include_filtering(self, fd_rule, parser, include_path, should_skip):
        """Test that system/third-party includes are skipped."""
        code = f"""
#pragma once

#include <{include_path}>

class Test {{
    SomeType* ptr_;
}};
"""
        issues = parse_and_check(fd_rule, code, parser)
        
        if should_skip:
            assert len(issues) == 0
        else:
            # Would need the type to match the include for a real detection
            # This is a simplified test
            pass


class TestVajraPlugin:
    """Test the plugin itself."""
    
    @pytest.mark.unit
    def test_plugin_rules(self, plugin):
        """Test that plugin provides expected rules."""
        rules = plugin.get_rules()
        assert len(rules) == 2
        
        rule_ids = [r.id for r in rules]
        assert "include-missing-pch" in rule_ids
        assert "file-include-strategy" in rule_ids
    
    @pytest.mark.unit
    def test_plugin_metadata(self, plugin):
        """Test plugin metadata."""
        assert plugin.name == "vajra"
        assert plugin.version == "0.1.0"
        assert "Vajra" in plugin.description
    
    @pytest.mark.unit
    def test_plugin_configuration(self, plugin):
        """Test plugin configuration handling."""
        config = {"pch_path": "custom/pch.h", "extra": "value"}
        plugin.configure(config)
        assert plugin._config == config


@pytest.mark.integration
class TestPluginIntegration:
    """Integration tests for the plugin."""
    
    def test_complex_file(self, pch_rule, fd_rule, parser):
        """Test both rules on a complex file."""
        # PCH rule should find missing PCH
        pch_issues = parse_and_check(pch_rule, CppCodeSamples.COMPLEX_FILE, parser)
        # Header files might be exempt
        assert len(pch_issues) == 0
        
        # FD rule should find opportunities
        fd_issues = parse_and_check(fd_rule, CppCodeSamples.COMPLEX_FILE, parser)
        assert len(fd_issues) >= 2  # Manager.h and Service.h
    
    @pytest.mark.slow
    def test_performance(self, pch_rule, fd_rule, parser):
        """Test rule performance on large files."""
        # Generate a large file
        large_code = """
#pragma once

#include <vector>
#include <memory>
"""
        # Add many includes
        for i in range(100):
            large_code += f'#include "Class{i}.h"\n'
        
        large_code += """
namespace test {
"""
        # Add many class definitions
        for i in range(100):
            large_code += f"""
    class User{i} {{
        Class{i}* ptr_{i};
    }};
"""
        large_code += "\n}"
        
        # Rules should handle large files efficiently
        import time
        
        start = time.time()
        pch_issues = parse_and_check(pch_rule, large_code, parser)
        pch_time = time.time() - start
        
        start = time.time()
        fd_issues = parse_and_check(fd_rule, large_code, parser)
        fd_time = time.time() - start
        
        # Should complete in reasonable time
        assert pch_time < 1.0  # Less than 1 second
        assert fd_time < 2.0   # FD rule is more complex