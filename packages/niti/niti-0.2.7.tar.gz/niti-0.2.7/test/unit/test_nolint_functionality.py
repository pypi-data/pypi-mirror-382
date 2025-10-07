"""Tests for NOLINT comment functionality."""

import pytest
from test.test_utils import NitiTestCase

from niti.rules.rule_id import RuleId


@pytest.mark.unit
class TestNolintFunctionality(NitiTestCase):
    """Test cases for NOLINT comment functionality."""

    def test_nolint_disables_all_rules_on_line(self):
        """Test that NOLINT disables all rules on the same line."""
        content = """
int main() {
    int value = 42;  // NOLINT
    int other = 10;
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Should only have one issue (line 4), line 3 should be skipped
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 4)
        self.assertEqual(issues[0].rule_id, "type-forbidden-int")

    def test_nolint_rule_specific_disabling(self):
        """Test that NOLINT with specific rule only disables that rule."""
        content = """
int main() {
    int value = 42;  // NOLINT type-forbidden-int
    int other = 10;  // NOLINT some-other-rule
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Line 3 should be skipped (matches our rule), line 4 should trigger
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 4)
        self.assertEqual(issues[0].rule_id, "type-forbidden-int")

    def test_nolint_multiple_rules_comma_separated(self):
        """Test that NOLINT with multiple comma-separated rules works."""
        content = """
int main() {
    int value = 42;  // NOLINT type-forbidden-int,naming-variable-case
    int other = 10;  // NOLINT naming-variable-case,some-other-rule
    int third = 20;  // NOLINT some-other-rule
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Line 3 should be skipped (type-forbidden-int in NOLINT list)
        # Line 4 should trigger (type-forbidden-int NOT in NOLINT list)  
        # Line 5 should trigger (type-forbidden-int NOT in NOLINT list)
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0].line_number, 4)
        self.assertEqual(issues[1].line_number, 5)

    def test_nolintnextline_disables_next_line(self):
        """Test that NOLINTNEXTLINE disables rules on the following line."""
        content = """
int main() {
    // NOLINTNEXTLINE
    int value = 42;
    int other = 10;
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Line 4 should be skipped, line 5 should trigger
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 5)

    def test_nolintnextline_rule_specific_disabling(self):
        """Test that NOLINTNEXTLINE with specific rule only disables that rule."""
        content = """
int main() {
    // NOLINTNEXTLINE type-forbidden-int
    int value = 42;
    // NOLINTNEXTLINE some-other-rule  
    int other = 10;
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Line 4 should be skipped (matches our rule), line 6 should trigger
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 6)

    def test_nolint_case_sensitivity(self):
        """Test that NOLINT comments are case sensitive."""
        content = """
int main() {
    int value = 42;  // nolint (lowercase)
    int other = 10;  // NOLINT (uppercase)
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Only uppercase NOLINT should work, lowercase should not
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 3)

    def test_nolint_multiple_on_same_line(self):
        """Test multiple NOLINT patterns on same line."""
        content = """
int main() {
    int value = 42;  // NOLINT // Another comment
    int other = 10;  // Some comment // NOLINT
}
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # Both lines should be skipped due to NOLINT
        self.assertEqual(len(issues), 0)

    def test_nolint_mixed_with_multiple_rules(self):
        """Test NOLINT functionality with multiple different rules enabled."""
        content = """
int main() {
    int badValue = 42;                    // Should trigger both rules
    int badOther = 10;  // NOLINT         // Should trigger no rules
    int badThird = 20;  // NOLINT type-forbidden-int  // Should trigger naming only
    // NOLINTNEXTLINE type-forbidden-int
    int badFourth = 30;                   // Should trigger naming only
    // NOLINTNEXTLINE
    int badFifth = 40;                    // Should trigger no rules
}
"""
        # Enable both type and naming rules to test interaction
        issues = self.lint_content(
            content, 
            enable_rules=["type-forbidden-int", "naming-variable-case"]
        )
        
        # Expect issues on:
        # Line 3: both type-forbidden-int and naming-variable-case
        # Line 5: naming-variable-case only (type disabled by NOLINT)
        # Line 7: naming-variable-case only (type disabled by NOLINTNEXTLINE)
        
        self.assertEqual(len(issues), 4)  # 2 + 1 + 1 = 4 total issues
        
        # Check line 3 has both rule violations
        line_3_issues = [i for i in issues if i.line_number == 3]
        self.assertEqual(len(line_3_issues), 2)
        
        # Check line 5 has only naming violation
        line_5_issues = [i for i in issues if i.line_number == 5]
        self.assertEqual(len(line_5_issues), 1)
        self.assertEqual(line_5_issues[0].rule_id, "naming-variable-case")
        
        # Check line 7 has only naming violation
        line_7_issues = [i for i in issues if i.line_number == 7]
        self.assertEqual(len(line_7_issues), 1)
        self.assertEqual(line_7_issues[0].rule_id, "naming-variable-case")

    def test_nolintnextline_edge_cases(self):
        """Test NOLINTNEXTLINE edge cases."""
        content = """// NOLINTNEXTLINE
