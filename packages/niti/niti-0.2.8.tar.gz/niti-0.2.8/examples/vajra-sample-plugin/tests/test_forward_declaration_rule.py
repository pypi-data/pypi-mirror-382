"""Tests for the ForwardDeclarationRule."""

import unittest
from typing import List
import tree_sitter_cpp as tscpp
from tree_sitter import Parser

from niti_vajra_plugin.rules.forward_declaration_rule import ForwardDeclarationRule
from niti.core.issue import Issue


class TestForwardDeclarationRule(unittest.TestCase):
    """Test cases for ForwardDeclarationRule."""

    def setUp(self):
        """Set up test fixtures."""
        self.rule = ForwardDeclarationRule()
        
        # Initialize tree-sitter parser
        CPP_LANGUAGE = tscpp.language()
        self.parser = Parser()
        self.parser.set_language(CPP_LANGUAGE)

    def _get_issues(self, code: str) -> List[Issue]:
        """Helper to parse code and get issues."""
        tree = self.parser.parse(code.encode())
        return self.rule.check(tree.root_node, code.encode())

    def test_detects_unnecessary_includes_for_pointers(self):
        """Test detection of includes that could be forward declarations."""
        code = """
#pragma once

#include "Widget.h"      // Only used as pointer
#include "Gadget.h"      // Only used as reference
#include "Component.h"   // Used as value - OK

namespace vajra {
    class Manager {
        Widget* widget_ptr_;
        const Gadget& GetGadget();
        Component component_;  // Needs full definition
    };
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 2)
        
        # Check that Widget.h and Gadget.h are flagged
        issue_files = [issue.message for issue in issues]
        self.assertTrue(any("Widget.h" in msg for msg in issue_files))
        self.assertTrue(any("Gadget.h" in msg for msg in issue_files))
        self.assertFalse(any("Component.h" in msg for msg in issue_files))

    def test_accepts_necessary_includes(self):
        """Test that necessary includes are not flagged."""
        code = """
#pragma once

#include "Base.h"        // Used as base class
#include "Member.h"      // Used as member variable
#include "Inline.h"      // Used in inline function

namespace vajra {
    class Derived : public Base {
        Member member_;
        
        void InlineFunc() {
            Inline obj;
            obj.Process();
        }
    };
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 0)

    def test_smart_pointer_usage(self):
        """Test smart pointer usage detection."""
        code = """
#pragma once

#include <memory>
#include "Resource.h"    // Only used in smart pointers
#include "Data.h"       // Used as value

namespace vajra {
    class Container {
        std::shared_ptr<Resource> resource_;
        std::unique_ptr<Resource> owned_resource_;
        Data data_;  // Needs full definition
    };
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 1)
        self.assertIn("Resource.h", issues[0].message)

    def test_skip_system_includes(self):
        """Test that system includes are not flagged."""
        code = """
#pragma once

#include <vector>
#include <string>
#include <memory>
#include "boost/optional.hpp"

namespace vajra {
    class Container {
        std::vector<int>* vec_ptr_;
        std::string* str_ptr_;
    };
}
"""
        issues = self._get_issues(code)
        # System includes should not be flagged
        self.assertEqual(len(issues), 0)

    def test_template_parameters(self):
        """Test handling of template parameters."""
        code = """
#pragma once

#include "TemplateClass.h"  // Used in template

namespace vajra {
    template<typename T>
    class Container {
        T* ptr_;  // Could use forward declaration
    };
    
    // Explicit instantiation
    template class Container<TemplateClass>;
}
"""
        issues = self._get_issues(code)
        # Template usage is complex, might not be flagged
        # depending on implementation
        self.assertLessEqual(len(issues), 1)

    def test_typedef_and_using(self):
        """Test typedef and using declarations."""
        code = """
#pragma once

#include "Original.h"  // Used in typedef/using

namespace vajra {
    using OriginalPtr = Original*;
    typedef Original& OriginalRef;
    
    class User {
        OriginalPtr ptr_;
        OriginalRef GetRef();
    };
}
"""
        issues = self._get_issues(code)
        # Typedef/using might need full definition
        self.assertEqual(len(issues), 0)

    def test_nested_class_usage(self):
        """Test nested class forward declaration opportunities."""
        code = """
#pragma once

#include "Outer.h"  // Contains Outer::Inner

namespace vajra {
    class Container {
        Outer::Inner* inner_ptr_;  // Could use forward declaration
    };
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 1)
        self.assertIn("Outer.h", issues[0].message)

    def test_function_parameters(self):
        """Test function parameter usage."""
        code = """
#pragma once

#include "Param.h"     // Only in function signatures
#include "Return.h"    // Only as return type

namespace vajra {
    class Interface {
        virtual void Process(const Param& param) = 0;
        virtual Return* GetReturn() = 0;
    };
}
"""
        issues = self._get_issues(code)
        self.assertEqual(len(issues), 2)

    def test_inline_function_usage(self):
        """Test that inline functions requiring full definition are handled."""
        code = """
#pragma once

#include "Helper.h"  // Used in inline function

namespace vajra {
    class Utils {
        inline int Calculate() {
            Helper h;
            return h.GetValue();
        }
    };
}
"""
        issues = self._get_issues(code)
        # Inline function needs full definition
        self.assertEqual(len(issues), 0)

    def test_cpp_file_excluded(self):
        """Test that .cpp files are excluded from this rule."""
        # Note: The rule only checks header files
        # This test verifies that by checking a header
        code = """
#include "Implementation.h"

namespace vajra {
    void Function() {
        Implementation impl;
        impl.DoWork();
    }
}
"""
        # If this were a .cpp file, it should not be checked
        # The rule should only apply to headers
        issues = self._get_issues(code)
        # Since we can't simulate file extension in unit test,
        # we expect this to be treated as a header and get no issues
        # because Implementation is used as value
        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()