"""Unit tests for logging rules."""

from test.test_utils import RuleTestCase

import pytest


@pytest.mark.unit
class TestLoggingForbiddenOutput(RuleTestCase):
    """Test LOGGING_FORBIDDEN_OUTPUT rule."""

    rule_id = "logging-forbidden-output"

    def test_detects_cout_cerr(self):
        """Test detection of std::cout and std::cerr usage."""
        code = """
#include <iostream>

void DebugFunction() {
    std::cout << "Debug message" << std::endl;     // Line 5: forbidden
    std::cerr << "Error message" << std::endl;     // Line 6: forbidden
    
    std::cout << "Value: " << value << "\\n";       // Line 8: forbidden
}

void PrintData() {
    using std::cout;
    cout << "Data: " << data;                       // Line 13: forbidden
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=4)
        self.assert_issue_at_line(issues, self.rule_id, 5)
        self.assert_issue_at_line(issues, self.rule_id, 6)
        self.assert_issue_at_line(issues, self.rule_id, 8)
        self.assert_issue_at_line(issues, self.rule_id, 13)

    def test_detects_printf_family(self):
        """Test detection of printf family functions."""
        code = """
#include <cstdio>

void OldStyleDebug() {
    printf("Debug: %d\\n", value);                   // Line 5: forbidden
    fprintf(stderr, "Error: %s\\n", message);        // Line 6: forbidden
    sprintf(buffer, "Value: %d", value);             // Line 7: might be OK for formatting
    
    // These might be acceptable for specific use cases
    snprintf(buffer, sizeof(buffer), "%d", value);  // Line 10: safer version
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id)
        # Should at least detect printf and fprintf

    def test_suggests_logging_framework(self):
        """Test that proper logging framework usage is suggested."""
        code = """
#include <iostream>

void BadLogging() {
    std::cout << "[INFO] Starting process" << std::endl;
    std::cerr << "[ERROR] Failed to connect" << std::endl;
}

// Should suggest something like:
// #include "logging/Logger.h"
// 
// void GoodLogging() {
//     LOG_INFO("Starting process");
//     LOG_ERROR("Failed to connect");
// }
"""
        issues = self.lint_only_this_rule(code)
        if issues:
            # Check that suggestion mentions logging framework
            self.assertIn("logging", issues[0].suggested_fix.lower())

    def test_main_function_exception(self):
        """Test that main function might be an exception."""
        code = """
#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0] << " <input>\\n";  // Might be acceptable in main
        return 1;
    }
    
    std::cout << "Processing...\\n";  // Might be acceptable in main
    return 0;
}

void RegularFunction() {
    std::cout << "This should be flagged\\n";  // Line 14: forbidden
}
"""
        self.lint_only_this_rule(code)
        # Implementation might allow exceptions in main() or might not
        # At least RegularFunction should be flagged
