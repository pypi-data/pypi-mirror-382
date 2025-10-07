"""Unit tests for naming convention rules."""

from test.fixtures.cpp_samples import CppSamples
from test.test_utils import RuleTestCase

import pytest


@pytest.mark.unit
class TestNamingFunctionCase(RuleTestCase):
    """Test NAMING_FUNCTION_CASE rule."""

    rule_id = "naming-function-case"

    def test_detects_snake_case_functions(self):
        """Test detection of snake_case function names."""
        issues = self.lint_only_this_rule(CppSamples.NAMING_FUNCTION_CASE_BAD)
        self.assert_has_rule(issues, self.rule_id, count=3)

    def test_accepts_camel_case_functions(self):
        """Test that CamelCase function names are accepted."""
        issues = self.lint_only_this_rule(CppSamples.NAMING_FUNCTION_CASE_GOOD)
        self.assert_no_issues(issues)

    def test_specific_violations(self):
        """Test specific naming violations."""
        code = """
void process_data() {}     // Line 2: snake_case
void processData() {}      // Line 3: incorrect camelCase (should start uppercase)  
void ProcessData() {}      // Line 4: correct PascalCase
void PROCESS_DATA() {}     // Line 5: all uppercase
void process() {}          // Line 6: all lowercase
"""
        issues = self.lint_only_this_rule(code)
        # Should find violations on lines 2, 3, 5, 6
        self.assert_has_rule(issues, self.rule_id, count=4)
        self.assert_issue_at_line(issues, self.rule_id, 2)
        self.assert_issue_at_line(issues, self.rule_id, 3)
        self.assert_issue_at_line(issues, self.rule_id, 5)
        self.assert_issue_at_line(issues, self.rule_id, 6)


@pytest.mark.unit
class TestNamingVariableCase(RuleTestCase):
    """Test NAMING_VARIABLE_CASE rule."""

    rule_id = "naming-variable-case"

    def test_detects_camel_case_variables(self):
        """Test detection of CamelCase variable names."""
        issues = self.lint_only_this_rule(CppSamples.NAMING_VARIABLE_CASE_BAD)
        self.assert_has_rule(issues, self.rule_id, count=3)

    def test_accepts_snake_case_variables(self):
        """Test that snake_case variable names are accepted."""
        issues = self.lint_only_this_rule(CppSamples.NAMING_VARIABLE_CASE_GOOD)
        self.assert_no_issues(issues)

    def test_specific_violations(self):
        """Test specific variable naming violations."""
        code = """
int userData = 0;          // Line 2: CamelCase
int user_data = 0;         // Line 3: correct snake_case
int USERDATA = 0;          // Line 4: all uppercase (should be for constants)
int userdata = 0;          // Line 5: no separators
"""
        issues = self.lint_only_this_rule(code)
        # Should find violations on lines 2, 4, 5
        self.assert_has_rule(issues, self.rule_id, count=3)
        self.assert_issue_at_line(issues, self.rule_id, 2)
        self.assert_issue_at_line(issues, self.rule_id, 4)
        self.assert_issue_at_line(issues, self.rule_id, 5)


@pytest.mark.unit
class TestNamingClassCase(RuleTestCase):
    """Test NAMING_CLASS_CASE rule."""

    rule_id = "naming-class-case"

    def test_detects_snake_case_classes(self):
        """Test detection of snake_case class names."""
        issues = self.lint_only_this_rule(CppSamples.NAMING_CLASS_CASE_BAD)
        self.assert_has_rule(issues, self.rule_id, count=3)

    def test_accepts_camel_case_classes(self):
        """Test that CamelCase class names are accepted."""
        issues = self.lint_only_this_rule(CppSamples.NAMING_CLASS_CASE_GOOD)
        self.assert_no_issues(issues)

    def test_handles_structs_and_enums(self):
        """Test that structs and enums follow same rules."""
        code = """
struct user_info {};       // Line 2: snake_case struct
struct UserInfo {};        // Line 3: correct CamelCase struct
enum class status_type {}; // Line 4: snake_case enum
enum class StatusType {};  // Line 5: correct CamelCase enum
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=2)
        self.assert_issue_at_line(issues, self.rule_id, 2)
        self.assert_issue_at_line(issues, self.rule_id, 4)


@pytest.mark.unit
class TestNamingMemberCase(RuleTestCase):
    """Test NAMING_MEMBER_CASE rule."""

    rule_id = "naming-member-case"

    def test_detects_missing_trailing_underscore(self):
        """Test detection of member variables without trailing underscore."""
        issues = self.lint_only_this_rule(CppSamples.NAMING_MEMBER_CASE_BAD)
        self.assert_has_rule(issues, self.rule_id, count=3)

    def test_accepts_proper_member_naming(self):
        """Test that properly named members are accepted."""
        issues = self.lint_only_this_rule(CppSamples.NAMING_MEMBER_CASE_GOOD)
        self.assert_no_issues(issues)

    def test_hungarian_notation_detection(self):
        """Test detection of Hungarian notation."""
        code = """
