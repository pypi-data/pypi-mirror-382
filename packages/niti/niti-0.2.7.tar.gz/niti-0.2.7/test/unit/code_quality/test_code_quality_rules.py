"""Unit tests for code quality rules."""

from test.test_utils import RuleTestCase

import pytest


@pytest.mark.unit
class TestQualityMagicNumbers(RuleTestCase):
    """Test QUALITY_MAGIC_NUMBERS rule."""

    rule_id = "quality-magic-numbers"

    def test_detects_magic_numbers(self):
        """Test detection of magic numbers in code."""
        code = """
void ProcessData() {
    const int buffer_size = 1024;      // Line 3: OK - power of 2
    
    if (count > 100) {                  // Line 5: magic number
        ResizeBuffer(2048);             // Line 6: OK - power of 2
    }
    
    for (int i = 0; i < 10; ++i) {     // Line 9: magic number
        data[i] *= 1.5;                 // Line 10: magic number
    }
}

// These should be OK
const int kMaxSize = 100;
constexpr float kScaleFactor = 1.5f;

void BetterCode() {
    if (count > kMaxSize) {
        ResizeBuffer(kDefaultBufferSize);
    }
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)  # Only 100, 10, and 1.5 are flagged

    def test_accepts_named_constants(self):
        """Test that named constants are accepted."""
        code = """
namespace Constants {
    constexpr int kMaxConnections = 100;
    constexpr float kPi = 3.14159f;
    constexpr size_t kBufferSize = 1024;
    constexpr std::size_t kOtherSize = 256;
}

void ProcessWithConstants() {
    if (connections > Constants::kMaxConnections) {
        // Handle overflow
    }
    
    float circumference = 2.0f * Constants::kPi * radius;
    
    std::vector<char> buffer(Constants::kBufferSize);
    std::array<int, Constants::kOtherSize> arr{};
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_accepts_powers_of_two(self):
        """Test that powers of 2 are accepted as non-magic numbers."""
        code = """
void ConfigureBuffers() {
    const int buffer_size = 1024;     // OK - power of 2
    ResizeBuffer(2048);               // OK - power of 2  
    std::array<int, 4096> data;       // OK - power of 2
    const size_t cache_size = 512;    // OK - power of 2
    
    // Also test hex powers of 2
    const int hex_size = 0x400;       // OK - 1024 in hex
    const int binary_size = 0b10000000000; // OK - 1024 in binary
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_common_exceptions(self):
        """Test that common values like 0, 1, -1 are not flagged."""
        code = """
void CommonPatterns() {
    int index = 0;              // OK: zero initialization
    int count = 1;              // OK: one is common
    int error_code = -1;        // OK: -1 for error
    
    bool first = true;          // OK: boolean values
    float zero = 0.0f;          // OK: zero float
    
    // Array indices
    data[0] = value;            // OK: array access
    data[size - 1] = last;      // OK: last element
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)


