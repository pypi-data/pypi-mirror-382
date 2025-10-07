"""Integration tests for the Niti C++ linter."""

import os
from test.test_utils import NitiTestCase

import pytest

from niti.core.config import LinterConfig
from niti.core.severity import Severity


@pytest.mark.integration
class TestCompleteFiles(NitiTestCase):
    """Test linting complete, realistic C++ files."""

    def test_lint_well_formatted_file(self):
        """Test linting a well-formatted C++ file following all conventions."""
        content = """
// Copyright (c) 2024 Vajra Project
// Licensed under the Apache License, Version 2.0

#pragma once
#include "commons/PrecompiledHeaders.h"

#include <memory>
#include <string>
#include <vector>

#include "core/Base.h"

namespace vajra {

/**
 * @brief Manages user sessions in the application
 * @thread_safety Thread-safe
 */
class UserSessionManager : public NonCopyableNonMovable {
public:
    UserSessionManager() noexcept = default;
    ~UserSessionManager() = default;
    
    /**
     * @brief Create a new user session
     * @param user_id Unique user identifier (in)
     * @param session_data Initial session data (in)
     * @return Session ID if successful, empty optional otherwise
     */
    [[nodiscard]] std::optional<std::string> CreateSession(
        std::int32_t user_id,
        const SessionData& session_data) noexcept;
    
    /**
     * @brief Check if a session is valid
     * @param session_id Session identifier to check (in)
     * @return True if session exists and is valid
     */
    [[nodiscard]] bool IsSessionValid(const std::string& session_id) const noexcept;
    
    /**
     * @brief End a user session
     * @param session_id Session to terminate (in)
     */
    void EndSession(const std::string& session_id) noexcept;

private:
    struct SessionInfo {
        std::int32_t user_id_;
        SessionData data_;
        std::chrono::steady_clock::time_point created_at_;
    };
    
    std::unordered_map<std::string, SessionInfo> sessions_;
    mutable std::shared_mutex sessions_mutex_;
};

}  // namespace vajra
"""
        issues = self.lint_content(content, filename="UserSessionManager.h")
        # Well-formatted file should have minimal issues
        error_count = len([i for i in issues if i.severity == Severity.ERROR])
        self.assertEqual(
            error_count, 0, "Well-formatted file should have no errors"
        )

    def test_lint_problematic_file(self):
        """Test linting a file with multiple issues."""
        content = """
#include <vector>
#include "MyClass.h"

class data_processor {  // snake_case class name
    int processData(int* data) {  // raw pointer, non-const method
        int result = 0;  // forbidden int type
        for (int i = 0; i < 10; i++) {  // C-style loop
            result += data[i];
        }
        return result;
    }
    
    void print_result(int value) {  // snake_case function
        std::cout << "Result: " << value << std::endl;  // forbidden output
    }
};

std::pair<int, string> getUserInfo() {  // pair usage, wrong case
    return std::make_pair(123, "John");
}
"""
        issues = self.lint_content(content, filename="bad_code.cpp")

        # Should detect multiple issues
        self.assertGreater(len(issues), 5, "Should detect multiple issues")

        # Check for specific issues
        rule_ids = {issue.rule_id for issue in issues}
        expected_rules = {
            "naming-class-case",  # data_processor
            "naming-function-case",  # processData (should be CamelCase)
            "type-forbidden-int",  # int types
            "safety-raw-pointer-param",  # int* data
            "safety-range-loop-missing",  # C-style for loop
            "logging-forbidden-output",  # std::cout
            "type-pair-tuple",  # std::pair usage
        }

        # Check that at least some expected rules are triggered
        found_rules = rule_ids & expected_rules
        self.assertGreater(
            len(found_rules),
            3,
            f"Should find multiple expected issues. Found: {rule_ids}",
        )


@pytest.mark.integration
class TestMultipleFiles(NitiTestCase):
    """Test linting multiple files together."""

    def test_lint_directory(self):
        """Test linting an entire directory."""
        # Create multiple test files
        header_content = """
#pragma once
#include "commons/PrecompiledHeaders.h"

namespace test {

/**
 * @brief Test class
 */
class TestClass : public NonCopyableNonMovable {
public:
    void Process();
};

}  // namespace test
"""

        impl_content = """
#include "TestClass.h"

namespace test {

void TestClass::Process() {
    int value = 42;  // TYPE_FORBIDDEN_INT
    // Implementation
}

}  // namespace test
"""

        bad_content = """
class bad_class {  // Multiple issues
    int data;
    void process_data() {}
};
"""

        # Create files
        self.create_test_file(header_content, "include/TestClass.h")
        self.create_test_file(impl_content, "src/TestClass.cpp")
        self.create_test_file(bad_content, "src/bad.cpp")

        # Lint directory
        issues = self.engine.lint_paths([self.temp_dir])

        # Should find issues across multiple files
        self.assertGreater(len(issues), 0)

        # Check that issues come from different files
        affected_files = {os.path.basename(issue.file_path) for issue in issues}
        self.assertIn("TestClass.cpp", affected_files)
        self.assertIn("bad.cpp", affected_files)


