"""Unit tests for include and header rules."""

from test.fixtures.cpp_samples import CppSamples
from test.test_utils import RuleTestCase

import pytest


@pytest.mark.unit
class TestIncludeOrderWrong(RuleTestCase):
    """Test INCLUDE_ORDER_WRONG rule."""

    rule_id = "include-order-wrong"

    def test_detects_wrong_order(self):
        """Test detection of incorrectly ordered includes."""
        issues = self.lint_only_this_rule(CppSamples.INCLUDE_ORDER_WRONG_BAD)
        self.assert_has_rule(issues, self.rule_id)

    def test_accepts_correct_order(self):
        """Test that correctly ordered includes are accepted."""
        issues = self.lint_only_this_rule(CppSamples.INCLUDE_ORDER_WRONG_GOOD)
        self.assert_no_issues(issues)

    def test_detailed_ordering_rules(self):
        """Test detailed include ordering rules."""
        code = """
// Wrong: mixed order
#include <vector>
#include "MyClass.h"
#include <algorithm>
#include "commons/PrecompiledHeaders.h"
#include <string>

// Should be:
// 1. Precompiled headers
// 2. System headers (alphabetically)
// 3. Third-party headers (alphabetically)
// 4. Project headers (alphabetically)
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id)

    def test_groups_with_blank_lines(self):
        """Test that include groups should be separated by blank lines."""
        code = """
#include "commons/PrecompiledHeaders.h"

#include <algorithm>
#include <string>
#include <vector>

#include <boost/asio.hpp>
#include <boost/thread.hpp>

#include "MyClass.h"
#include "MyOtherClass.h"
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)


@pytest.mark.unit
class TestIncludeAngleBracketForbidden(RuleTestCase):
    """Test INCLUDE_ANGLE_BRACKET_FORBIDDEN rule."""

    rule_id = "include-angle-bracket-forbidden"

    def test_detects_angle_brackets_for_local(self):
        """Test detection of angle brackets for local includes."""
        code = """
#include <MyClass.h>              // Line 2: local file with angle brackets
#include <utils/Helper.h>         // Line 3: local file with angle brackets
#include <components/Widget.h>    // Line 4: local file with angle brackets

// These are OK
#include <vector>
#include <string>
#include "MyClass.h"
#include "utils/Helper.h"
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)
        self.assert_issue_at_line(issues, self.rule_id, 2)
        self.assert_issue_at_line(issues, self.rule_id, 3)
        self.assert_issue_at_line(issues, self.rule_id, 4)

    def test_accepts_quotes_for_local(self):
        """Test that quotes for local includes are accepted."""
        code = """
#include "MyClass.h"
#include "utils/Helper.h"
#include "components/Widget.h"
#include "commons/PrecompiledHeaders.h"
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_system_headers_with_angle_brackets(self):
        """Test that system headers with angle brackets are accepted."""
        code = """
#include <iostream>
#include <vector>
#include <memory>
#include <cstdint>
#include <sys/types.h>
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)


@pytest.mark.unit
class TestHeaderPragmaOnce(RuleTestCase):
    """Test HEADER_PRAGMA_ONCE rule."""

    rule_id = "header-pragma-once"

    def test_detects_missing_pragma_once(self):
        """Test detection of missing #pragma once in headers."""
        code = """
#include <vector>

namespace MyApp {
    class Widget {
        // Class definition
    };
}
"""
        issues = self.lint_only_this_rule(code, filename="Widget.h")
        self.assert_has_rule(issues, self.rule_id, count=1)

    def test_accepts_pragma_once(self):
        """Test that headers with #pragma once are accepted."""
        code = """
#pragma once

#include <vector>

namespace MyApp {
    class Widget {
        // Class definition
    };
}
"""
        issues = self.lint_only_this_rule(code, filename="Widget.h")
        self.assert_no_issues(issues)

    def test_pragma_once_must_be_first(self):
        """Test that #pragma once must be first non-comment line."""
        code = """
#include <vector>
#pragma once  // Wrong location

namespace MyApp {
    class Widget {};
}
"""
        issues = self.lint_only_this_rule(code, filename="Widget.h")
        self.assert_has_rule(issues, self.rule_id)

    def test_allows_copyright_before_pragma(self):
        """Test that copyright comments are allowed before #pragma once."""
        code = """
// Copyright (c) 2024 Company Name
// Licensed under Apache 2.0

#pragma once

#include <vector>

namespace MyApp {
    class Widget {};
}
"""
        issues = self.lint_only_this_rule(code, filename="Widget.h")
        self.assert_no_issues(issues)

    def test_not_required_for_cpp_files(self):
        """Test that #pragma once is not required for .cpp files."""
        code = """
#include "Widget.h"

namespace MyApp {
    void Widget::Process() {
        // Implementation
    }
}
"""
        issues = self.lint_only_this_rule(code, filename="Widget.cpp")
        self.assert_no_issues(issues)


@pytest.mark.unit
class TestHeaderCopyright(RuleTestCase):
    """Test HEADER_COPYRIGHT rule."""

    rule_id = "header-copyright"

    def test_detects_missing_copyright(self):
        """Test detection of missing copyright header."""
        code = """
#pragma once

namespace MyApp {
    class Widget {};
}
"""
        issues = self.lint_only_this_rule(code, filename="Widget.h")
        self.assert_has_rule(issues, self.rule_id, count=1)

    def test_accepts_various_copyright_formats(self):
        """Test that various copyright formats are accepted."""
        code = """
// Copyright (c) 2024 Company Name
// All rights reserved.

#pragma once

namespace MyApp {
    class Widget {};
}
"""
        issues = self.lint_only_this_rule(code, filename="Widget.h")
        self.assert_no_issues(issues)

        # Alternative format
        code2 = """
/*
 * Copyright 2024 Company Name
 * Licensed under the Apache License, Version 2.0
 */

#pragma once

class Widget {};
"""
        issues2 = self.lint_only_this_rule(code2, filename="Widget.h")
        self.assert_no_issues(issues2)
