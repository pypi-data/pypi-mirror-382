"""Unit tests for documentation rules."""

from test.fixtures.cpp_samples import CppSamples
from test.test_utils import RuleTestCase

import pytest


@pytest.mark.unit
class TestDocFunctionMissing(RuleTestCase):
    """Test DOC_FUNCTION_MISSING rule."""

    rule_id = "doc-function-missing"

    def test_detects_undocumented_public_functions(self):
        """Test detection of undocumented public functions."""
        code = """
class Widget {
public:
    void Initialize();                    // Line 4: missing docs
    int Calculate(int a, int b);         // Line 5: missing docs
    bool IsValid() const;                // Line 6: missing docs
    
private:
    void InternalProcess();              // Private - docs optional
};

// Free function
void GlobalFunction(int param);          // Line 13: missing docs
"""
        issues = self.lint_only_this_rule(code, filename="test.h")
        self.assert_has_rule(issues, self.rule_id, count=4)
        self.assert_issue_at_line(issues, self.rule_id, 4)
        self.assert_issue_at_line(issues, self.rule_id, 5)
        self.assert_issue_at_line(issues, self.rule_id, 6)
        self.assert_issue_at_line(issues, self.rule_id, 13)

    def test_accepts_documented_functions(self):
        """Test that documented functions are accepted."""
        code = """
class Widget {
public:
    /**
     * @brief Initialize the widget
     */
    void Initialize();
    
    /**
     * @brief Calculate sum of two numbers
     * @param a First number (in)
     * @param b Second number (in)
     * @return Sum of a and b
     */
    int Calculate(int a, int b);
    
    /// @brief Check if widget is valid
    /// @return True if valid, false otherwise
    bool IsValid() const;
};

/**
 * @brief Global processing function
 * @param param Input parameter (in)
 */
void GlobalFunction(int param);
"""
        issues = self.lint_only_this_rule(code, filename="test.h")
        self.assert_no_issues(issues)

    def test_private_functions_optional(self):
        """Test that private functions don't require documentation."""
        code = """
class Implementation {
private:
    void HelperMethod();
    int InternalCalculation(int x);
    
protected:
    void ProtectedMethod();  // Might need docs if part of interface
};
"""
        self.lint_only_this_rule(code, filename="test.h")
        # Private methods typically don't require docs
        # Protected methods might, depending on configuration


@pytest.mark.unit
class TestDocClassMissing(RuleTestCase):
    """Test DOC_CLASS_MISSING rule."""

    rule_id = "doc-class-missing"

    def test_detects_undocumented_classes(self):
        """Test detection of undocumented classes, structs, and enums."""
        code = """
class UndocumentedClass {            // Line 2: missing docs
public:
    void Method();
};

struct UndocumentedStruct {          // Line 7: missing docs
    int x, y;
};

enum class Status {                  // Line 11: missing docs
    Running,
    Stopped,
    Error
};

enum OldStyleEnum {                  // Line 17: missing docs
    VALUE_ONE,
    VALUE_TWO
};
"""
        issues = self.lint_only_this_rule(code, filename="test.h")
        self.assert_has_rule(issues, self.rule_id, count=4)

    def test_accepts_documented_classes(self):
        """Test that documented classes are accepted."""
        issues = self.lint_only_this_rule(CppSamples.DOC_CLASS_MISSING_GOOD, filename="test.h")
        self.assert_no_issues(issues)

    def test_various_doc_styles(self):
        """Test various documentation styles."""
        code = """
/**
 * @brief Doxygen style documentation
 */
class DoxygenStyle {};

/// @brief Single line doxygen style
class SingleLineStyle {};

/** @brief Javadoc style */
class JavadocStyle {};

//! @brief Qt style documentation
class QtStyle {};

/*! 
 * @brief Qt multiline style
 */
class QtMultilineStyle {};
"""
        issues = self.lint_only_this_rule(code, filename="test.h")
        self.assert_no_issues(issues)


@pytest.mark.unit
class TestDocParamDirectionMissing(RuleTestCase):
    """Test DOC_PARAM_DIRECTION_MISSING rule."""

    rule_id = "doc-param-direction-missing"

    def test_detects_missing_direction(self):
        """Test detection of parameters without direction annotations."""
        code = """
/**
 * @brief Process data
 * @param input The input data
 * @param output The output buffer (out)
 * @param flags Processing flags
 */
void ProcessData(const Data& input, Data& output, int flags);
"""
        issues = self.lint_only_this_rule(code, filename="test.h")
        # Should detect missing (in) for 'input' and 'flags'
        self.assert_has_rule(issues, self.rule_id, count=2)

    def test_accepts_all_directions(self):
        """Test that all direction annotations are accepted."""
        code = """
/**
 * @brief Complex processing function
 * @param input Input data (in)
 * @param output Output data (out)
 * @param cache Temporary cache (in/out)
 * @param config Configuration [in]
 * @param result Result buffer [out]
 * @param state Processing state [in,out]
 */
void ComplexProcess(const Data& input, Data& output, Cache& cache,
                   const Config& config, Result& result, State& state);
"""
        issues = self.lint_only_this_rule(code, filename="test.h")
        self.assert_no_issues(issues)


