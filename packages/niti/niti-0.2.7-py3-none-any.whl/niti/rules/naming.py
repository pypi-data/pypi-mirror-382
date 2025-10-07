"""Naming convention rules for C++ code."""

import re
from typing import Any, List, Optional

from ..core.issue import LintIssue
from ..core.severity import Severity
from .base import ASTRule, AutofixResult
from .rule_id import RuleId


class NamingFunctionCaseRule(ASTRule):
    """Rule to enforce PascalCase for function names."""

    def __init__(self, rule_id: RuleId, severity: Severity):
        super().__init__(rule_id, severity)
        self.supports_autofix = True

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find all function declarations/definitions
        function_nodes = self.find_nodes_by_types(
            tree, ["function_declaration", "function_definition"]
        )

        for func_node in function_nodes:
            func_name = self._get_function_name(func_node, content)
            if func_name and not self._should_skip_function(func_name):
                if not self._is_valid_pascalcase(func_name):
                    line_num = self.get_line_from_byte(
                        func_node.start_byte, content
                    )

                    # Check if this line should be skipped due to NOLINT directives
                    line_content = self.get_line(content, line_num)
                    if self.should_skip_line(line_content, str(self.rule_id)):
                        continue

                    # Check if next line skip applies
                    should_skip_next, skip_rules = self.should_skip_next_line(content, line_num)
                    if should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules):
                        continue

                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=1,
                        message=f"Function '{func_name}' should use PascalCase (e.g., 'ProcessRequest')",
                        suggested_fix=self._to_pascalcase(func_name),
                    )

        return self.issues

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Wrapper now delegating to the shared helper on ASTRule."""
        return self.extract_function_name(func_node, content)

    def _should_skip_function(self, func_name: str) -> bool:
        """Check if function should be skipped from naming checks."""
        # Skip unknown (parse failure)
        if func_name == "unknown":
            return True

        # Skip special functions
        if func_name.startswith("~") or func_name.startswith("operator"):
            return True

        # Skip C functions and main
        if func_name in ["main", "printf", "malloc", "free"]:
            return True

        # Skip std library overrides
        if func_name in ["parse", "format"]:
            return True


        # Skip pybind11 macros
        if "PYBIND11_" in func_name:
            return True

        return False

    def _is_valid_pascalcase(self, name: str) -> bool:
        """Check if name follows PascalCase convention."""
        if not name:
            return False

        # Should start with capital letter
        if not name[0].isupper():
            return False

        # Should not have underscores (except leading/trailing for special cases)
        if "_" in name.strip("_"):
            return False

        # Should not be all uppercase (that's not PascalCase)
        if name.isupper():
            return False

        # Should not be all lowercase (that's not PascalCase)
        if name.islower():
            return False

        # Must contain at least one lowercase letter to be proper PascalCase
        if not any(c.islower() for c in name):
            return False

        return True

    def _to_pascalcase(self, name: str) -> str:
        """Convert snake_case or other formats to PascalCase."""
        if "_" in name:
            parts = name.split("_")
            return "".join(part.capitalize() for part in parts if part)
        else:
            return name.capitalize()

    def autofix(
        self,
        file_path: str,
        content: str,
        tree: Any,
        config: Any,
        issues: List[LintIssue],
    ) -> AutofixResult:
        """Automatically fix function naming issues."""
        if not issues:
            return AutofixResult(success=False, message="No issues to fix")

        lines = content.split("\n")
        fixes_applied = 0

        # Process each issue
        for issue in issues:
            # Extract the function name from the message
            match = re.search(
                r"Function '([^']+)' should use PascalCase", issue.message
            )
            if not match:
                continue

            old_name = match.group(1)
            new_name = self._to_pascalcase(old_name)

            # Replace the function name in the specific line
            line_idx = issue.line_number - 1
            if 0 <= line_idx < len(lines):
                # Use word boundaries to avoid partial matches
                pattern = r"\b" + re.escape(old_name) + r"\b"
                if re.search(pattern, lines[line_idx]):
                    lines[line_idx] = re.sub(pattern, new_name, lines[line_idx])
                    fixes_applied += 1

        if fixes_applied > 0:
            new_content = "\n".join(lines)
            return AutofixResult(
                success=True,
                new_content=new_content,
                message=f"Fixed {fixes_applied} function naming issues to PascalCase",
                issues_fixed=fixes_applied,
            )

        return AutofixResult(
            success=False, message="No function names could be fixed"
        )


class NamingVariableCaseRule(ASTRule):
    """Rule to enforce snake_case for variable names."""

    def __init__(self, rule_id: RuleId, severity: Severity):
        super().__init__(rule_id, severity)
        self.supports_autofix = True

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find variable declarations
        declaration_nodes = self.find_nodes_by_types(
            tree, ["declaration", "parameter_declaration", "field_declaration"]
        )

        for decl_node in declaration_nodes:
            var_names = self._extract_variable_names(decl_node, content)
            for var_name, position in var_names:
                if not self._should_skip_variable(var_name):
                    if not self._is_valid_snake_case(var_name):
                        line_num = self.get_line_from_byte(position, content)
                        
                        # Check if this line should be skipped due to NOLINT directives
                        line_content = self.get_line(content, line_num)
                        if self.should_skip_line(line_content, str(self.rule_id)):
                            continue
                        
                        # Check if next line skip applies
                        should_skip_next, skip_rules = self.should_skip_next_line(content, line_num)
                        if should_skip_next and (skip_rules == "all" or str(self.rule_id) in skip_rules):
                            continue
                        
                        self.add_issue(
                            file_path=file_path,
                            line_number=line_num,
                            column=1,
                            message=f"Variable '{var_name}' should use snake_case (e.g., 'user_count')",
                            suggested_fix=self._to_snake_case(var_name),
                        )

        return self.issues

    def _extract_variable_names(
        self, decl_node: Any, content: str
    ) -> List[tuple]:
        """Extract variable names from declaration nodes using proper AST structure."""
        names = []

        # Only process actual declaration nodes
        if decl_node.type not in [
            "declaration",
            "field_declaration",
            "parameter_declaration",
        ]:
            return names

        # Skip template parameters - they follow type naming conventions (PascalCase)
        # not variable naming conventions (snake_case)
        if self._is_template_parameter(decl_node):
            return names

        # Look for specific patterns based on AST structure
        if decl_node.type == "declaration":
            # Pattern: type_specifier init_declarator ;
            # Example: int variable_name = 5;
            for child in decl_node.children:
                if child.type == "init_declarator":
                    # The FIRST child of init_declarator should be the variable name
                    # We must be very strict here to avoid parsing artifacts
                    if (
                        child.children
                        and child.children[0].type == "identifier"
                    ):
                        first_child = child.children[0]
                        text = self.get_text_from_node(first_child, content)
                        if self._is_valid_variable_name(text):
                            names.append((text, first_child.start_byte))
                elif child.type == "identifier":
                    # Simple declaration: std::vector<int> variable_name;
                    # But make sure this identifier comes AFTER a type specifier
                    prev_siblings = []
                    for sibling in decl_node.children:
                        if sibling == child:
                            break
                        prev_siblings.append(sibling.type)

                    # Only accept if there's a type specifier before this identifier
                    type_specifiers = {
                        "primitive_type",
                        "qualified_identifier",
                        "type_identifier",
                        "placeholder_type_specifier",
                        "template_type",
                    }
                    if any(spec in prev_siblings for spec in type_specifiers):
                        text = self.get_text_from_node(child, content)
                        if self._is_valid_variable_name(text):
                            names.append((text, child.start_byte))

        elif decl_node.type == "field_declaration":
            # Pattern for class member variables
            for child in decl_node.children:
                if child.type == "field_identifier":
                    text = self.get_text_from_node(child, content)
                    if self._is_valid_variable_name(text):
                        names.append((text, child.start_byte))

        elif decl_node.type == "parameter_declaration":
            # Pattern for function parameters
            for child in decl_node.children:
                if child.type == "identifier":
                    text = self.get_text_from_node(child, content)
                    if self._is_valid_variable_name(text):
                        names.append((text, child.start_byte))

        return names

    def _is_valid_variable_name(self, name: str) -> bool:
        """Check if name is a valid variable name (not a type or parsing artifact)."""
        # Basic identifier validation
        if not name or len(name) < 2:
            return False

        # Must be valid C++ identifier characters only
        if not all(c.isalnum() or c == "_" for c in name):
            return False

        # Must not start with digit
        if name[0].isdigit():
            return False

        # Skip type names
        if self._is_type_name(name):
            return False

        # Skip obvious keywords and macros
        keywords = {
            "const",
            "auto",
            "static",
            "extern",
            "register",
            "volatile",
            "mutable",
            "public",
            "private",
            "protected",
            "virtual",
            "inline",
            "explicit",
            "namespace",
            "class",
            "struct",
            "union",
            "enum",
            "typedef",
            "using",
            "template",
            "typename",
            "operator",
            "friend",
            "this",
            "nullptr",
        }
        if name in keywords:
            return False

        return True

    def _is_type_name(self, name: str) -> bool:
        """Wrapper delegating to shared helper in ASTRule."""
        return self.is_type_name(name)

    def _is_template_parameter(self, param_node: Any) -> bool:
        """Check if a parameter_declaration is inside a template parameter list.
        
        Template parameters (both type and non-type) follow type naming conventions
        (PascalCase), not variable naming conventions (snake_case).
        
        Example: template <typename ValueType, std::size_t Index>
        Both ValueType and Index should use PascalCase.
        """
        if param_node.type != "parameter_declaration":
            return False
        current = param_node.parent
        while current:
            if current.type == "template_parameter_list":
                return True
            # Stop searching if we reach a function or class boundary
            if current.type in ["function_definition", "function_declaration", 
                               "class_specifier", "struct_specifier"]:
                return False
            current = current.parent
        return False

    def _should_skip_variable(self, var_name: str) -> bool:
        """Check if variable should be skipped from naming checks."""
        # Skip single letter variables (often used in loops)
        if len(var_name) == 1:
            return True

        # Skip common abbreviations
        if var_name in ["i", "j", "k", "x", "y", "z", "id", "fd"]:
            return True

        # Skip constants with k prefix (kCamelCase is valid constant style)
        if (
            var_name.startswith("k")
            and len(var_name) > 1
            and var_name[1].isupper()
        ):
            return True

        # Skip ML framework conventions (PyTorch, NumPy, etc.)
        # These are standard parameter names in ML libraries that should be preserved
        ml_conventions = {
            "dtype",   # Data type parameter (PyTorch, NumPy)
            "device",  # Device parameter (PyTorch)
            "ScalarType",  # Scalar type parameter (PyTorch)
        }
        if var_name in ml_conventions:
            return True

        return False

    def _is_valid_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention."""
        if not name:
            return False

        # Should be lowercase with underscores
        if not name.islower():
            return False

        # Should only contain alphanumeric and underscores
        if not name.replace("_", "").isalnum():
            return False

        # Whitelist of valid single-word identifiers that happen to contain
        # common suffixes but are not compound words
        valid_single_words = {
            "counter",
            "pointer",
            "iterator",
            "register",
            "buffer",
            "container",
            "adapter",
            "manager",
            "handler",
            "formatter",
            "multiplier",
            "divider",
            "remainder",
        }
        if name in valid_single_words:
            return True

        # For compound words (common patterns that suggest multiple words),
        # require underscores for readability
        import re

        # Check for common compound word patterns that should be separated.
        # Use word boundaries to avoid matching substrings within valid words.
        # These patterns look for distinct word combinations.
        compound_patterns = [
            # Pattern: <prefix><suffix> where both parts are common words
            # e.g., userdata, maxvalue, totalcount, countitems, datalist
            r"^(user|max|min|avg|sum|total|current|next|prev|first|last|count|data|info|size|value|name|type|list|item|file|path|num|get|set)(data|info|count|size|value|name|type|list|items|item|file|path|list|user|result)$",
            # Pattern: Common prefix + type/name/file/path suffixes
            # e.g., typename, filename, filepath
            r"^(data|info|count|size|value|name|type|list|item|file|path)(type|name|file|path|size|count|list)$",
        ]

        for pattern in compound_patterns:
            if re.match(pattern, name):
                return False  # Found compound pattern without underscores

        return True

    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        # Insert underscore before uppercase letters (except first)
        result = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return result

    def autofix(
        self,
        file_path: str,
        content: str,
        tree: Any,
        config: Any,
        issues: List[LintIssue],
    ) -> AutofixResult:
        """Automatically fix variable naming issues."""
        if not issues:
            return AutofixResult(success=False, message="No issues to fix")

        lines = content.split("\n")
        fixes_applied = 0

        # Process each issue
        for issue in issues:
            # Extract the variable name from the message
            match = re.search(
                r"Variable '([^']+)' should use snake_case", issue.message
            )
            if not match:
                continue

            old_name = match.group(1)
            new_name = self._to_snake_case(old_name)

            # Replace the variable name in the specific line
            line_idx = issue.line_number - 1
            if 0 <= line_idx < len(lines):
                # Use word boundaries to avoid partial matches
                pattern = r"\b" + re.escape(old_name) + r"\b"
                if re.search(pattern, lines[line_idx]):
                    lines[line_idx] = re.sub(pattern, new_name, lines[line_idx])
                    fixes_applied += 1

        if fixes_applied > 0:
            new_content = "\n".join(lines)
            return AutofixResult(
                success=True,
                new_content=new_content,
                message=f"Fixed {fixes_applied} variable naming issues to snake_case",
                issues_fixed=fixes_applied,
            )

        return AutofixResult(
            success=False, message="No variable names could be fixed"
        )