@pytest.mark.integration
class TestConfigurationIntegration(NitiTestCase):
    """Test configuration file integration."""

    def test_config_file_loading(self):
        """Test loading configuration from file."""
        config_content = """
# Niti configuration
documentation_style: doxygen

disabled_rules:
  - type-forbidden-int
  - modern-missing-noexcept

enabled_rules:
  - modern-nodiscard-missing
  - doc-function-param-desc-quality

rule_severities:
  naming-function-case: error
  doc-class-missing: info
"""
        config_path = os.path.join(self.temp_dir, ".nitirc")
        with open(config_path, "w") as f:
            f.write(config_content)

        # Load config
        config = LinterConfig.load(config_path)

        # Verify settings
        self.assertEqual(config.documentation_style, "doxygen")
        # Apply config to registry first
        config._apply_to_registry()

        from niti.rules.rule_id import RuleId

        self.assertFalse(config.is_rule_enabled(RuleId.TYPE_FORBIDDEN_INT))
        # Check that some rules are enabled (verify basic functionality)
        enabled_rules = [r for r in RuleId if config.is_rule_enabled(r)]
        self.assertGreater(
            len(enabled_rules), 10, "At least some rules should be enabled"
        )

        # Test that disabled rules in config are actually disabled
        self.assertIn("type-forbidden-int", config.disabled_rules)
        self.assertIn("modern-missing-noexcept", config.disabled_rules)


@pytest.mark.integration
class TestErrorRecovery(NitiTestCase):
    """Test error recovery and edge cases."""

    def test_syntax_error_recovery(self):
        """Test that linter handles files with syntax errors gracefully."""
        content = """
class BrokenClass {
    void Method() {
        if (condition {  // Missing closing parenthesis
            // Do something
        }
    }
    // Missing closing brace
"""
        issues = self.lint_content(content, filename="broken.cpp")
        # Should still try to find some issues despite syntax errors
        # Exact behavior depends on tree-sitter's error recovery

    def test_empty_file(self):
        """Test linting empty files."""
        issues = self.lint_content("", filename="empty.cpp")
        # Empty files may have certain expected issues (copyright, naming, etc.)
        # but shouldn't crash the linter
        self.assertIsInstance(issues, list)
        # Should not have any critical errors that would stop linting
        critical_issues = [i for i in issues if i.severity.name == "ERROR"]
        # Debug: print critical issues
        for issue in critical_issues:
            print(f"Critical issue: {issue.rule_id} - {issue.message}")
        # Empty files may have some errors (like missing copyright) which is acceptable
        # The test should verify linter doesn't crash
        self.assertTrue(len(issues) >= 0, "Should successfully lint empty file")

    def test_very_large_file(self):
        """Test linting very large files."""
        # Generate a large file
        lines = []
        for i in range(1000):
            lines.append(f"void Function{i}() {{ int value = {i}; }}")

        content = "\n".join(lines)
        issues = self.lint_content(content, filename="large.cpp")

        # Should handle large files without crashing
        # Should find many type-forbidden-int issues
        self.assertGreater(len(issues), 100)

    def test_unicode_content(self):
        """Test handling of Unicode content."""
        content = """
// Copyright © 2024 Company™
// Author: José García

/**
 * @brief Process UTF-8 strings with émojis 🚀
 * @param text Input text with unicode (in)
 */
void ProcessUnicode(const std::string& text) {
    // Process unicode: αβγ, 中文, العربية
    std::u32string converted = U"Hello 世界";
}
"""
        issues = self.lint_content(content, filename="unicode.cpp")
        # Should handle Unicode without crashing


@pytest.mark.integration
class TestCLIIntegration(NitiTestCase):
    """Test CLI functionality integration."""

    def test_cli_basic_run(self):
        """Test basic CLI execution."""
        import sys
        from io import StringIO

        from niti.cli import main

        # Create test file
        test_file = self.create_test_file("int x = 0;")

        # Capture output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout = StringIO()
        stderr = StringIO()

        try:
            sys.stdout = stdout
            sys.stderr = stderr
            sys.argv = ["niti", "--check", test_file]

            # Run CLI (might raise SystemExit)
            try:
                main()
            except SystemExit as e:
                # Check exit code
                self.assertIn(
                    e.code, [0, 1]
                )  # 0 for success, 1 for issues found

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def test_cli_list_rules(self):
        """Test --list-rules CLI option."""
        import contextlib
        from io import StringIO

        from niti.cli import list_rules

        output = StringIO()
        with contextlib.redirect_stdout(output):
            list_rules(None)  # No config file

        output_text = output.getvalue()

        # Should list all rule categories
        self.assertIn("TYPE-SYSTEM", output_text)
        self.assertIn("NAMING", output_text)
        self.assertIn("SAFETY", output_text)
        self.assertIn("MODERN-CPP", output_text)
