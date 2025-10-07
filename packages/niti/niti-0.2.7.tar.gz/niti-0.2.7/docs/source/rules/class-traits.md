# Class Trait Rules

Class traits are base classes that define the fundamental capabilities of a class, such as its copy, move, or static nature. Enforcing these traits ensures architectural consistency and helps prevent unintended usage.

## Missing Class Trait

<div class="rule-card">
<h3 class="rule-title">CLASS_TRAIT_MISSING</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: CLASS_TRAIT_MISSING</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Requires classes to explicitly inherit from a trait base class (e.g., `Copyable`, `Movable`, `NonCopyable`) to clearly define their copy and move semantics.
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
// This class is designed to be copied and moved.
class ValueObject : public CopyableMovable {
public:
    // ...
};

// This class manages a resource and should not be copied.
class ResourceManager : public NonCopyable {
public:
    // ...
};

// This class can be moved but not copied.
class UniqueResource : public Movable {
public:
    // ...
};
```

</div>
<div class="code-bad">

```cpp
// This class has no explicit trait.
// Can it be copied? Moved? It's ambiguous.
class ValueObject {
public:
    // ...
};

// The compiler will generate default copy/move operations,
// which might be incorrect for a resource-managing class.
class ResourceManager {
public:
    // ...
private:
    int* resource_;
};
```

</div>
</div>
</div>
</div>

## Static Class Trait

<div class="rule-card">
<h3 class="rule-title">CLASS_TRAIT_STATIC</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: CLASS_TRAIT_STATIC</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Requires utility classes that contain only static methods to inherit from a `StaticClass` trait. This trait typically deletes the constructor to prevent instantiation.
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
// This class is a collection of static utility functions.
// Inheriting from StaticClass prevents it from being instantiated.
class MathUtils : public StaticClass {
public:
    static double Add(double a, double b) { return a + b; }
    static double Multiply(double a, double b) { return a * b; }
};

void usage() {
    auto sum = MathUtils::Add(2.0, 3.0);
}
```

</div>
<div class="code-bad">

```cpp
// This utility class is missing the StaticClass trait.
class MathUtils {
public:
    static double Add(double a, double b) { return a + b; }
    static double Multiply(double a, double b) { return a * b; }
};

void usage() {
    // It can be accidentally instantiated, which makes no sense.
    MathUtils utils_instance;
    auto sum = utils_instance.Add(2.0, 3.0); // Misleading
}
```

</div>
</div>
</div>
</div>

## Trait Base Classes

The Trait-base classes are defined as follows: 

### NonCopyable

```cpp
class NonCopyable {
 public:
  // Delete copy constructor and copy assignment operator
  NonCopyable(const NonCopyable&) = delete;
  NonCopyable& operator=(const NonCopyable&) = delete;

  // Default move constructor and move assignment operator
  // A class that is NonCopyable can still be movable by default.
  // If you want to prevent this, the derived class must delete them,
  // or you can use NonCopyableNonMovable.
  NonCopyable(NonCopyable&&) = default;
  NonCopyable& operator=(NonCopyable&&) = default;
protected:
  NonCopyable() = default;
  ~NonCopyable() = default;
};
```

### Non-Movable

```cpp
class NonMovable {
 public:
  // Delete move constructor and move assignment operator
  NonMovable(NonMovable&&) = delete;
  NonMovable& operator=(NonMovable&&) = delete;

  // Default copy constructor and copy assignment operator
  // A class that is NonMovable can still be copyable by default.
  NonMovable(const NonMovable&) = default;
  NonMovable& operator=(const NonMovable&) = default;
 protected:
  NonMovable() = default;
  ~NonMovable() = default;

};
```

### NonCopyableNonMovable

```cpp
class NonCopyableNonMovable {
 protected:
  NonCopyableNonMovable() = default;
  ~NonCopyableNonMovable() = default;

 public:
  // Delete all copy and move operations
  NonCopyableNonMovable(const NonCopyableNonMovable&) = delete;
  NonCopyableNonMovable& operator=(const NonCopyableNonMovable&) = delete;
  NonCopyableNonMovable(NonCopyableNonMovable&&) = delete;
  NonCopyableNonMovable& operator=(NonCopyableNonMovable&&) = delete;
};
```

## Summary

Using class traits makes the intended behavior of a class explicit:

- **Define Copy/Move Semantics**: Clearly state whether a class is `Copyable`, `Movable`, or `NonCopyable`.
- **Identify Static Utilities**: Mark utility classes with `StaticClass` to prevent instantiation.

This leads to a more robust and self-documenting architecture.