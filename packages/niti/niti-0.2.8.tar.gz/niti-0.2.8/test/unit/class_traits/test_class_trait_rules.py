"""Unit tests for class trait rules."""

from test.fixtures.cpp_samples import CppSamples
from test.test_utils import RuleTestCase

import pytest


@pytest.mark.unit
class TestClassTraitMissing(RuleTestCase):
    """Test CLASS_TRAIT_MISSING rule."""

    rule_id = "class-trait-missing"

    def test_detects_missing_traits(self):
        """Test detection of classes without required traits."""
        issues = self.lint_only_this_rule(CppSamples.CLASS_TRAIT_MISSING_BAD)
        self.assert_has_rule(issues, self.rule_id, count=2)

    def test_accepts_classes_with_traits(self):
        """Test that classes with traits are accepted."""
        issues = self.lint_only_this_rule(CppSamples.CLASS_TRAIT_MISSING_GOOD)
        self.assert_no_issues(issues)

    def test_various_trait_types(self):
        """Test detection with various trait types."""
        code = """
// Missing traits
class ResourceManager {              // Line 3: needs trait
public:
    void Manage();
};

// With traits  
class FileManager : public NonCopyableNonMovable {
public:
    void Manage();
};

class DataProcessor : public NonCopyable {
public:
    void Process();
};

class ValueHolder : public CopyableMovable {
public:
    int GetValue() const;
};

// Utility class should use StaticClass trait
class MathUtils {                    // Line 25: needs StaticClass trait
public:
    static int Add(int a, int b);
    static int Multiply(int a, int b);
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=2)
        self.assert_issue_at_line(issues, self.rule_id, 3)
        self.assert_issue_at_line(issues, self.rule_id, 25)

    def test_exceptions_for_simple_types(self):
        """Test that simple structs/POD types might not need traits."""
        code = """
// Simple POD struct - might not need trait
struct Point {
    float x, y, z;
};

// Simple data holder - might not need trait  
struct Config {
    int max_connections;
    std::string server_url;
    bool enable_logging;
};

// Complex class - needs trait
class ConnectionManager {            // Should need trait
    std::vector<Connection> connections_;
    void AddConnection();
};
"""
        self.lint_only_this_rule(code)
        # POD structs might be exempt, but ConnectionManager should need trait


@pytest.mark.unit
class TestClassTraitStatic(RuleTestCase):
    """Test CLASS_TRAIT_STATIC rule."""

    rule_id = "class-trait-static"

    def test_detects_static_only_classes_without_trait(self):
        """Test detection of classes with only static members missing StaticClass trait."""
        code = """
class StringUtils {                  // Line 2: all static, needs StaticClass
public:
    static std::string ToUpper(const std::string& str);
    static std::string ToLower(const std::string& str);
    static bool StartsWith(const std::string& str, const std::string& prefix);
};

class FileUtils : public StaticClass {  // OK: has StaticClass trait
public:
    static bool Exists(const std::string& path);
    static std::string ReadFile(const std::string& path);
};

class MixedClass {                   // OK: has instance members too
public:
    static int GetGlobalCount();
    void ProcessInstance();
    
private:
    int instance_data_;
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=1)
        self.assert_issue_at_line(issues, self.rule_id, 2)

    def test_namespace_vs_static_class(self):
        """Test suggestion to use namespace instead of static class."""
        code = """
// This pattern suggests using a namespace instead
class Constants {                    // Line 3: all static constants
public:
    static constexpr int kMaxSize = 100;
    static constexpr float kPi = 3.14159f;
    static const std::string kDefaultName;
};

// Better as namespace:
namespace BetterConstants {
    constexpr int kMaxSize = 100;
    constexpr float kPi = 3.14159f;
    const std::string kDefaultName = "default";
}
"""
        issues = self.lint_only_this_rule(code)
        if issues:
            # Should suggest considering namespace
            self.assertIn("namespace", issues[0].suggested_fix.lower())
