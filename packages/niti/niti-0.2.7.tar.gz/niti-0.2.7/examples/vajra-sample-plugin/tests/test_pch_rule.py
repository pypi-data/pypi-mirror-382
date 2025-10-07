"""Tests for the PrecompiledHeaderRule."""

import unittest
from typing import List
import tree_sitter_cpp as tscpp
from tree_sitter import Parser

from niti_vajra_plugin.rules.pch_rule import PrecompiledHeaderRule
from niti.core.issue import Issue


class TestPrecompiledHeaderRule(unittest.TestCase):
    """Test cases for PrecompiledHeaderRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {"pch_path": "commons/PrecompiledHeaders.h"}
        self.rule = PrecompiledHeaderRule(self.config)
        
        # Initialize tree-sitter parser
        CPP_LANGUAGE = tscpp.language()
        self.parser = Parser()
        self.parser.set_language(CPP_LANGUAGE)

    def _get_issues(self, code: str) -> List[Issue]:
        """Helper to parse code and get issues."""
        tree = self.parser.parse(code.encode())
        return self.rule.check(tree.root_node, code.encode())

    def test_detects_missing_pch(self):
        """Test detection of missing precompiled header."""
        code = """
#include <vector>
#include <string>
#include "MyClass.h"

namespace vajra {
    void ProcessData() {
        // Implementation
    }
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 1)
        self.assertIn("Missing precompiled header", issues[0].message)
        self.assertIn("commons/PrecompiledHeaders.h", issues[0].message)

    def test_accepts_with_pch_first(self):
        """Test that files with PCH as first include are accepted."""
        code = """
#include "commons/PrecompiledHeaders.h"

#include <vector>
#include <string>
#include "MyClass.h"

namespace vajra {
    void ProcessData() {
        // Implementation
    }
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 0)

    def test_pch_must_be_first_include(self):
        """Test that PCH must be the first include."""
        code = """
#include <vector>
#include "commons/PrecompiledHeaders.h"  // Not first
#include <string>

namespace vajra {
    void ProcessData() {
        // Implementation
    }
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 1)
        self.assertIn("should be the first include", issues[0].message)

    def test_header_guards_before_pch(self):
        """Test that header guards are allowed before PCH."""
        code = """
#pragma once
#include "commons/PrecompiledHeaders.h"

#include <vector>

namespace vajra {
    class Widget {
        // Class definition
    };
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 0)

    def test_comments_before_pch(self):
        """Test that comments are allowed before PCH."""
        code = """
// Copyright (C) 2024 Company
// Licensed under MIT License

#include "commons/PrecompiledHeaders.h"

#include <vector>

namespace vajra {
    void Function() {}
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 0)

    def test_header_files_exempt(self):
        """Test that header files don't require PCH."""
        # Simulate a header file by not having implementation
        code = """
#pragma once

#include <vector>
#include <string>

namespace vajra {
    class Widget {
        std::vector<std::string> data_;
    };
}
"""
        issues = self._get_issues(code)
        # Should not require PCH in header-only code
        self.assertEqual(len(issues), 0)

    def test_custom_pch_path(self):
        """Test with custom PCH path configuration."""
        custom_config = {"pch_path": "project/pch.h"}
        rule = PrecompiledHeaderRule(custom_config)
        
        code = """
#include "project/pch.h"

void Function() {
    // Implementation
}
"""
        tree = self.parser.parse(code.encode())
        issues = rule.check(tree.root_node, code.encode())
        self.assertEqual(len(issues), 0)

    def test_no_includes_file(self):
        """Test file with no includes at all."""
        code = """
namespace vajra {
    inline constexpr int kValue = 42;
}
"""
        issues = self._get_issues(code)
        # Files with no includes but with actual code might still need PCH
        self.assertEqual(len(issues), 1)
        self.assertIn("Missing precompiled header", issues[0].message)

    def test_main_function_requires_pch(self):
        """Test that files with main function require PCH."""
        code = """
#include <iostream>

int main(int argc, char* argv[]) {
    std::cout << "Hello World\\n";
    return 0;
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 1)
        self.assertIn("Missing precompiled header", issues[0].message)


if __name__ == "__main__":
    unittest.main()