# Logging Rules

Consistent, structured logging is essential for debugging, monitoring, and understanding application behavior. These rules ensure that logging is done through a centralized system rather than using direct console output, which allows for better control over log levels, formatting, and destinations.

## Forbidden Direct Output

<div class="rule-card">
<h3 class="rule-title">LOGGING_FORBIDDEN_OUTPUT</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: LOGGING_FORBIDDEN_OUTPUT</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Forbids direct use of `std::cout`, `std::cerr`, `printf`, and `fprintf`. All logging should be routed through a dedicated logging library (e.g., `LOG_INFO`, `LOG_ERROR`) to ensure consistency and control.
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
// Use a structured logging macro
#include "logging.h"

void ProcessRequest(const Request& req) {
    LOG_INFO("Processing request {} for user {}", req.id, req.user);

    if (!req.IsValid()) {
        LOG_ERROR("Invalid request received: {}", req.Serialize());
        return;
    }

    LOG_DEBUG("Request payload size: {}", req.payload.size());
}
```

</div>
<div class="code-bad">

```cpp
#include <iostream>
#include <cstdio>

void ProcessRequest(const Request& req) {
    // Avoid direct console output
    std::cout << "Processing request " << req.id << std::endl;

    if (!req.IsValid()) {
        // Error messages should go through the logger
        std::cerr << "Error: Invalid request!" << std::endl;
        return;
    }

    // Debug messages should use the logger
    printf("Request payload size: %zu\n", req.payload.size());
}
```

</div>
</div>
</div>
</div>

## Summary

By centralizing logging and avoiding direct console output, you gain several advantages:

- **Configurability**: Easily change log levels (e.g., DEBUG, INFO, ERROR) at runtime.
- **Flexibility**: Redirect logs to files, network sockets, or other services without changing the code.
- **Consistency**: All log messages have a uniform format, including timestamps, severity, and source location.
- **Performance**: Logging libraries are often optimized to minimize performance impact.