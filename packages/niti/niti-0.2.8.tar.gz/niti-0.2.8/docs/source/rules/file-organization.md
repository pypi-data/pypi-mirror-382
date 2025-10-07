# File Organization Rules

A consistent file and directory structure is crucial for navigating a large codebase. These rules enforce conventions for file naming and location.

## Copyright Header

<div class="rule-card">
<h3 class="rule-title">FILE_HEADER_COPYRIGHT</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: FILE_HEADER_COPYRIGHT</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Ensures that every source and header file begins with a copyright notice and license information. This is important for legal compliance and clarifying code ownership.
</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect (Lint Error)</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// Copyright (C) 2025 My Awesome Company Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

// ... rest of file
```

</div>
<div class="code-bad">

```cpp
// No copyright notice at the top of the file.

#pragma once

// ... rest of file
```

</div>
</div>
</div>
</div>

<!-- ## Include Strategy

<div class="rule-card">
<h3 class="rule-title">FILE_INCLUDE_STRATEGY</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: FILE_INCLUDE_STRATEGY</span>
    <span class="severity-badge severity-warning">Warning</span>
</div>
<div class="rule-description">
Prefers forward declarations over full `#include` directives in header files whenever possible. This reduces compilation dependencies and can significantly speed up build times.
</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect (Lint Error)</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// In MyClass.h
#pragma once

// Forward-declare classes instead of including their headers
class UserSession;
class RequestContext;

class MyClass {
public:
    // Pointers and references to forward-declared types are fine
    void Process(UserSession* session, const RequestContext& context);
};
```

</div>
<div class="code-bad">

```cpp
// In MyClass.h
#pragma once

// Unnecessary includes increase coupling and compile times
#include "UserSession.h"
#include "RequestContext.h"

class MyClass {
public:
    void Process(UserSession* session, const RequestContext& context);
};
```

</div>
</div>
</div>
</div> -->

## File Naming Convention

<div class="rule-card">
<h3 class="rule-title">FILE_NAMING_CONVENTION</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: FILE_NAMING_CONVENTION</span>
    <span class="severity-badge severity-warning">Warning</span>
</div>
<div class="rule-description">
Enforces a consistent naming convention for files. Header and source files should use `PascalCase` and have matching names (e.g., `MyClass.h` and `MyClass.cpp`).
</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect (Lint Error)</div>
</div>
<div class="code-comparison">
<div class="code-good">

```
// Consistent PascalCase naming
src/core/DatabaseConnection.h
src/core/DatabaseConnection.cpp

src/utils/StringUtils.h
src/utils/StringUtils.cpp
```

</div>
<div class="code-bad">

```
// Inconsistent naming styles
src/core/database_connection.h // snake_case
src/core/DatabaseConnection.cpp

src/utils/string-utils.h // kebab-case
src/utils/StringUtils.cpp
```

</div>
</div>
</div>
</div>

## Summary

A well-organized file structure is a sign of a well-organized project:

- **Copyright First**: Ensure all files have proper legal notices.
<!-- - **Forward-Declare**: Reduce compile times by minimizing includes in headers. -->
- **Consistent Naming**: Make files easy to find and identify.