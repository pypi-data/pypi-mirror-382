# Namespace Rules

Proper namespace management is essential for organizing code, preventing naming collisions, and maintaining a clean global scope. These rules help enforce a consistent and modern approach to using namespaces in C++.

## Nested Namespace Declaration

<div class="rule-card">
<h3 class="rule-title">NAMESPACE_OLD_STYLE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMESPACE_OLD_STYLE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Prefers the concise C++17 nested namespace syntax (`namespace A::B::C`) over the older, style of nesting namespace blocks.
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
// C++17 nested namespace syntax is clean and concise
namespace MyCompany::Core::Logging {
    void Log(const std::string& message);
}

namespace Niti::Rules::Naming {
    class FunctionNameRule;
}
```

</div>
<div class="code-bad">

```cpp
// Old-style nested namespaces are verbose
namespace MyCompany {
    namespace Core {
        namespace Logging {
            void Log(const std::string& message);
        }
    }
}

namespace Niti {
    namespace Rules {
        namespace Naming {
            class FunctionNameRule;
        }
    }
}
```

</div>
</div>
</div>
</div>

## `using namespace` in Headers

<div class="rule-card">
<h3 class="rule-title">NAMESPACE_USING_FORBIDDEN</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMESPACE_USING_FORBIDDEN</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Forbids `using namespace` directives in header files to prevent namespace pollution, which can lead to symbol clashes and unexpected behavior in including files.
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
// In a header file (.h, .hpp)
#include <string>
#include <vector>

// Use explicit namespace qualification
namespace MyApi {
    class MyClass {
    public:
        void ProcessData(const std::vector<int>& data);
        std::string GetName() const;
    private:
        std::string name_;
    };
}
```

</div>
<div class="code-bad">

```cpp
// In a header file (.h, .hpp)
#include <string>
#include <vector>

// This pollutes the global namespace for any file that includes this header
using namespace std;

namespace MyApi {
    class MyClass {
    public:
        // Types are now ambiguous
        void ProcessData(const vector<int>& data);
        string GetName() const;
    private:
        string name_;
    };
}
```

</div>
</div>
</div>
</div>

## Long Namespace Simplification

<div class="rule-card">
<h3 class="rule-title">NAMESPACE_LONG_USAGE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMESPACE_LONG_USAGE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Suggests using namespace aliases or `using` declarations within `.cpp` files to simplify code when dealing with deeply nested or long namespaces.
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
// In a .cpp file
#include "my_header.h"

// Use a namespace alias for brevity
namespace CoreLog = MyCompany::Core::Logging;

void Initialize() {
    CoreLog::Initialize();
    auto processor = std::make_unique<MyCompany::Core::Processing::DataProcessor>();
    processor->Process();
}

// Or use a 'using' declaration for a specific class
using MyCompany::Core::Processing::DataProcessor;

void Run() {
    auto processor = std::make_unique<DataProcessor>();
    processor->Process();
}
```

</div>
<div class="code-bad">

```cpp
// In a .cpp file
#include "my_header.h"

void Initialize() {
    // Repeated long namespace makes code hard to read
    MyCompany::Core::Logging::Initialize();
    auto processor = std::make_unique<MyCompany::Core::Processing::DataProcessor>();
    processor->Process();
    MyCompany::Core::Logging::Log("Initialized");
}
```

</div>
</div>
</div>
</div>

## Summary

Effective namespace usage is key to scalable C++ projects:

- **Use Nested C++17 style syntax**: Keep namespace declarations clean and modern.
- **Avoid `using namespace` in headers**: Prevent symbol conflicts and maintain a clean global scope.
- **Simplify in implementation**: Use aliases and `using` declarations in `.cpp` files to improve readability without polluting headers for long namespace names