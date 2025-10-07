# Header File Rules

Header files are the public-facing contracts of your components. These rules ensure they are well-formed, protected against common issues, and contain necessary legal information.

## Pragma Once

<div class="rule-card">
<h3 class="rule-title">HEADER_PRAGMA_ONCE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: HEADER_PRAGMA_ONCE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Requires every header file to start with `#pragma once` to prevent multiple inclusions, which can lead to compilation errors. It is a more modern and efficient alternative to traditional include guards.
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
// my_class.h
#pragma once

#include <string>

class MyClass {
public:
    MyClass(std::string name);
private:
    std::string name_;
};
```

</div>
<div class="code-bad">

```cpp
// my_class.h
// Missing #pragma once

#include <string>

class MyClass {
public:
    MyClass(std::string name);
private:
    std::string name_;
};

// Also bad: using old-style include guards
#ifndef MY_CLASS_H
#define MY_CLASS_H
// ... content ...
#endif // MY_CLASS_H
```

</div>
</div>
</div>
</div>

<!-- ## Copyright Header

<div class="rule-card">
<h3 class="rule-title">HEADER_COPYRIGHT</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: HEADER_COPYRIGHT</span>
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
</div> -->

## Summary

Well-structured header files are fundamental to a C++ project:

- **`#pragma once`**: The modern, standard way to prevent multiple inclusions.