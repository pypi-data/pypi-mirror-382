"""Unit tests for type system rules."""

from test.fixtures.cpp_samples import CppSamples
from test.test_utils import RuleTestCase

import pytest


@pytest.mark.unit
class TestTypeForbiddenInt(RuleTestCase):
    """Test TYPE_FORBIDDEN_INT rule."""

    rule_id = "type-forbidden-int"

    def test_detects_primitive_int_types(self):
        """Test detection of primitive int types."""
        issues = self.lint_only_this_rule(CppSamples.TYPE_FORBIDDEN_INT_BAD)
        # Should detect: int, unsigned int, long, short, unsigned long
        self.assert_has_rule(
            issues, self.rule_id, count=7
        )  # 5 declarations + 2 in function

    def test_accepts_fixed_width_types(self):
        """Test that fixed-width integer types are accepted."""
        issues = self.lint_only_this_rule(CppSamples.TYPE_FORBIDDEN_INT_GOOD)
        self.assert_no_issues(issues)

    def test_specific_contexts(self):
        """Test specific contexts where int might be detected."""
        code = """
// Function parameters
void Func1(int param);                    // Line 3: forbidden
void Func2(std::int32_t param);          // OK

// Return types  
int GetValue();                           // Line 7: forbidden
std::int32_t GetCorrectValue();          // OK

// Local variables
void Process() {
    int local = 0;                        // Line 12: forbidden
    unsigned int flags = 0;               // Line 13: forbidden
    std::uint32_t good_flags = 0;        // OK
}

// Class members
class Widget {
    int member_;                          // Line 19: forbidden
    std::int32_t good_member_;           // OK
};

// Template parameters are OK
template<int N>
class Array {};

#define ll long long // Line 28: forbidden
#define ull uint_64_t // Line 29: Allowed

// main function is exception
int main(int argc, char* argv[]) {       // OK - main is special
    return 0;
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=6)
        self.assert_issue_at_line(issues, self.rule_id, 3)
        self.assert_issue_at_line(issues, self.rule_id, 7)
        self.assert_issue_at_line(issues, self.rule_id, 12)
        self.assert_issue_at_line(issues, self.rule_id, 13)
        self.assert_issue_at_line(issues, self.rule_id, 19)
        self.assert_issue_at_line(issues, self.rule_id, 27)

    def test_typedef_and_using(self):
        """Test detection in typedef and using declarations."""
        code = """
typedef int MyInt;                        // Line 2: forbidden
using MyInt2 = int;                       // Line 3: forbidden

typedef std::int32_t MyInt32;            // OK
using MyInt32_2 = std::int32_t;          // OK

