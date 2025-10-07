"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path so we can import the plugin
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))


@pytest.fixture
def parser():
    """Provide a configured tree-sitter parser."""
    import tree_sitter_cpp as tscpp
    from tree_sitter import Parser
    
    CPP_LANGUAGE = tscpp.language()
    parser = Parser()
    parser.set_language(CPP_LANGUAGE)
    return parser


@pytest.fixture
def pch_rule():
    """Provide a PrecompiledHeaderRule instance."""
    from niti_vajra_plugin.rules.pch_rule import PrecompiledHeaderRule
    config = {"pch_path": "commons/PrecompiledHeaders.h"}
    return PrecompiledHeaderRule(config)


@pytest.fixture
def fd_rule():
    """Provide a ForwardDeclarationRule instance."""
    from niti_vajra_plugin.rules.forward_declaration_rule import ForwardDeclarationRule
    return ForwardDeclarationRule()


@pytest.fixture
def plugin():
    """Provide a VajraPlugin instance."""
    from niti_vajra_plugin.plugin import VajraPlugin
    return VajraPlugin()


def parse_and_check(rule, code, parser):
    """Helper function to parse code and run rule check."""
    tree = parser.parse(code.encode())
    return rule.check(tree.root_node, code.encode())