class NamingClassCaseRule(ASTRule):
    """Rule to enforce CamelCase for class names."""

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find class/struct/enum declarations
        class_nodes = self.find_nodes_by_types(
            tree, ["class_specifier", "struct_specifier", "enum_specifier"]
        )

        for class_node in class_nodes:
            class_name = self._get_class_name(class_node, content)
            node_type = class_node.type
            if (
                class_name
                and not self._should_skip_class(class_name, node_type)
                and not self._is_valid_camelcase(class_name)
            ):
                line_num = self.get_line_from_byte(
                    class_node.start_byte, content
                )
                if self.should_skip_line(self.get_line(content, line_num), str(self.rule_id)) or self.should_skip_next_line(content, line_num)[0]:
                    continue
                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=1,
                    message=f"{self._get_node_type(node_type)} '{class_name}' should use CamelCase (e.g., 'MyClass')",
                    suggested_fix=self._to_camelcase(class_name),
                )

        return self.issues

    def _get_node_type(self, node_type: str) -> str:
        """Get the node type in a human readable format."""
        if node_type == "class_specifier":
            return "Class"
        elif node_type == "struct_specifier":
            return "Struct"
        elif node_type == "enum_specifier":
            return "Enum"
        return node_type

    def _get_class_name(self, class_node: Any, content: str) -> str:
        """Extract class name from class node."""
        for child in class_node.children:
            if child.type == "type_identifier":
                return self.get_text_from_node(child, content)
        return ""

    def _should_skip_class(self, class_name: str, node_type: str) -> bool:
        """Check if class should be skipped from naming checks."""
        # Skip system types and POSIX types
        system_types = {
            "sockaddr",
            "sockaddr_in",
            "sockaddr_un",
            "in_addr",
            "hostent",
            "servent",
            "protoent",
            "stat",
            "dirent",
            "FILE",
            "DIR",
            "pthread_t",
            "pthread_mutex_t",
            "pthread_cond_t",
            "sigaction",
            "sigset_t",
            "timespec",
            "timeval",
            "fd_set",
            "pollfd",
            "epoll_event",
        }

        # Skip if it's a known system type
        if class_name in system_types:
            return True

        # Skip template parameter types (single uppercase letters)
        if len(class_name) == 1 and class_name.isupper():
            return True

        return False

    def _is_valid_camelcase(self, name: str) -> bool:
        """Check if name follows CamelCase convention."""
        if not name:
            return False

        # Should start with capital letter (PascalCase)
        if not name[0].isupper():
            return False

        # Should not have underscores
        if "_" in name.strip("_"):
            return False

        # Should not be all uppercase (that's not CamelCase)
        if name.isupper():
            return False

        # Should not be all lowercase (that's not CamelCase)
        if name.islower():
            return False

        # Must contain at least one lowercase letter to be proper CamelCase
        if not any(c.islower() for c in name):
            return False

        return True

    def _to_camelcase(self, name: str) -> str:
        """Convert to CamelCase."""
        if "_" in name:
            parts = name.split("_")
            return "".join(part.capitalize() for part in parts if part)
        else:
            return name.capitalize()