int value = 42;
int other = 10;
"""
        issues = self.lint_content(content, enable_rules=["type-forbidden-int"])
        
        # First line should be skipped, second should trigger
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].line_number, 3)

    def test_nolint_in_realistic_code(self):
        """Test NOLINT in realistic C++ code scenarios."""
        content = """
#include <iostream>
#include <memory>

// Legacy code - needs raw pointers for C API
class LegacyInterface {
public:
    // NOLINTNEXTLINE type-forbidden-int
    int* GetRawPointer() {
        return raw_data_;  // NOLINT type-forbidden-int
    }
    
    void ProcessData(int* data) {  // NOLINT type-forbidden-int
        // Processing logic here
        int temp = *data;  // NOLINT type-forbidden-int
    }

private:
    int* raw_data_ = nullptr;  // NOLINT type-forbidden-int
};
"""
        issues = self.lint_content(
            content, 
            enable_rules=[
                "type-forbidden-int"
            ]
        )
        
        # All int* violations should be suppressed by NOLINT comments
        violation_lines = [i.line_number for i in issues]
        
        # Verify that the NOLINT suppressions worked
        self.assertNotIn(9, violation_lines)   # NOLINTNEXTLINE should suppress line 9
        self.assertNotIn(10, violation_lines)  # NOLINT should suppress line 10 
        self.assertNotIn(13, violation_lines)  # NOLINT should suppress line 13
        self.assertNotIn(15, violation_lines)  # NOLINT should suppress line 15
        self.assertNotIn(19, violation_lines)  # NOLINT should suppress line 19
        
        # Should have no violations at all
        self.assertEqual(len(issues), 0)

    def test_safety_range_loop_nolint_multiline(self):
        """Test NOLINT functionality with safety-range-loop-missing rule in multi-line for loops."""
        content = """#include <vector>
#include <iostream>

void processVector() {
    std::vector<int> data = {1, 2, 3, 4, 5};
    
    // This traditional loop should trigger the safety rule  
    for (int i = 0; i < data.size(); ++i) {  // Line 8
        std::cout << data[i] << std::endl;
    }
    
    // NOLINTNEXTLINE safety-range-loop-missing
    for (int i = 0;   // Line 13 - should be suppressed
         i < data.size(); 
         ++i) {
        std::cout << data[i] << std::endl;  
    }
    
    // Multi-line loop with NOLINT on the opening line
    for (int i = 0; i < data.size(); ++i) {  // NOLINT safety-range-loop-missing - Line 20
        std::cout << data[i] << std::endl;
    }
    
    // Multi-line loop without suppression should trigger
    for (size_t j = 0;   // Line 25 - should trigger
         j < data.size(); 
         j++) {
        data[j] *= 2;
    }
}"""
        issues = self.lint_content(content, enable_rules=["safety-range-loop-missing"])
        
        # Debug: Print actual issue lines for troubleshooting
        issue_lines = [issue.line_number for issue in issues]
        print(f"DEBUG: Found issues on lines: {issue_lines}")
        
        # Should have 2 violations:
        # Line 8: Traditional loop (not suppressed)
        # Line 25: Multi-line loop (not suppressed)
        # Lines 13 and 20 should be suppressed by NOLINT comments
        self.assertEqual(len(issues), 2)
        
        self.assertIn(8, issue_lines)   # First loop should trigger
        self.assertIn(25, issue_lines)  # Last loop should trigger
        self.assertNotIn(13, issue_lines)  # NOLINTNEXTLINE should suppress
        self.assertNotIn(20, issue_lines)  # NOLINT should suppress

    def test_include_order_nolint_alphabetical_suppression(self):
        """Test NOLINT suppression of alphabetical ordering violations within include groups."""
        content = """#include <iostream>
#include <vector>

#include "core/base/Logger.h"    // NOLINT include-order-wrong
#include "network/service/Processor.h"
// NOLINTNEXTLINE include-order-wrong
#include "core/database/Connection.h"  
#include "tooling/utils/Helper.h"    // should trigger
#include "platform/core/Manager.h"  
"""
        issues = self.lint_content(content, enable_rules=["include-order-wrong"])
        
        issue_lines = [issue.line_number for issue in issues]
        
        # Expected behavior:
        # Line 4: core/base/Logger.h should be SUPPRESSED by NOLINT comment
        # Line 7: core/database/Connection.h should be SUPPRESSED by NOLINTNEXTLINE comment  
        # Line 8: tooling/utils/Helper.h should TRIGGER (no NOLINT protection)
        
        self.assertNotIn(4, issue_lines)    # NOLINT should suppress  
        self.assertNotIn(7, issue_lines)    # NOLINTNEXTLINE should suppress
        self.assertIn(8, issue_lines)       # Should trigger (no NOLINT protection)


if __name__ == "__main__":
    import unittest
    unittest.main()