class Example {
private:
    int m_count;           // Line 4: Hungarian notation
    std::string m_name;    // Line 5: Hungarian notation
    int count_;            // Line 6: correct
    int p_pointer;         // Line 7: Hungarian notation
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)


@pytest.mark.unit
class TestNamingConstantCase(RuleTestCase):
    """Test NAMING_CONSTANT_CASE rule."""

    rule_id = "naming-constant-case"

    def test_detects_incorrect_constant_naming(self):
        """Test detection of incorrectly named constants."""
        code = """
const int MAX_VALUE = 100;      // Line 2: UPPER_CASE (wrong)
const int max_value = 100;      // Line 3: snake_case (wrong)
const int kMaxValue = 100;      // Line 4: kCamelCase (correct)
constexpr int MIN_VALUE = 0;    // Line 5: UPPER_CASE (wrong) 
constexpr int kMinValue = 0;    // Line 6: kCamelCase (correct)
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)
        self.assert_issue_at_line(issues, self.rule_id, 2)
        self.assert_issue_at_line(issues, self.rule_id, 3)
        self.assert_issue_at_line(issues, self.rule_id, 5)

    def test_static_const_members(self):
        """Test static const member naming."""
        code = """
class Config {
    static const int MAX_SIZE = 100;     // Line 3: wrong
    static const int kMaxSize = 100;     // Line 4: correct
    static constexpr int MIN_SIZE = 10;  // Line 5: wrong
    static constexpr int kMinSize = 10;  // Line 6: correct
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=2)


@pytest.mark.unit
class TestNamingEnumCase(RuleTestCase):
    """Test NAMING_ENUM_CASE and NAMING_ENUM_VALUE_CASE rules."""

    def test_enum_class_naming(self):
        """Test enum class naming conventions."""
        code = """
enum class status_type {     // Line 2: snake_case (wrong)
    Running,
    Stopped
};

enum class StatusType {      // Line 7: PascalCase (correct)
    Running,
    Stopped  
};

enum class kStatusType {     // Line 12: kPascalCase (incorrect should be PascalCase)
    Running,
    Stopped
};
"""
        issues = self.lint_content(code, enable_rules=["naming-enum-case"])
        self.assert_has_rule(issues, "naming-enum-case", count=2)
        self.assert_issue_at_line(issues, "naming-enum-case", 2)
        self.assert_issue_at_line(issues, "naming-enum-case", 12)

    def test_enum_value_naming(self):
        """Test enum value naming conventions."""
        code = """
enum class Status {
    running,        // Line 3: lowercase (wrong for enum class)
    STOPPED,        // Line 4: UPPER_CASE (wrong for enum class)
    Running,        // Line 5: PascalCase (wrong for enum class - should be kPascalCase)
    Stopped,        // Line 6: PascalCase (wrong for enum class - should be kPascalCase)
    kRunning,       // Line 7: kPascalCase (correct for enum class)
    kStopped        // Line 8: kPascalCase (correct for enum class)
};

enum OldStyle {
    VALUE_ONE,      // Line 12: UPPER_CASE (correct for C-style)
    value_two,      // Line 13: lowercase (wrong for C-style)
    ValueThree      // Line 14: PascalCase (wrong for C-style)
};
"""
        issues = self.lint_content(
            code, enable_rules=["naming-enum-value-case"]
        )
        self.assert_has_rule(issues, "naming-enum-value-case", count=6)


@pytest.mark.unit
class TestNamingHungarianNotation(RuleTestCase):
    """Test NAMING_HUNGARIAN_NOTATION rule."""

    rule_id = "naming-hungarian-notation"

    def test_detects_hungarian_notation(self):
        """Test detection of Hungarian notation."""
        code = """
int nCount = 0;            // Line 2: 'n' prefix for int
std::string strName = "";  // Line 3: 'str' prefix for string
bool bEnabled = true;      // Line 4: 'b' prefix for bool
float fValue = 1.0f;       // Line 5: 'f' prefix for float
int* pPointer = nullptr;   // Line 6: 'p' prefix for pointer

// These should be fine
int count = 0;
std::string name = "";
bool enabled = true;
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=5)

    def test_member_variable_hungarian(self):
        """Test Hungarian notation in member variables."""
        code = """
class Widget {
private:
    int m_nCount;          // Line 4: both 'm_' and 'n' prefixes
    std::string m_strName; // Line 5: both 'm_' and 'str' prefixes
    bool m_bActive;        // Line 6: both 'm_' and 'b' prefixes
    
    // Correct member variables
    int count_;
    std::string name_;
    bool active_;
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)