# Additional naming rule implementations
class NamingFunctionVerbRule(ASTRule):
    """Rule to enforce that functions start with verbs.

    Functions should start with action verbs to clearly indicate their purpose.
    Common verbs: Get, Set, Create, Update, Delete, Process, Handle, etc.
    """

    # Common function verb prefixes used in the codebase
    VALID_VERB_PREFIXES = {
        "Get",
        "Set",
        "Create",
        "Update",
        "Delete",
        "Remove",
        "Add",
        "Insert",
        "Process",
        "Handle",
        "Execute",
        "Run",
        "Start",
        "Stop",
        "Initialize",
        "Init",
        "Setup",
        "Cleanup",
        "Reset",
        "Clear",
        "Parse",
        "Format",
        "Convert",
        "Transform",
        "Generate",
        "Build",
        "Make",
        "Calculate",
        "Compute",
        "Find",
        "Search",
        "Filter",
        "Sort",
        "Compare",
        "Check",
        "Validate",
        "Verify",
        "Test",
        "Is",
        "Has",
        "Can",
        "Should",
        "Will",
        "Load",
        "Save",
        "Read",
        "Write",
        "Open",
        "Close",
        "Connect",
        "Disconnect",
        "Send",
        "Receive",
        "Emit",
        "Listen",
        "Watch",
        "Monitor",
        "Track",
        "Register",
        "Unregister",
        "Subscribe",
        "Unsubscribe",
        "Notify",
        "Trigger",
        "Fire",
        "Launch",
        "Invoke",
        "Call",
        "Apply",
        "Execute",
    }

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if self.has_file_level_disable(content, str(self.rule_id)):
            return self.issues

        # Find all function declarations/definitions
        function_nodes = self.find_nodes_by_types(
            tree, ["function_declaration", "function_definition"]
        )

        for func_node in function_nodes:
            self._check_function_verb(func_node, content)

        return self.issues

    def _check_function_verb(self, func_node: Any, content: str) -> None:
        """Check if function name starts with a verb."""
        try:
            func_name = self._get_function_name(func_node, content)

            if not func_name or self._should_skip_function(func_name):
                return

            if not self._starts_with_verb(func_name):
                line_num = func_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    return

                suggestion = self._suggest_verb_name(func_name)
                issue = LintIssue(
                    rule_id=self.rule_id,
                    file_path=self.current_file,
                    line_number=line_num,
                    column=func_node.start_point[1] + 1,
                    message=f"Function '{func_name}' should start with a verb (e.g., {suggestion})",
                    suggestion=f"Consider renaming to {suggestion} or similar verb-based name",
                )
                self.issues.append(issue)

        except Exception:
            # Skip on parsing errors
            pass

    def _get_function_name(self, func_node: Any, content: str) -> str:
        """Delegate to shared helper in ASTRule."""
        return self.extract_function_name(func_node, content)

    def _should_skip_function(self, func_name: str) -> bool:
        """Check if function should be skipped from verb checking."""
        # Skip unknown (parse failure)
        if func_name == "unknown":
            return True

        # Skip constructors and destructors
        if func_name.startswith("~") or func_name[0].isupper():
            return True

        # Skip special functions
        if func_name in ["main", "parse", "format"]:
            return True

        # Skip single letter or very short names
        if len(func_name) <= 2:
            return True

        return False

    def _starts_with_verb(self, func_name: str) -> bool:
        """Check if function name starts with a recognized verb."""
        # Check if any verb prefix matches
        for verb in self.VALID_VERB_PREFIXES:
            if func_name.startswith(verb):
                # Make sure it's not just a partial match
                if (
                    len(func_name) == len(verb)
                    or func_name[len(verb)].isupper()
                ):
                    return True

        return False

    def _suggest_verb_name(self, func_name: str) -> str:
        """Suggest a verb-based name for the function."""
        name_lower = func_name.lower()

        # Common patterns and suggestions
        if (
            "size" in name_lower
            or "length" in name_lower
            or "count" in name_lower
        ):
            return f"Get{func_name}"
        elif "empty" in name_lower or "valid" in name_lower:
            return f"Is{func_name}"
        elif "status" in name_lower or "state" in name_lower:
            return f"Get{func_name}"
        elif "error" in name_lower or "exception" in name_lower:
            return f"Handle{func_name}"
        else:
            return f"Process{func_name}"