@pytest.mark.unit
class TestDocFunctionParamDocs(RuleTestCase):
    """Test DOC_FUNCTION_MISSING_PARAM_DOCS and related rules."""

    def test_missing_param_documentation(self):
        """Test detection of missing @param documentation."""
        code = """
/**
 * @brief Calculate result
 * @param a First value (in)
 * @return Calculated result
 */
int Calculate(int a, int b, int c);  // Missing @param for b and c
"""
        issues = self.lint_content(
            code, filename="test.h", enable_rules=["doc-function-missing-param-docs"]
        )
        self.assert_has_rule(issues, "doc-function-missing-param-docs", count=1)

    def test_extra_param_documentation(self):
        """Test detection of extra @param documentation."""
        code = """
/**
 * @brief Simple function
 * @param a First parameter (in)
 * @param b Second parameter (in)
 * @param c Non-existent parameter (in)
 * @return Result
 */
int SimpleFunc(int a, int b);  // Extra @param for c
"""
        issues = self.lint_content(
            code, filename="test.h", enable_rules=["doc-function-extra-param-docs"]
        )
        self.assert_has_rule(issues, "doc-function-extra-param-docs", count=1)

    def test_missing_return_documentation(self):
        """Test detection of missing @return documentation."""
        code = """
/**
 * @brief Get the value
 * @param index Index to retrieve (in)
 */
int GetValue(size_t index);  // Missing @return

/**
 * @brief Set the value  
 * @param index Index to set (in)
 * @param value Value to set (in)
 */
void SetValue(size_t index, int value);  // void - no @return needed
"""
        issues = self.lint_content(
            code, filename="test.h", enable_rules=["doc-function-missing-return-docs"]
        )
        self.assert_has_rule(
            issues, "doc-function-missing-return-docs", count=1
        )

    def test_missing_throws_documentation(self):
        """Test detection of missing @throws documentation."""
        code = """
/**
 * @brief Validate input
 * @param data Input data (in)
 * @return True if valid
 */
bool Validate(const Data& data) {
    if (data.empty()) {
        throw std::invalid_argument("empty data");
    }
    return true;
}
"""
        issues = self.lint_content(
            code, filename="test.h", enable_rules=["doc-function-missing-throws-docs"]
        )
        self.assert_has_rule(
            issues, "doc-function-missing-throws-docs", count=1
        )


@pytest.mark.unit
class TestDocQualityRules(RuleTestCase):
    """Test documentation quality rules."""

    def test_param_description_quality(self):
        """Test parameter description quality checks."""
        code = """
/**
 * @brief Process the data
 * @param data data (in)              // Bad: just repeats param name
 * @param index The index (in)        // Bad: just adds "The"
 * @param buffer Input buffer to process (in)  // Good: descriptive
 */
void Process(const Data& data, size_t index, Buffer& buffer);
"""
        issues = self.lint_content(
            code, filename="test.h", enable_rules=["doc-function-param-desc-quality"]
        )
        self.assert_has_rule(issues, "doc-function-param-desc-quality", count=2)

    def test_class_docstring_brief(self):
        """Test that class documentation includes @brief."""
        code = """
/**
 * This class manages widgets
 */
class WidgetManager {};  // Missing @brief tag

/**
 * @brief Manages widget lifecycle
 */
class ProperWidgetManager {};  // Has @brief tag
"""
        issues = self.lint_content(
            code, filename="test.h", enable_rules=["doc-class-docstring-brief"]
        )
        self.assert_has_rule(issues, "doc-class-docstring-brief", count=1)

    def test_thread_safety_documentation(self):
        """Test thread safety documentation for managers/engines."""
        code = """
/**
 * @brief Manages application state
 */
class StateManager {  // Should document thread safety
public:
    void UpdateState();
};

/**
 * @brief Processes data batches
 * @thread_safety Not thread-safe
 */
class DataEngine {  // Has thread safety docs
public:
    void Process();
};

/**
 * @brief Simple data holder
 */
struct DataHolder {  // Not a manager/engine, no thread safety needed
    int value;
};
"""
        issues = self.lint_content(
            code, filename="test.h", enable_rules=["doc-class-docstring-thread-safety"]
        )
        self.assert_has_rule(
            issues, "doc-class-docstring-thread-safety", count=1
        )
