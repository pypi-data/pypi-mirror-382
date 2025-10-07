# Documentation Rules

Clear and consistent documentation is vital for code maintainability. These rules enforce the use of Doxygen-style comments for classes, functions, and parameters, ensuring that the codebase is self-documenting.

## Missing Function Documentation

<div class="rule-card">
<h3 class="rule-title">DOC_FUNCTION_MISSING</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: DOC_FUNCTION_MISSING</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Requires all public functions to have a Doxygen-style documentation block that describes their purpose.
</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect </div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
/**
 * @brief Processes a batch of incoming data records.
 * 
 * This function validates, transforms, and forwards the data to the next
 * stage in the processing pipeline.
 */
void ProcessData(const std::vector<DataRecord>& records);
```

</div>
<div class="code-bad">

```cpp
// Missing Doxygen comment block
void ProcessData(const std::vector<DataRecord>& records);
```

</div>
</div>
</div>
</div>

## Missing Class Documentation

<div class="rule-card">
<h3 class="rule-title">DOC_CLASS_MISSING</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: DOC_CLASS_MISSING</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Requires all class definitions to have a Doxygen-style documentation block that describes their purpose and responsibility.
</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect </div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
/**
 * @brief Manages user sessions and authentication.
 * 
 * This class handles user login, logout, and session validation.
 * It is responsible for maintaining the lifecycle of a user session.
 */
class SessionManager {
public:
    // ...
};
```

</div>
<div class="code-bad">

```cpp
// Missing Doxygen comment block
class SessionManager {
public:
    // ...
};
```

</div>
</div>
</div>
</div>

## Missing Parameter Documentation

<div class="rule-card">
<h3 class="rule-title">DOC_FUNCTION_MISSING_PARAM_DOCS</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: DOC_FUNCTION_MISSING_PARAM_DOCS</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Requires every function parameter to be documented with a `@param` tag, explaining its purpose.
</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect </div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
/**
 * @brief Finds a user by their ID and email.
 * 
 * @param user_id The unique identifier of the user.
 * @param email The email address to match.
 * @return A shared_ptr to the User object.
 */
shared_ptr<User> FindUser(int user_id, const std::string& email);
```

</div>
<div class="code-bad">

```cpp
/**
 * @brief Finds a user by their ID and email.
 * 
 * @return A pointer to the User object, or nullptr if not found.
 */
// Missing @param documentation for user_id and email
User* FindUser(int user_id, const std::string& email);
```

</div>
</div>
</div>
</div>

## Missing Return Value Documentation

<div class="rule-card">
<h3 class="rule-title">DOC_FUNCTION_MISSING_RETURN_DOCS</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: DOC_FUNCTION_MISSING_RETURN_DOCS</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Requires any non-void function to document its return value using a `@return` or `@returns` tag.
</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect </div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
/**
 * @brief Calculates the total size of the data.
 * 
 * @param records A list of data records.
 * @return The total size in bytes.
 */
size_t CalculateTotalSize(const std::vector<DataRecord>& records);
```

</div>
<div class="code-bad">

```cpp
/**
 * @brief Calculates the total size of the data.
 * 
 * @param records A list of data records.
 */
// Missing @return documentation
size_t CalculateTotalSize(const std::vector<DataRecord>& records);
```

</div>
</div>
</div>
</div>

## Summary

Thorough documentation is a gift to your future self and your teammates:

- **Document Everything**: Every class and public function should have a clear description.
- **Detail Parameters and Returns**: Explain what goes in and what comes out of each function.
- **Use Doxygen**: Adhere to a standard format that can be used to automatically generate documentation.