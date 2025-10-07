# Niti: A Fast, Modern C++ Linter

Niti is a fast, modern, and lean linter for C++ designed to be simple, extensible, and easy to configure. It helps enforce coding standards and best practices in C++ projects.

## The Problem

Maintaining code quality and consistency across a large C++ codebase is challenging. Many existing linters are complex to configure, slow, or not easily extensible to enforce project-specific rules. Developers need a tool that is fast, integrates seamlessly into their workflow, and can be tailored to their unique needs.

## The Solution

Niti addresses these challenges by providing a simple, powerful, and extensible C++ linter written in Python. It uses the fast and accurate `tree-sitter` library for parsing C++ code and features a modular architecture that allows developers to easily create and share custom linting rules.

## Key Features

- **Fast and Modern:** Built on `tree-sitter` for high-performance and accurate C++ parsing.
- **Highly Extensible:** A modular rule system makes it easy to add custom rules for project-specific standards.
- **Simple Configuration:** Configure Niti with a straightforward `.nitirc` YAML file or command-line options.
- **Comprehensive Rule Set:** Comes with over 50 built-in rules covering safety, modern C++, naming conventions, and more.
- **Developer-Friendly Workflow:** Integrates smoothly with development tools and provides clear, actionable feedback.

## Quick Start

To get started with Niti:

```bash
# Install Niti from the project root
pip install -e .

# Lint a single file
niti path/to/file.cpp

# Lint a directory
niti path/to/cpp/project/

# Show help
niti --help
```

## Rule Suppression and Configuration

Niti provides flexible rule suppression mechanisms to handle legacy code, special cases, and configuration needs.

### Configuration-based Rule Disabling

Disable rules globally via configuration file (`.nitirc` or `niti.yaml`):

```yaml
rules:
  # Disable specific rules completely
  type-forbidden-int:
    enabled: false
  naming-variable-case:
    enabled: false
  
  # Change severity levels
  include-order-wrong:
    severity: warning  # Instead of error
```

### Comment-based Rule Suppression (NOLINT)

Niti supports flexible comment-based rule suppression using NOLINT directives.

#### Basic NOLINT Usage

**Disable all rules for a line:**
```cpp
int value = 42;  // NOLINT
int badVariableName = 10;  // NOLINT (legacy code - all rules disabled)
```

**Disable specific rules for a line:**
```cpp
int value = 42;  // NOLINT type-forbidden-int
int badName = 10;  // NOLINT naming-variable-case

// Multiple rules can be disabled with comma separation
int badValue = 99;  // NOLINT type-forbidden-int,naming-variable-case
```

**Disable rules for the next line:**
```cpp
// NOLINTNEXTLINE
int value = 42;  // All rules disabled for this line

// NOLINTNEXTLINE type-forbidden-int
int other = 24;  // Only type rule disabled for this line

// NOLINTNEXTLINE type-forbidden-int,naming-variable-case
int badValue = 99;  // Multiple rules disabled for this line
```

#### File-level Rule Disabling

Disable specific rules for an entire file:

```cpp
// NOLINT naming-variable-case
// NOLINT type-forbidden-int

#include <iostream>

class legacy_class {  // naming-variable-case disabled for entire file
public:
    int process_data(int input) {  // type-forbidden-int disabled for entire file
        int temp_value = input * 2;
        return temp_value;
    }
};
```

#### Advanced NOLINT Patterns

**Legacy code integration examples:**
```cpp
// Legacy API integration
class LegacyInterface {
public:
    // NOLINTNEXTLINE type-forbidden-int
    int* GetRawPointer() {
        return raw_data_;  // NOLINT type-forbidden-int
    }
    
    void ProcessData(int* data) {  // NOLINT type-forbidden-int
        int temp = *data;  // NOLINT type-forbidden-int
    }

private:
    int* raw_data_ = nullptr;  // NOLINT type-forbidden-int (C API requirement)
};
```

### Important NOLINT Guidelines

**Syntax Rules:**
- **Case Sensitive**: Only uppercase `NOLINT` and `NOLINTNEXTLINE` work
- **Rule Names**: Use kebab-case rule names (e.g., `type-forbidden-int`, `naming-variable-case`)
- **Comments Allowed**: Additional text after NOLINT is ignored: `// NOLINT (legacy code)`
- **Comma Separation**: Multiple rules: `// NOLINT rule-one,rule-two,rule-three`
- **No Spaces in Rule Lists**: Use `rule-one,rule-two` not `rule-one, rule-two`

**Scope and Precedence:**
- **NOLINT**: Affects only the specific line where the comment appears
- **NOLINTNEXTLINE**: Affects only the immediately following line
- **File-level disable**: Affects the entire file for specified rules
- **Configuration disable**: Affects all files globally for specified rules
- **Precedence**: Comment-based > File-level > Configuration-based

### Discovering Available Rules

Before disabling rules, discover what's available:

```bash
# See all available rules
niti --list-rules

# Run linter to see which rules are being triggered
niti --check your_project/

# Get detailed rule information
niti --check --verbose your_file.cpp
```

**Common Rule Names:**
- `type-forbidden-int` - Forbids use of raw int types
- `naming-variable-case` - Enforces variable naming conventions
- `naming-function-case` - Enforces function naming conventions
- `safety-raw-pointer-param` - Warns about raw pointer parameters
- `safety-unsafe-cast` - Warns about unsafe type casts
- `include-order-wrong` - Enforces include statement ordering
- `modern-missing-const` - Enforces const correctness
- `doc-function-missing` - Requires function documentation

### Troubleshooting Rule Suppression

**Common Issues and Solutions:**

1. **Rule name mismatch**: Ensure kebab-case rule names
   ```cpp
   // ❌ Wrong: camelCase or snake_case
   int value = 42;  // NOLINT typeForbiddenInt
   
   // ✅ Correct: kebab-case
   int value = 42;  // NOLINT type-forbidden-int
   ```

2. **Case sensitivity**: Only uppercase NOLINT works
   ```cpp
   // ❌ Wrong
   int value = 42;  // nolint type-forbidden-int
   
   // ✅ Correct
   int value = 42;  // NOLINT type-forbidden-int
   ```

3. **Spaces in rule lists**: No spaces between rules
   ```cpp
   // ❌ Wrong: spaces between rules
   int Bad_Name = 42;  // NOLINT type-forbidden-int, naming-variable-case
   
   // ✅ Correct: no spaces
   int Bad_Name = 42;  // NOLINT type-forbidden-int,naming-variable-case
   ```

```{toctree}
:maxdepth: 1
:caption: Table of Contents

self
rules/naming
rules/safety
rules/modern_cpp
rules/documentation
rules/code-quality
rules/class-organization
rules/class-traits
rules/file-organization
rules/headers
rules/includes
rules/logging
rules/namespace
```