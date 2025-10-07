"""Modern C++ feature rules."""

from typing import Any, List

from ..core.issue import LintIssue
from .base import ASTRule
from .rule_id import RuleId


class ModernMissingNoexceptRule(ASTRule):
    """Rule to suggest adding noexcept to functions.

    Checks for destructors and move operations that should be noexcept.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if self.has_file_level_disable(content, str(self.rule_id)):
            return self.issues

        # EXCLUDE: pybind11 bindings (these often have complex exception handling)
        if "pybind" in file_path.lower() or "#include <pybind11" in content:
            return self.issues

        # EXCLUDE: test files (tests often use assertions and complex operations)
        if "/test/" in file_path or "Test.cpp" in file_path or "_test.cpp" in file_path:
            return self.issues

        # Find all function declarations/definitions
        # Note: Member functions are represented as field_declaration nodes
        # Free functions are represented as declaration nodes
        function_nodes = self.find_nodes_by_types(
            tree,
            [
                "function_declaration",
                "function_definition",
                "field_declaration",
                "declaration",
            ],
        )

        for func_node in function_nodes:
            # Only process nodes that are actually functions
            if self._is_function_node(func_node, content):
                self._check_noexcept_candidacy(func_node, content, file_path)

        return self.issues

    def _check_noexcept_candidacy(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check if function should be noexcept."""
        try:
            func_name = self._get_function_name(func_node, content)

            if not func_name:
                return

            # Skip deleted functions - they cannot have noexcept
            if self._is_deleted_function(func_node, content):
                return

            # Check if it returns void (void functions don't need noexcept)
            # Void functions can throw exceptions (i.e Setter methods)
            if self._returns_void_noexcept(func_node, content):
                return

            # Check if it's already noexcept
            if self._is_already_noexcept(func_node, content):
                return

            should_be_noexcept = False
            reason = ""

            # CASE 1: Destructors (must be noexcept)
            if func_name.startswith("~"):
                should_be_noexcept = True
                reason = "Destructors must be noexcept"

            # CASE 2: Move operations (must be noexcept for STL compatibility)
            elif self._is_move_operation(func_node, content):
                should_be_noexcept = True
                reason = "Move operations should be noexcept for STL compatibility"

            # CASE 3: ONLY trivial member variable getters
            elif self._is_trivial_getter(func_node, content):
                should_be_noexcept = True
                reason = "Trivial getters should be noexcept"

            # That's it - no other cases to avoid false positives!

            if should_be_noexcept:
                line_num = func_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=func_node.start_point[1] + 1,
                    message=f"Function '{func_name}' should be noexcept - {reason}",
                    suggested_fix="Add 'noexcept' specifier to function declaration",
                )

        except Exception:
            # Skip on parsing errors
            pass

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node.

        Handles:
        - Regular functions: identifier or field_identifier
        - Operators: operator_name (e.g., operator=, operator+, etc.)
        - Destructors: identifier starting with ~
        - Functions with reference/pointer return types (where function_declarator is nested)
        """
        def find_function_declarator(node):
            """Recursively find function_declarator node."""
            if node.type == "function_declarator":
                return node
            for child in node.children:
                result = find_function_declarator(child)
                if result:
                    return result
            return None

        try:
            func_declarator = find_function_declarator(func_node)
            if func_declarator:
                for subchild in func_declarator.children:
                    if subchild.type in ["identifier", "field_identifier"]:
                        return self.get_text_from_node(subchild, content)
                    elif subchild.type == "operator_name":
                        # For operators like operator=, operator+, etc.
                        return self.get_text_from_node(subchild, content)
            return ""
        except Exception:
            return ""

    def _is_deleted_function(self, func_node: Any, content: str) -> bool:
        """Check if function is deleted (= delete).

        Deleted functions cannot have noexcept specifier.
        """
        try:
            func_text = self.get_text_from_node(func_node, content)
            # Check for = delete pattern
            return "= delete" in func_text or "=delete" in func_text
        except Exception:
            return False

    def _is_already_noexcept(self, func_node: Any, content: str) -> bool:
        """Check if function is already marked noexcept."""
        try:
            func_text = self.get_text_from_node(func_node, content)
            return "noexcept" in func_text
        except Exception:
            return False

    def _returns_void_noexcept(self, func_node: Any, content: str) -> bool:
        """Check if function returns void."""
        try:
            func_text = self.get_text_from_node(func_node, content)
            return "void" in func_text
        except Exception:
            return False

    def _is_move_operation(self, func_node: Any, content: str) -> bool:
        """Check if function is a move constructor or move assignment.
        
        Only checks for && in the parameter list, not in the function body
        (to avoid false positives from logical AND operators).
        """
        try:
            func_text = self.get_text_from_node(func_node, content)

            # Extract just the function signature (before the opening brace or semicolon)
            # This avoids matching && in the function body (logical AND)
            signature = func_text.split('{')[0].split(';')[0]

            # Look for move constructor/assignment patterns in signature only
            if "&&" in signature:  # Rvalue reference in parameter
                # Move constructor or move assignment
                if (
                    "operator=" in signature
                    or self._looks_like_move_constructor(signature, func_text)
                ):
                    return True

            return False
        except Exception:
            return False

    def _looks_like_move_constructor(self, signature: str, full_text: str) -> bool:
        """Check if function signature looks like a move constructor.

        A move constructor must:
        1. Have && in parameters
        2. Have the class name as the function name
        3. Take a single parameter of the form ClassName&&

        Args:
            signature: Function signature (declaration part before body)
            full_text: Full function text (for additional context)
        """
        # Must have && in the signature (rvalue reference parameter)
        if "&&" not in signature:
            return False

        # Must not be operator= (that's handled separately)
        if "operator=" in signature:
            return False

        # Must have parameter list
        if "(" not in signature or ")" not in signature:
            return False

        # Extract function name and parameter part
        try:
            import re

            param_start = signature.find("(")
            param_end = signature.rfind(")")
            params = signature[param_start:param_end+1]

            # Extract function name (the identifier before the opening parenthesis)
            # Handle cases like: MyClass(MyClass&&), explicit MyClass(MyClass&&)
            func_name_match = re.search(r'\b(\w+)\s*\(', signature)
            if not func_name_match:
                return False

            func_name = func_name_match.group(1)

            # Check if parameter matches ClassName&& pattern where ClassName is the function name
            # This ensures we only flag actual move constructors, not template functions like:
            # template<typename T> void LaunchThread(Rank, T&&)
            # Move constructor pattern: ClassName(ClassName&&) or ClassName(const ClassName&&)
            move_ctor_pattern = rf'\(\s*(?:const\s+)?{func_name}\s*&&'
            if re.search(move_ctor_pattern, params):
                return True

        except Exception:
            pass

        return False

    def _is_trivial_getter(self, func_node: Any, content: str) -> bool:
        """Only catch truly trivial getters: const methods that return member variables directly.
        
        This is ultra-restrictive to avoid false positives in codebases with:
        - Defensive validation (ASSERT_*, RAISE_*)
        - Modern string formatting (std::format)
        - Complex resource management
        """
        try:
            func_text = self.get_text_from_node(func_node, content)

            # Must be const
            if "const" not in func_text:
                return False

            # Must not return void
            if "void" in func_text:
                return False

            # Must have exactly one return statement
            if func_text.count("return") != 1:
                return False

            # Must not call any functions (no parentheses except declaration)
            # Count parens: declaration has 2, if more than 2 = function calls
            if func_text.count("(") > 2 or func_text.count(")") > 2:
                return False

            # Must not have complex operators, keywords, or patterns that could throw
            forbidden_patterns = [
                "throw", "new", "delete",           # Explicit throwing
                "std::", "format",          # Namespace/formatting (might throw)
                "ASSERT", "RAISE", "CHECK_",        # Validation macros
                "->", ".at(", "[",                  # Member access/subscript (might throw)
                "ToString", "Serialize",            # Complex operations
            ]
            if any(pattern in func_text for pattern in forbidden_patterns):
                return False

            # Must have inline body with single return
            if "{" in func_text and "}" in func_text:
                body = func_text.split("{")[1].split("}")[0].strip()
                # Body should be just "return member_variable_;"
                # Very simple: no more than 3 tokens (return, variable, semicolon)
                if not (body.startswith("return") and body.count(";") == 1 and len(body.split()) <= 3):
                    return False
            else:
                # Declaration only - we can't verify it's trivial, skip it
                return False

            return True

        except Exception:
            return False


class ModernMissingConstRule(ASTRule):
    """Rule to suggest making methods const.

    Detects getter methods that should be const but aren't marked as const.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []
        if self.has_file_level_disable(content, str(self.rule_id)):
            return self.issues

        # We only care about definitions, as declarations might not have the 'const' keyword
        function_nodes = self.find_nodes_by_types(tree, ["function_definition"])

        for func_node in function_nodes:
            # Ensure we are inside a class
            parent = func_node.parent
            while parent and parent.type != "class_specifier":
                parent = parent.parent
            if not parent:
                continue  # Skip free functions

            self._check_const_candidacy(func_node, content, file_path, parent)

        return self.issues

    def _check_const_candidacy(
        self, func_node: Any, content: str, file_path: str, class_node: Any
    ) -> None:
        """Check if a specific function should be const."""
        try:
            func_name = self._get_function_name(func_node, content)
            class_name = self._get_class_name(class_node, content)

            if not func_name or self._should_skip_function(
                func_name, class_name
            ):
                return

            if self._is_already_const(func_node, content):
                return

            # Skip static methods - they cannot have const qualifier
            if self._is_static_method(func_node, content):
                return

            # Skip methods marked with override - they must match base class signature
            if self._is_override_method(func_node, content):
                return

            if self._is_getter_method(func_name, func_node, content):
                line_num = func_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=func_node.start_point[1] + 1,
                    message=f"Getter method '{func_name}' should be const",
                    suggested_fix="Add 'const' qualifier to method declaration",
                )
        except Exception:
            pass

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from a function_definition node."""
        declarator = func_node.child_by_field_name("declarator")
        if declarator:
            # This can be a simple identifier or a qualified_identifier
            name_node = declarator.child_by_field_name("declarator")
            if name_node:
                return self.get_text_from_node(name_node, content)
        return ""

    def _get_class_name(self, class_node: Any, content: str) -> str:
        """Extract the class name from a class_specifier node."""
        name_node = class_node.child_by_field_name("name")
        if name_node:
            return self.get_text_from_node(name_node, content)
        return ""

    def _should_skip_function(self, func_name: str, class_name: str) -> bool:
        """Check if function should be skipped from const checking."""
        if (
            func_name == class_name  # Constructor
            or func_name.startswith("~")  # Destructor
            or func_name.startswith("operator")  # Operator
        ):
            return True

        mutating_prefixes = {
            "set",
            "add",
            "insert",
            "remove",
            "delete",
            "clear",
            "update",
            "modify",
        }
        for prefix in mutating_prefixes:
            if func_name.lower().startswith(prefix):
                return True
        return False

    def _is_already_const(self, func_node: Any, content: str) -> bool:
        """Check if function is already marked const."""
        declarator = func_node.child_by_field_name("declarator")
        if not declarator:
            return False

        # The 'const' qualifier can be:
        # 1. A child of the function_declarator node
        # 2. A sibling of the declarator (less common)

        # First check within the declarator
        for child in declarator.children:
            if (
                child.type == "type_qualifier"
                and self.get_text_from_node(child, content) == "const"
            ):
                return True

        # Also check siblings of the declarator
        for child in func_node.children:
            if (
                child.type == "type_qualifier"
                and self.get_text_from_node(child, content) == "const"
            ):
                if child.start_byte > declarator.end_byte:
                    return True
        return False

    def _is_static_method(self, func_node: Any, content: str) -> bool:
        """Check if function is a static method.

        Static methods cannot have const qualifier as they don't have a 'this' pointer.
        """
        try:
            func_text = self.get_text_from_node(func_node, content)
            # Check for 'static' keyword in the function signature
            # Look for it before the return type or function name
            return "static" in func_text.split("(")[0]
        except Exception:
            return False

    def _is_override_method(self, func_node: Any, content: str) -> bool:
        """Check if function is marked with override keyword.

        Methods marked with 'override' must match the base class signature,
        so we cannot add const unless the base class method is also const.
        """
        try:
            func_text = self.get_text_from_node(func_node, content)
            return "override" in func_text
        except Exception:
            return False

    def _is_getter_method(
        self, func_name: str, func_node: Any, content: str
    ) -> bool:
        """Check if function is a getter method."""
        if self._returns_void(func_node, content):
            return False

        # Check if the method body modifies member variables
        # This is a simple heuristic - if we see assignments to members, it's not a const-safe getter
        func_text = self.get_text_from_node(func_node, content)
        if self._appears_to_modify_state(func_text):
            return False

        getter_prefixes = {
            "get",
            "is",
            "has",
            "can",
            "should",
            "will",
            "size",
            "empty",
        }
        for prefix in getter_prefixes:
            if func_name.lower().startswith(prefix):
                return True

        if self._has_no_parameters(func_node, content):
            return True

        return False
    
    def _appears_to_modify_state(self, func_text: str) -> bool:
        """Check if function appears to modify member state."""
        # Look for patterns that suggest state modification
        # This is a heuristic - not perfect but catches common cases
        
        # Check for member variable modifications (e.g., member_ = value, member_ += value)
        import re
        
        # Pattern for member variable assignment (members usually end with _)
        if re.search(r'\b\w+_\s*[+\-*/]?=', func_text):
            return True
        
        # Check for increment/decrement of members
        if re.search(r'(\+\+|--)\s*\w+_|\w+_\s*(\+\+|--)', func_text):
            return True
        
        # Check for method calls that likely modify state
        modifying_methods = ['push', 'pop', 'insert', 'erase', 'clear', 'resize', 'reserve',
                             'Read', 'Write', 'Append', 'Update', 'Modify']
        for method in modifying_methods:
            if f'.{method}(' in func_text or f'->{method}(' in func_text or f'{method}<' in func_text:
                return True
        
        return False

    def _returns_void(self, func_node: Any, content: str) -> bool:
        """Check if function returns void."""
        return_type = func_node.child_by_field_name("type")
        return (
            return_type is not None
            and "void" in self.get_text_from_node(return_type, content)
        )

    def _has_no_parameters(self, func_node: Any, content: str) -> bool:
        """Check if function has no parameters."""
        declarator = func_node.child_by_field_name("declarator")
        if declarator:
            param_list = declarator.child_by_field_name("parameters")
            if param_list:
                return param_list.named_child_count == 0
        return True


class ModernNodiscardMissingRule(ASTRule):
    """Enhanced rule to suggest adding [[nodiscard]] to functions.

    This is a more comprehensive version of the existing nodiscard rule,
    with enhanced detection for factory functions, getters, and validation functions.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if self.has_file_level_disable(content, str(self.rule_id)):
            return self.issues

        # Find all function declarations/definitions
        # Note: Member functions are represented as field_declaration nodes
        # Free functions are represented as declaration nodes
        function_nodes = self.find_nodes_by_types(
            tree,
            [
                "function_declaration",
                "function_definition",
                "field_declaration",
                "declaration",
            ],
        )

        for func_node in function_nodes:
            # Only process nodes that are actually functions
            if self._is_function_node(func_node, content):
                self._check_enhanced_nodiscard(func_node, content, file_path)

        return self.issues

    def _check_enhanced_nodiscard(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Enhanced check for nodiscard candidacy."""
        try:
            func_name = self._get_function_name(func_node, content)

            if not func_name or self._should_skip_function(func_name):
                return

            # Check if it's already marked with nodiscard
            if self._has_nodiscard(func_node, content):
                return

            # Check if it returns void
            if self._returns_void(func_node, content):
                return

            should_have_nodiscard = False
            reason = ""

            # Enhanced factory function detection
            if self._is_enhanced_factory_function(func_name):
                should_have_nodiscard = True
                reason = "Factory functions should not have their return value ignored"

            # Enhanced query/getter functions
            elif self._is_enhanced_query_function(func_name):
                should_have_nodiscard = True
                reason = "Query/getter functions should not have their return value ignored"

            # Validation and checking functions
            elif self._is_validation_function(func_name):
                should_have_nodiscard = True
                reason = "Validation functions should not have their return value ignored"

            # Functions returning important resources or handles
            elif self._returns_important_resource(func_node, content):
                should_have_nodiscard = True
                reason = "Functions returning important resources should not be ignored"

            # Mathematical or computational functions
            elif self._is_computational_function(func_name):
                should_have_nodiscard = True
                reason = "Computational functions should not have their return value ignored"

            if should_have_nodiscard:
                line_num = func_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=func_node.start_point[1] + 1,
                    message=f"Function '{func_name}' should be [[nodiscard]] - {reason}",
                    suggested_fix="Add [[nodiscard]] attribute before function declaration",
                )

        except Exception:
            # Skip on parsing errors
            pass

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Extract function name from AST node."""
        try:
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type in ["identifier", "field_identifier"]:
                            return self.get_text_from_node(subchild, content)
            return ""
        except Exception:
            return ""

    def _should_skip_function(self, func_name: str) -> bool:
        """Check if function should be skipped."""
        if func_name.startswith("~") or func_name.startswith("operator"):
            return True
        return False

    def _has_nodiscard(self, func_node: Any, content: str) -> bool:
        """Check if function already has [[nodiscard]]."""
        try:
            func_text = self.get_text_from_node(func_node, content)
            return "[[nodiscard]]" in func_text or "nodiscard" in func_text
        except Exception:
            return False

    def _returns_void(self, func_node: Any, content: str) -> bool:
        """Check if function returns void."""
        try:
            func_text = self.get_text_from_node(func_node, content)
            return "void" in func_text
        except Exception:
            return False

    def _is_enhanced_factory_function(self, func_name: str) -> bool:
        """Enhanced factory function detection."""
        factory_patterns = {
            "Create",
            "Make",
            "Build",
            "Construct",
            "New",
            "Generate",
            "Produce",
            "Allocate",
            "GetInstance",
            "GetSingleton",
            "Clone",
            "Copy",
            "Duplicate",
            "Spawn",
            "FromString",
            "FromJson",
            "FromConfig",
            "Parse",
            "Deserialize",
        }

        for pattern in factory_patterns:
            if func_name.startswith(pattern):
                return True
        return False

    def _is_enhanced_query_function(self, func_name: str) -> bool:
        """Enhanced query/getter function detection."""
        query_patterns = {
            "Get",
            "Find",
            "Search",
            "Query",
            "Lookup",
            "Fetch",
            "Retrieve",
            "Extract",
            "Compute",
            "Calculate",
            "Count",
            "Size",
            "Length",
            "Is",
            "Has",
            "Can",
            "Should",
            "Check",
            "Contains",
            "Exists",
            "Empty",
            "Full",
            "Available",
            "Ready",
            "Active",
            "Enabled",
            "Valid",
            "Equal",
            "Compare",
        }

        for pattern in query_patterns:
            if func_name.startswith(pattern):
                return True
        return False

    def _is_validation_function(self, func_name: str) -> bool:
        """Check if function is for validation."""
        validation_patterns = {
            "Validate",
            "Verify",
            "Test",
            "Ensure",
            "Assert",
            "Confirm",
            "Audit",
            "TryParse",
            "TryGet",
            "TrySet",
            "TryConnect",
            "TryLock",
            "TryAcquire",
        }

        for pattern in validation_patterns:
            if func_name.startswith(pattern):
                return True
        return False

    def _returns_important_resource(self, func_node: Any, content: str) -> bool:
        """Check if function returns important resources."""
        try:
            func_text = self.get_text_from_node(func_node, content)

            # Look for important resource types
            resource_indicators = {
                "std::unique_ptr",
                "std::shared_ptr",
                "std::weak_ptr",
                "Handle",
                "Socket",
                "Connection",
                "Stream",
                "Buffer",
                "Token",
                "Key",
                "Credential",
                "Result",
                "Status",
                "Optional",
                "Expected",
                "Future",
                "Promise",
            }

            for indicator in resource_indicators:
                if indicator in func_text:
                    return True
            return False
        except Exception:
            return False

    def _is_computational_function(self, func_name: str) -> bool:
        """Check if function performs computation."""
        computational_patterns = {
            "Calculate",
            "Compute",
            "Evaluate",
            "Process",
            "Transform",
            "Convert",
            "Encode",
            "Decode",
            "Compress",
            "Decompress",
            "Hash",
            "Checksum",
            "Sum",
            "Average",
            "Min",
            "Max",
            "Sort",
            "Filter",
            "Map",
            "Reduce",
            "Aggregate",
        }

        for pattern in computational_patterns:
            if func_name.startswith(pattern):
                return True

        # Also check for mathematical operations
        math_patterns = {"Add", "Subtract", "Multiply", "Divide", "Mod"}
        for pattern in math_patterns:
            if func_name.startswith(pattern):
                return True

        return False


class ModernSmartPtrByRefRule(ASTRule):
    """Rule to enforce passing smart pointers by value for ownership transfer.

    Detects function parameters that are smart pointers passed by reference
    and suggests passing them by value instead for clear ownership semantics.
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if self.has_file_level_disable(content, str(self.rule_id)):
            return self.issues

        # Find all function declarations/definitions
        # Note: Member functions are represented as field_declaration nodes
        # Free functions are represented as declaration nodes
        function_nodes = self.find_nodes_by_types(
            tree,
            [
                "function_declaration",
                "function_definition",
                "field_declaration",
                "declaration",
            ],
        )

        for func_node in function_nodes:
            # Only process nodes that are actually functions
            if self._is_function_node(func_node, content):
                self._check_smart_ptr_parameters(func_node, content, file_path)

        return self.issues

    def _check_smart_ptr_parameters(
        self, func_node: Any, content: str, file_path: str
    ) -> None:
        """Check function parameters for smart pointers passed by reference."""
        try:
            # Find the parameter list
            param_list = self._find_parameter_list(func_node)
            if not param_list:
                return

            # Check each parameter
            for param in param_list.children:
                if param.type == "parameter_declaration":
                    self._check_parameter_for_smart_ptr(
                        param, content, file_path
                    )

        except Exception:
            # Skip on parsing errors
            pass

    def _find_parameter_list(self, func_node: Any) -> Any:
        """Find the parameter list node within a function."""
        try:
            for child in func_node.children:
                if child.type == "function_declarator":
                    for subchild in child.children:
                        if subchild.type == "parameter_list":
                            return subchild
            return None
        except Exception:
            return None

    def _check_parameter_for_smart_ptr(
        self, param_node: Any, content: str, file_path: str
    ) -> None:
        """Check a single parameter for smart pointer by reference."""
        try:
            param_text = self.get_text_from_node(param_node, content)

            # Check if parameter is a smart pointer type
            if not self._is_smart_pointer_type(param_text):
                return

            # Check if it's passed by reference (which we want to flag)
            if not self._is_passed_by_reference(param_text):
                return  # Already by value, which is what we want

            # Check if it's a move parameter (T&&) - allow this
            if self._is_move_parameter(param_text):
                return

            # Get parameter name for better error message
            param_name = self._extract_parameter_name(param_node, content)

            line_num = param_node.start_point[0] + 1
            if self.should_skip_line(
                self.get_line(content, line_num), str(self.rule_id)
            ):
                return

            self.add_issue(
                file_path=file_path,
                line_number=line_num,
                column=param_node.start_point[1] + 1,
                message=f"Smart pointer parameter '{param_name}' should be passed by value for clear ownership transfer semantics",
                suggested_fix="Remove 'const' and '&' to pass by value: 'std::unique_ptr<T> param' or 'std::shared_ptr<T> param'",
            )

        except Exception:
            # Skip on parsing errors
            pass

    def _is_smart_pointer_type(self, param_text: str) -> bool:
        """Check if parameter text contains smart pointer types."""
        smart_ptr_types = {
            "std::unique_ptr",
            "std::shared_ptr",
            "std::weak_ptr",
            "unique_ptr",
            "shared_ptr",
            "weak_ptr",
        }

        for smart_ptr in smart_ptr_types:
            if smart_ptr in param_text:
                return True
        return False

    def _is_passed_by_reference(self, param_text: str) -> bool:
        """Check if parameter is already passed by reference."""
        # Look for & (reference) but not && (move)
        if "&" in param_text:
            # Check if it's a single & (reference) not && (move)
            if "&&" not in param_text:
                return True
        return False

    def _is_const_reference(self, param_text: str) -> bool:
        """Check if parameter is a const reference."""
        return (
            "const" in param_text
            and "&" in param_text
            and "&&" not in param_text
        )

    def _is_passed_by_value(self, param_text: str) -> bool:
        """Check if parameter is passed by value (no & or &&)."""
        return "&" not in param_text

    def _is_unique_ptr_type(self, param_text: str) -> bool:
        """Check if parameter is a unique_ptr type."""
        return "unique_ptr" in param_text

    def _is_shared_ptr_type(self, param_text: str) -> bool:
        """Check if parameter is a shared_ptr type."""
        return "shared_ptr" in param_text

    def _is_move_parameter(self, param_text: str) -> bool:
        """Check if parameter is a move parameter (T&&)."""
        return "&&" in param_text

    def _extract_parameter_name(self, param_node: Any, content: str) -> str:
        """Extract parameter name from parameter declaration."""
        try:
            # Find the last identifier in the parameter declaration
            identifiers = []

            def collect_identifiers(node):
                if node.type == "identifier":
                    identifiers.append(self.get_text_from_node(node, content))
                for child in node.children:
                    collect_identifiers(child)

            collect_identifiers(param_node)

            # Return the last identifier (parameter name)
            if identifiers:
                return identifiers[-1]
            return "unknown"
        except Exception:
            return "unknown"