// In structs
struct Config {
    typedef unsigned int Flags;           // Line 10: forbidden
    using Count = int;                    // Line 11: forbidden
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=4)

    def test_ignores_types_in_single_line_comments(self):
        """Test that types in single-line comments are ignored."""
        code = """
// This is a comment mentioning int and long types
// Another comment with short and unsigned int
std::int32_t valid_var = 0;              // OK - not in comment
// int main() is a special case
"""
        issues = self.lint_only_this_rule(code)
        # Should have no issues since all 'int', 'long', 'short' are in comments
        self.assert_no_issues(issues)

    def test_ignores_types_in_multiline_comments(self):
        """Test that types in multi-line comments are ignored."""
        code = """
/*
 * This is a multi-line comment that mentions int, long, and short types.
 * We split sessions into different categories:
 * - long sessions with many tokens
 * - short sessions with few tokens
 * The int type should not be flagged here.
 */
std::int32_t valid_var = 0;              // OK

/**
 * @brief Another Doxygen comment mentioning int
 * @param value An int value (mentioned in comment)
 * @return A long value (also in comment)
 */
[[nodiscard]] std::int64_t GetValue(std::int32_t value);  // OK

int actual_problem = 0;                   // Line 18: This should be detected!
"""
        issues = self.lint_only_this_rule(code)
        # Should only detect the one on line 18, not any in comments
        self.assert_has_rule(issues, self.rule_id, count=1)
        self.assert_issue_at_line(issues, self.rule_id, 18)

    def test_ignores_types_in_inline_multiline_comments(self):
        """Test that types in inline /* ... */ comments are ignored."""
        code = """
void ProcessSession(/* int session_id */ std::int32_t session_id);  // OK
void GetStatus(/* returns long status */ std::int64_t status);      // OK

/* int, long, short are all primitive types */ std::int32_t valid = 0;  // OK

int problem = 0;  /* but this int is real */  // Line 7: should detect 'int problem'
"""
        issues = self.lint_only_this_rule(code)
        # Should only detect 'int problem' on line 7
        self.assert_has_rule(issues, self.rule_id, count=1)
        self.assert_issue_at_line(issues, self.rule_id, 7)

    def test_handles_mixed_code_and_multiline_comments(self):
        """Test handling of code mixed with multi-line comments."""
        code = """
/*
 * Multi-line comment at the start mentioning int and long
 */
std::int32_t valid1 = 0;                 // Line 5: OK

int problem1 = 0;                         // Line 7: should detect

/*
 * Another comment block with:
 * - int type
 * - long sessions
 * - short descriptions
 */
std::int64_t valid2 = 0;                 // Line 15: OK

unsigned int problem2 = 0;                // Line 17: should detect

/* inline comment with int */ std::int32_t valid3 = 0;  // Line 19: OK
long problem3 = 0;                        // Line 20: should detect
"""
        issues = self.lint_only_this_rule(code)
        # Should detect lines 7, 17, and 20
        self.assert_has_rule(issues, self.rule_id, count=3)
        self.assert_issue_at_line(issues, self.rule_id, 7)
        self.assert_issue_at_line(issues, self.rule_id, 17)
        self.assert_issue_at_line(issues, self.rule_id, 20)

    def test_handles_nested_comment_markers_in_strings(self):
        """Test that comment markers in strings don't affect comment detection."""
        code = """
const char* comment_example = "/* this is not a comment */";
int problem = 0;                          // Line 3: should detect
const char* another = "// also not a comment with int keyword";
std::int32_t valid = 0;                   // Line 5: OK
"""
        issues = self.lint_only_this_rule(code)
        # Should only detect line 3
        self.assert_has_rule(issues, self.rule_id, count=1)
        self.assert_issue_at_line(issues, self.rule_id, 3)


@pytest.mark.unit
class TestTypePairTuple(RuleTestCase):
    """Test TYPE_PAIR_TUPLE rule."""

    rule_id = "type-pair-tuple"

    def test_detects_pair_usage(self):
        """Test detection of std::pair usage."""
        code = """
std::pair<int, std::string> GetUserInfo() {      // Line 2: pair in return type
    return std::make_pair(123, "John");
}

void ProcessPair(const std::pair<int, int>& p) { // Line 6: pair in parameter
    auto first = p.first;
}

class Container {
    std::pair<std::string, int> data_;           // Line 11: pair as member
    std::vector<std::pair<int, int>> pairs_;     // Line 12: pair in container
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=4)

    def test_detects_tuple_usage(self):
        """Test detection of std::tuple usage."""
        code = """
std::tuple<int, std::string, bool> GetExtendedInfo() {  // Line 2: tuple return
    return std::make_tuple(123, "John", true);
}

void ProcessTuple(const std::tuple<float, float, float>& coords) {  // Line 6: tuple param
    auto x = std::get<0>(coords);
}

using UserData = std::tuple<int, std::string, bool>;    // Line 10: tuple alias
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)

    def test_accepts_proper_structs(self):
        """Test that proper struct usage is accepted."""
        issues = self.lint_only_this_rule(CppSamples.TYPE_PAIR_TUPLE_GOOD)
        self.assert_no_issues(issues)

    def test_suggests_struct_alternative(self):
        """Test that suggestions include creating a struct."""
        code = """
// Instead of this:
std::pair<int, std::string> user_data;

// The linter should suggest:
// struct UserData {
//     int id;
//     std::string name;
// };
"""
        issues = self.lint_only_this_rule(code)
        if issues:
            # Check that the suggestion mentions creating a struct
            self.assertIn("struct", issues[0].suggested_fix.lower())

    def test_ignores_template_specializations_for_type_traits(self):
        """Test that template specializations for type traits are not flagged."""
        code = """
template <typename T1, typename T2>
struct IsPair<std::pair<T1, T2>> : std::true_type {};

template <typename... Args>
struct IsTuple<std::tuple<Args...>> : std::true_type {};

template <typename T>
struct IsContainer<std::pair<T, T>> {
    static constexpr bool value = false;
};
"""
        issues = self.lint_only_this_rule(code)
        # Template specializations should not be flagged
        self.assert_no_issues(issues)
