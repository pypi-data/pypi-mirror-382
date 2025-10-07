# Include Rules

Managing include directives properly is crucial for build performance and code organization. These rules enforce a consistent style for including headers.

## Include Order

<div class="rule-card">
<h3 class="rule-title">INCLUDE_ORDER_WRONG</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: INCLUDE_ORDER_WRONG</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Enforces a standard include order: C standard library, C++ standard library, third-party libraries, and finally project-specific headers. This improves readability and helps identify dependencies.
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
// Correct order: C std, C++ std, third-party, project

// C standard library
#include <cstddef>
#include <cstdio>

// C++ standard library
#include <iostream>
#include <string>
#include <vector>

// Third-party libraries
#include <gtest/gtest.h>
#include <boost/optional.hpp>

// Project headers
#include "niti/core/engine.h"
#include "niti/rules/rule.h"
```

</div>
<div class="code-bad">

```cpp
// Incorrect order

#include "niti/core/engine.h" // Project header first
#include <iostream>            // C++ std header
#include <gtest/gtest.h>       // Third-party header
#include <cstddef>             // C std header
#include "niti/rules/rule.h"    // Another project header
#include <string>              // Another C++ std header
```

</div>
</div>
</div>
</div>

## Local Include Style

<div class="rule-card">
<h3 class="rule-title">INCLUDE_ANGLE_BRACKET_FORBIDDEN</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: INCLUDE_ANGLE_BRACKET_FORBIDDEN</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Requires local project headers to be included with quotes (`""`) and external/system headers with angle brackets (`<>`). This clearly distinguishes between internal and external dependencies.
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
// System headers use angle brackets
#include <vector>
#include <string>

// Project-local headers use quotes
#include "my_app/my_class.h"
#include "utils/string_helpers.h"
```

</div>
<div class="code-bad">

```cpp
// Don't use angle brackets for local headers
#include <my_app/my_class.h> // Incorrect

// Don't use quotes for system headers
#include "vector" // Incorrect
```

</div>
</div>
</div>
</div>

## Precompiled Headers (PCH) [Make it a Plugin for Vajra]

<div class="rule-card">
<h3 class="rule-title">INCLUDE_MISSING_PCH</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: INCLUDE_MISSING_PCH</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Ensures that if a precompiled header is used in the project, it is the very first include in every source file to improve build times.
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
// PCH must be the first include
#include "framework/precompiled.h"

#include <iostream>
#include "my_app/my_class.h"

// ... rest of the file
```

</div>
<div class="code-bad">

```cpp
#include <iostream>
// PCH is not the first include
#include "framework/precompiled.h" // Incorrect

#include "my_app/my_class.h"

// ... rest of the file
```

</div>
</div>
</div>
</div>

## Summary

A clean include policy is a cornerstone of a healthy C++ project:

- **Order matters**: A consistent include order makes dependencies clear.
- **Quotes vs. Brackets**: Visually separate internal and external code.
- **PCH First**: Maximize build speed by including the precompiled header first.