class NamingConstantCaseRule(ASTRule):
    """Rule to enforce kPascalCase for constants.

    Constants should use kPascalCase naming (e.g., kMaxSize, kDefaultValue).
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Check for file-level disable directive
        if self.has_file_level_disable(content, str(self.rule_id)):
            return self.issues

        # Find constant declarations
        const_nodes = self._find_constant_declarations(tree, content)

        for const_node, const_name in const_nodes:
            if not self._is_valid_k_pascal_case(const_name):
                line_num = const_node.start_point[0] + 1
                if self.should_skip_line(
                    self.get_line(content, line_num), str(self.rule_id)
                ):
                    continue

                suggestion = self._to_k_pascal_case(const_name)
                self.add_issue(
                    file_path=file_path,
                    line_number=line_num,
                    column=const_node.start_point[1] + 1,
                    message=f"Constant '{const_name}' should use kPascalCase (e.g., '{suggestion}')",
                    suggested_fix=f"Rename to {suggestion}",
                )

        return self.issues

    def _find_constant_declarations(
        self, tree: Any, content: str
    ) -> List[tuple]:
        """Find constant declarations in the AST.

        We only consider true constants:
        - Global/namespace scope constexpr variables with initialization
        - Static const class members with initialization
        - NOT local variables in functions (even if constexpr)
        - NOT function parameters
        - NOT function return types
        """
        constants = []

        # Find declarations marked with const/constexpr
        declaration_nodes = self.find_nodes_by_types(
            tree, ["declaration", "field_declaration"]
        )

        for decl_node in declaration_nodes:
            # Skip if this is inside a function body (local variable)
            if self._is_inside_function_body(decl_node):
                continue

            # Skip if this looks like a function declaration (has parameter_list)
            if self._is_function_declaration(decl_node):
                continue

            decl_text = self.get_text_from_node(decl_node, content)

            # Must have const or constexpr keyword
            has_const = "const " in decl_text or "constexpr " in decl_text
            if not has_const:
                continue

            # Must have initialization (=)
            if "=" not in decl_text:
                continue

            # Extract the variable name being declared
            var_name = self._extract_constant_name(decl_node, content)
            if var_name and self._looks_like_constant(var_name):
                # Find the node containing this identifier for position reporting
                id_node = self._find_identifier_node(decl_node, var_name, content)
                if id_node:
                    constants.append((id_node, var_name))

        return constants

    def _is_inside_function_body(self, node: Any) -> bool:
        """Check if a node is inside a function body or lambda expression.

        This includes:
        - Function definitions
        - Lambda expressions
        - Methods
        - Constructors
        """
        current = node.parent
        while current:
            if current.type == "compound_statement":
                # Check if parent is a function or lambda
                parent = current.parent
                if parent and parent.type in ["function_definition", "lambda_expression"]:
                    return True
            # Also check for lambda_expression directly
            if current.type == "lambda_expression":
                return True
            current = current.parent
        return False

    def _is_function_declaration(self, node: Any) -> bool:
        """Check if a declaration node is actually a function declaration."""
        # Look for parameter_list child, which indicates a function
        for child in node.children:
            if child.type in ["function_declarator", "parameter_list"]:
                return True
            # Recursively check declarator children
            if child.type in ["init_declarator", "declarator"]:
                for subchild in child.children:
                    if subchild.type in ["function_declarator", "parameter_list"]:
                        return True
        return False

    def _extract_constant_name(self, decl_node: Any, content: str) -> str:
        """Extract the variable name from a constant declaration.

        This is more precise than _extract_identifier - it looks for the
        actual variable being declared, not just any identifier.
        """
        # Look for init_declarator pattern: type identifier = value
        for child in decl_node.children:
            if child.type == "init_declarator":
                # The first child should be the declarator/identifier
                if child.children:
                    first_child = child.children[0]
                    if first_child.type == "identifier":
                        return self.get_text_from_node(first_child, content)
            elif child.type == "field_identifier":
                # For field declarations
                return self.get_text_from_node(child, content)

        return ""

    def _find_identifier_node(self, decl_node: Any, name: str, content: str) -> Any:
        """Find the AST node for a specific identifier name."""
        for child in decl_node.children:
            if child.type == "init_declarator":
                if child.children and child.children[0].type == "identifier":
                    if self.get_text_from_node(child.children[0], content) == name:
                        return child.children[0]
            elif child.type == "field_identifier":
                if self.get_text_from_node(child, content) == name:
                    return child
        return decl_node

    def _contains_identifier(self, node: Any) -> bool:
        """Check if node contains an identifier."""
        if node.type in ["identifier", "field_identifier"]:
            return True
        for child in node.children:
            if self._contains_identifier(child):
                return True
        return False

    def _extract_identifier(self, node: Any, content: str) -> str:
        """Extract identifier from node."""
        if node.type in ["identifier", "field_identifier"]:
            return self.get_text_from_node(node, content)
        for child in node.children:
            result = self._extract_identifier(child, content)
            if result:
                return result
        return ""

    def _looks_like_constant(self, name: str) -> bool:
        """Check if name looks like a constant."""
        # Skip keywords
        if name in ["const", "constexpr", "static", "inline"]:
            return False
        # All other identifiers in const/constexpr declarations are constants
        return True

    def _is_valid_k_pascal_case(self, name: str) -> bool:
        """Check if name follows kPascalCase convention."""
        if not name.startswith("k"):
            return False
        if len(name) < 2:
            return False
        if not name[1].isupper():
            return False
        if "_" in name:
            return False
        return True

    def _to_k_pascal_case(self, name: str) -> str:
        """Convert name to kPascalCase."""
        if name.startswith("k"):
            return name  # Already starts with k

        name = name.lstrip("k").lstrip("_")
        if "_" in name:
            parts = name.lower().split("_")
            pascal = "".join(part.capitalize() for part in parts if part)
        else:
            pascal = name.capitalize()
        return f"k{pascal}"


# === Enhanced Naming Convention Rules ===


class NamingEnumCaseRule(ASTRule):
    """Rule to enforce naming conventions for enums.

    - enum class: PascalCase (e.g., SequenceStatus)
    - C-style enum: snake_case (e.g., sequence_status)
    """

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find enum declarations
        enum_nodes = self.find_nodes_by_types(tree, ["enum_specifier"])

        for enum_node in enum_nodes:
            enum_info = self._get_enum_info(enum_node, content)
            if enum_info:
                enum_name, is_class, position = enum_info
                if not self._is_valid_enum_name(enum_name, is_class):
                    line_num = self.get_line_from_byte(position, content)
                    expected_name = self._get_expected_enum_name(
                        enum_name, is_class
                    )
                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=1,
                        message=f"Enum '{enum_name}' should use {'PascalCase' if is_class else 'snake_case'} (e.g., '{expected_name}')",
                        suggested_fix=expected_name,
                    )

        return self.issues

    def _get_enum_info(self, enum_node: Any, content: str) -> Optional[tuple]:
        """Extract enum information: (name, is_class, position)."""
        is_class = False
        enum_name = None
        position = enum_node.start_byte

        # Check if it's an enum class
        for child in enum_node.children:
            if child.type == "class":
                is_class = True
            elif child.type == "type_identifier":
                enum_name = self.get_text_from_node(child, content)
                position = child.start_byte

        return (enum_name, is_class, position) if enum_name else None

    def _is_valid_enum_name(self, name: str, is_class: bool) -> bool:
        """Check if enum name follows the correct convention."""
        if is_class:
            # Should start with capital letter
            if not name[0].isupper():
                return False
            # Should not have underscores
            if "_" in name:
                return False
            # Should not be all uppercase
            if name.isupper():
                return False
            # Should not be all lowercase
            if name.islower():
                return False
            # Must contain at least one lowercase letter to be proper PascalCase
            if not any(c.islower() for c in name):
                return False
            return True
        else:
            # C-style enum should be snake_case
            return name.islower() and name.replace("_", "").isalnum()

    def _get_expected_enum_name(self, name: str, is_class: bool) -> str:
        """Get expected enum name based on convention."""
        if is_class:
            # Convert to PascalCase
            # If already valid PascalCase, return as is
            if (name and name[0].isupper() and "_" not in name and 
                not name.isupper() and not name.islower() and 
                any(c.islower() for c in name)):
                return name
            return self._to_pascal_case(name)
        else:
            # Convert to snake_case
            return self._to_snake_case(name)

    def _to_pascal_case(self, name: str) -> str:
        """Convert to PascalCase."""
        name = name.lstrip("k").lstrip("_")
        if "_" in name:
            parts = name.lower().split("_")
            pascal = "".join(part.capitalize() for part in parts if part)
        else:
            # If all uppercase, capitalize properly
            if name.isupper():
                pascal = name.capitalize()
            # If all lowercase, capitalize
            elif name.islower():
                pascal = name.capitalize()
            else:
                # Already mixed case, keep as is
                pascal = name
        return pascal

    def _to_snake_case(self, name: str) -> str:
        """Convert to snake_case."""
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class NamingEnumValueCaseRule(ASTRule):
    """Rule to enforce naming conventions for enum values.

    - enum class values: kPascalCase (e.g., kWaiting, kRunning)
    """

    def __init__(self, rule_id: RuleId, severity: Severity):
        super().__init__(rule_id, severity)
        self.supports_autofix = True

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find enum declarations
        enum_nodes = self.find_nodes_by_types(tree, ["enum_specifier"])

        for enum_node in enum_nodes:
            is_enum_class = self._is_enum_class(enum_node)
            enum_values = self._get_enum_values(enum_node, content)

            for value_name, position in enum_values:
                is_valid = False
                expected_format = ""

                if is_enum_class:
                    # enum class values should be kPascalCase
                    is_valid = self._is_k_pascal_case(value_name)
                    expected_format = "kPascalCase (e.g., kRunning, kStopped)"
                else:
                    # C-style enum values should be UPPER_CASE
                    is_valid = self._is_upper_case(value_name)
                    expected_format = "UPPER_CASE (e.g., VALUE_ONE, MAX_SIZE)"

                if not is_valid:
                    line_num = self.get_line_from_byte(position, content)
                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=1,
                        message=f"Enum value '{value_name}' should use {expected_format}",
                        suggested_fix=None,
                    )

        return self.issues

    def _is_enum_class(self, enum_node: Any) -> bool:
        """Check if this is an enum class."""
        for child in enum_node.children:
            if child.type == "class":
                return True
        return False

    def _get_enum_values(self, enum_node: Any, content: str) -> List[tuple]:
        """Get enum values and their positions."""
        values = []
        list_node = next(
            (c for c in enum_node.children if c.type == "enumerator_list"), None
        )
        if list_node:
            for enumerator in list_node.children:
                if enumerator.type == "enumerator":
                    id_node = next(
                        (
                            c
                            for c in enumerator.children
                            if c.type == "identifier"
                        ),
                        None,
                    )
                    if id_node:
                        values.append(
                            (
                                self.get_text_from_node(id_node, content),
                                id_node.start_byte,
                            )
                        )
        return values

    def _is_k_pascal_case(self, name: str) -> bool:
        """Check if name is in kPascalCase."""
        if not name:
            return False
        # Length check
        if len(name) < 2:
            return False
        # First character must be 'k'
        if not name.startswith("k"):
            return False
        # Second character must be uppercase
        if not name[1].isupper():
            return False
        # No underscores allowed
        return "_" not in name

    def _is_upper_case(self, name: str) -> bool:
        """Check if name is in UPPER_CASE."""
        if not name:
            return False
        # All alphabetic characters must be uppercase
        # Numbers and underscores are allowed
        for c in name:
            if c.isalpha() and not c.isupper():
                return False
        return True

    def _is_valid_k_pascal_case(self, name: str) -> bool:
        """Check if name follows kPascalCase convention."""
        if not name.startswith("k"):
            return False
        if len(name) < 2:
            return False
        if not name[1].isupper():
            return False
        if "_" in name:
            return False
        return True

    def _to_k_pascal_case(self, name: str) -> str:
        """Convert to kPascalCase."""
        if name.startswith("k"):
            return name
        name = name.lstrip("k").lstrip("_")
        if "_" in name:
            parts = name.split("_")
            pascal = "".join(part.capitalize() for part in parts if part)
        else:
            pascal = name.capitalize()
        return f"k{pascal}"

    def autofix(
        self,
        file_path: str,
        content: str,
        tree: Any,
        config: Any,
        issues: List[LintIssue],
    ) -> AutofixResult:
        """Automatically fix enum value naming issues."""
        if not issues:
            return AutofixResult(success=False, message="No issues to fix")

        lines = content.split("\n")
        fixes_applied = 0

        # Process each issue
        for issue in issues:
            # Extract the enum value name from the message
            match = re.search(
                r"Enum value '([^']+)' should use (?:kPascalCase|UPPER_CASE)",
                issue.message,
            )
            if not match:
                continue

            old_name = match.group(1)
            new_name = self._to_k_pascal_case(old_name)
            line_idx = issue.line_number - 1
            if 0 <= line_idx < len(lines):
                # Use word boundaries to avoid partial matches
                pattern = r"\b" + re.escape(old_name) + r"\b"
                if re.search(pattern, lines[line_idx]):
                    lines[line_idx] = re.sub(pattern, new_name, lines[line_idx])
                    fixes_applied += 1

        if fixes_applied > 0:
            new_content = "\n".join(lines)
            return AutofixResult(
                success=True,
                new_content=new_content,
                message=f"Fixed {fixes_applied} enum value naming issues",
                issues_fixed=fixes_applied,
            )

        return AutofixResult(
            success=False, message="No enum value names could be fixed"
        )

class NamingMemberCaseRule(ASTRule):
    """Rule to enforce snake_case_ (with trailing underscore) for member variables."""

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find class/struct declarations
        class_nodes = self.find_nodes_by_types(
            tree, ["class_specifier", "struct_specifier"]
        )

        for class_node in class_nodes:
            members = self._find_member_variables(class_node, content)
            for member_name, position, is_private_or_protected in members:
                if is_private_or_protected and not self._is_valid_member_name(
                    member_name
                ):
                    line_num = self.get_line_from_byte(position, content)
                    expected_name = self._get_expected_member_name(member_name)
                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=1,
                        message=f"Member variable '{member_name}' should use snake_case_ with trailing underscore (e.g., '{expected_name}')",
                        suggested_fix=expected_name,
                    )

        return self.issues

    def _find_member_variables(
        self, class_node: Any, content: str
    ) -> List[tuple]:
        """Find member variables in class/struct."""
        members = []
        current_access = "private"  # default for class

        # Check if this is a struct (default public) or class (default private)
        if class_node.type == "struct_specifier":
            current_access = "public"

        for child in class_node.children:
            if child.type == "field_declaration_list":
                # Process the field declaration list
                for field_child in child.children:
                    if field_child.type == "access_specifier":
                        access_text = self.get_text_from_node(
                            field_child, content
                        )
                        if "public" in access_text:
                            current_access = "public"
                        elif "protected" in access_text:
                            current_access = "protected"
                        elif "private" in access_text:
                            current_access = "private"
                    elif field_child.type == "field_declaration":
                        # Skip static constexpr constants - they use kPascalCase, not snake_case_
                        if self._is_static_constexpr_constant(field_child, content):
                            continue

                        # Extract variable names from field declaration
                        var_names = self._extract_variable_names_from_field(
                            field_child, content
                        )
                        for var_name, position in var_names:
                            is_private_or_protected = current_access in [
                                "private",
                                "protected",
                            ]
                            members.append(
                                (var_name, position, is_private_or_protected)
                            )

        return members

    def _extract_variable_names_from_field(
        self, field_node: Any, content: str
    ) -> List[tuple]:
        """Extract variable names from field_declaration node.

        This method must distinguish between:
        - Member variables: Type variable_name_;
        - Method declarations: Type MethodName(...);

        Methods have function_declarator nodes, variables don't.
        """
        names = []

        # First check if this is a method declaration (has function_declarator)
        if self._is_method_declaration(field_node):
            return names  # Skip methods entirely

        def find_identifiers(node):
            if node.type == "field_identifier":
                text = self.get_text_from_node(node, content)
                # Skip keywords but accept all field identifiers
                if not self._is_keyword(text):
                    names.append((text, node.start_byte))

            for child in node.children:
                find_identifiers(child)

        find_identifiers(field_node)
        return names

    def _is_method_declaration(self, field_node: Any) -> bool:
        """Check if a field_declaration is actually a method declaration.

        Methods have function_declarator or parameter_list nodes in their AST.
        Variables do not.
        """
        def has_function_declarator(node):
            if node.type in ["function_declarator", "parameter_list"]:
                return True
            for child in node.children:
                if has_function_declarator(child):
                    return True
            return False

        return has_function_declarator(field_node)

    def _is_static_constexpr_constant(self, field_node: Any, content: str) -> bool:
        """Check if a field_declaration is a static constexpr constant.

        Static constexpr constants should use kPascalCase naming (enforced by
        naming-constant-case rule), not snake_case_ with trailing underscore
        (which is for instance member variables).

        Examples:
        - static constexpr float kMaxValue = 1.0f;  ✅ Use kPascalCase
        - Type member_variable_;                    ✅ Use snake_case_
        - static Type static_member_;               ✅ Use snake_case_ (mutable)
        """
        decl_text = self.get_text_from_node(field_node, content)

        # Must have both 'static' and 'constexpr' keywords
        has_static = "static " in decl_text or decl_text.startswith("static ")
        has_constexpr = "constexpr " in decl_text

        return has_static and has_constexpr

    def _is_keyword(self, text: str) -> bool:
        """Wrapper delegating to shared helper in ASTRule."""
        return self.is_keyword(text)

    def _is_valid_member_name(self, name: str) -> bool:
        """Check if member name follows snake_case_ convention."""
        if not name.endswith("_"):
            return False
        base_name = name[:-1]  # Remove trailing underscore
        return base_name.islower() and base_name.replace("_", "").isalnum()

    def _get_expected_member_name(self, name: str) -> str:
        """Get expected member name with trailing underscore."""
        if name.endswith("_"):
            return name  # Already has underscore

        # Convert to snake_case and add underscore
        snake_case = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
        return snake_case + "_"


class NamingHungarianNotationRule(ASTRule):
    """Rule to detect and forbid Hungarian notation."""

    def __init__(self, rule_id: RuleId, severity: Severity):
        super().__init__(rule_id, severity)
        self.supports_autofix = True

    # Common Hungarian notation prefixes
    HUNGARIAN_PREFIXES = {
        "str",
        "sz",
        "psz",  # String prefixes
        "int",
        "n",
        "i",  # Integer prefixes
        "bool",
        "b",
        "f",  # Boolean prefixes
        "ptr",
        "p",  # Pointer prefixes
        "arr",
        "a",  # Array prefixes
        "dw",
        "ul",
        "l",  # Other numeric prefixes
        "ch",
        "c",  # Character prefixes
        "fn",
        "pfn",  # Function prefixes
        "h",
        "hnd",  # Handle prefixes
        "lp",
        "lpsz",  # Long pointer prefixes
        "cb",
        "cch",  # Count prefixes
        "rgb",
        "rgn",  # Array/region prefixes
        "obj",
        "o",  # Object prefixes
        "cls",
        "class",  # Class prefixes
    }

    HUNGARIAN_PREFIXES_TO_SKIP = {
        'O_RDWR',
        'O_RDONLY',
        'O_WRONLY',
        'O_NONBLOCK',
        'O_APPEND',
        'O_CREAT',
        'O_TRUNC',
        'O_EXCL',
        "PYBIND11_",
        "ASSERT_VALID_ARGUMENTS",
        "ASSERT_VALID_RUNTIME",
        "AF_INET",
        "INET_ADDRSTRLEN",
        "BFloat16"
    }

    def check(
        self, file_path: str, content: str, tree: Any, config: Any
    ) -> List[LintIssue]:
        self.issues = []

        # Find variable declarations
        declaration_nodes = self.find_nodes_by_types(
            tree, ["declaration", "parameter_declaration", "field_declaration"]
        )

        for decl_node in declaration_nodes:
            var_names = self._extract_variable_names(decl_node, content)
            for var_name, position in var_names:
                if self._is_hungarian_notation(var_name):
                    line_num = self.get_line_from_byte(position, content)
                    suggested_name = self._remove_hungarian_prefix(var_name)
                    self.add_issue(
                        file_path=file_path,
                        line_number=line_num,
                        column=1,
                        message=f"Variable '{var_name}' uses Hungarian notation, which is forbidden, Use '{suggested_name}' instead",
                        suggested_fix=suggested_name,
                    )

        return self.issues

    def _extract_variable_names(
        self, decl_node: Any, content: str
    ) -> List[tuple]:
        """Extract variable names from declaration node."""
        names = []

        def find_identifiers(node):
            if node.type in ["identifier", "field_identifier"]:
                text = self.get_text_from_node(node, content)
                # Skip type names and keywords
                if not self._is_type_name(text):
                    names.append((text, node.start_byte))

            for child in node.children:
                find_identifiers(child)

        find_identifiers(decl_node)
        return names

    def _is_type_name(self, name: str) -> bool:
        """Wrapper delegating to shared helper in ASTRule."""
        return self.is_type_name(name)

    def _is_hungarian_notation(self, name: str) -> bool:
        """Check if name uses Hungarian notation."""
        # Handle member variable prefixes like m_ or g_
        clean_name = name
        if name.startswith("m_") or name.startswith("g_"):
            clean_name = name[2:]

        for prefix in self.HUNGARIAN_PREFIXES_TO_SKIP:
            if clean_name.startswith(prefix):
                return False

        # Check for common prefixes
        for prefix in self.HUNGARIAN_PREFIXES:
            if clean_name.lower().startswith(prefix.lower()):
                # Make sure it's followed by a capital letter or underscore
                if len(clean_name) > len(prefix):
                    next_char = clean_name[len(prefix)]
                    if next_char.isupper() or next_char == "_":
                        return True

        # Check for patterns like intCount, strName, etc.
        hungarian_pattern = re.compile(
            r"^(str|int|bool|ptr|arr|dw|ul|ch|fn|obj|cls)[A-Z]"
        )
        return bool(hungarian_pattern.match(clean_name))

    def _remove_hungarian_prefix(self, name: str) -> str:
        """Remove Hungarian notation prefix."""
        for prefix in sorted(self.HUNGARIAN_PREFIXES, key=len, reverse=True):
            if name.lower().startswith(prefix.lower()):
                if len(name) > len(prefix):
                    remainder = name[len(prefix) :]
                    if remainder[0].isupper() or remainder[0] == "_":
                        # Convert to snake_case
                        clean_name = remainder.lstrip("_")
                        return re.sub(
                            r"(?<!^)(?=[A-Z])", "_", clean_name
                        ).lower()

        # Fallback: just convert to snake_case
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def autofix(
        self,
        file_path: str,
        content: str,
        tree: Any,
        config: Any,
        issues: List[LintIssue],
    ) -> AutofixResult:
        """Automatically fix Hungarian notation issues."""
        if not issues:
            return AutofixResult(success=False, message="No issues to fix")

        lines = content.split("\n")
        fixes_applied = 0

        # Process each issue
        for issue in issues:
            # Extract the variable name from the message
            match = re.search(
                r"Variable '([^']+)' uses Hungarian notation", issue.message
            )
            if not match:
                continue

            old_name = match.group(1)
            new_name = self._remove_hungarian_prefix(old_name)

            # Replace the variable name in the specific line
            line_idx = issue.line_number - 1
            if 0 <= line_idx < len(lines):
                # Use word boundaries to avoid partial matches
                pattern = r"\b" + re.escape(old_name) + r"\b"
                if re.search(pattern, lines[line_idx]):
                    lines[line_idx] = re.sub(pattern, new_name, lines[line_idx])
                    fixes_applied += 1

        if fixes_applied > 0:
            new_content = "\n".join(lines)
            return AutofixResult(
                success=True,
                new_content=new_content,
                message=f"Fixed {fixes_applied} Hungarian notation issues",
                issues_fixed=fixes_applied,
            )

        return AutofixResult(
            success=False, message="No Hungarian notation could be fixed"
        )


# Rule registration has been moved to registry.py
# All rules are now registered centrally in RuleRegistry._load_all_rules()
