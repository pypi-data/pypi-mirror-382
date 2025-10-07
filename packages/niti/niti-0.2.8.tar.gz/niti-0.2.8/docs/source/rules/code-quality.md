# Code Quality Rules

High-quality code is not just about correctness; it's also about clarity, maintainability, and avoiding common pitfalls. These rules target issues that can lead to bugs, reduce readability, or create unnecessary clutter.

## Magic Numbers

<div class="rule-card">
<h3 class="rule-title">QUALITY_MAGIC_NUMBERS</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: QUALITY_MAGIC_NUMBERS</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Forbids the use of unnamed, "magic" numbers in code. All numeric literals (except for simple cases like 0, 1, -1) should be defined as named constants to explain their meaning.
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
namespace Network {
    constexpr int kDefaultPort = 8080;
    constexpr int kMaxConnections = 100;
    constexpr double kTimeoutSeconds = 30.0;
}

void Connect() {
    if (connection.port() == Network::kDefaultPort) {
        // ...
    }
}

void SetTimeout(double seconds) {
    if (seconds > Network::kTimeoutSeconds) {
        // ...
    }
}

const int buffer_size = 1024;      // Power of 2s allowed
if (count > 100) {                  // 1, 100, 1000 Allowed
    ResizeBuffer(2048);             // Power of 2s allowed
}
```

</div>
<div class="code-bad">

```cpp
// What do these numbers mean?
void Connect() {
    if (connection.port() == 8080) { // Magic number
        // ...
    }
}

void SetTimeout(double seconds) {
    if (seconds > 30.0) { // No Variable
        // ...
    }
}
```

</div>
</div>
</div>
</div>


## Summary

Focusing on code quality leads to a more robust and maintainable system:

- **Name your numbers**: Avoid magic numbers by defining named constants.