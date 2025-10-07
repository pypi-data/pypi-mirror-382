# Safety Rules

Ensuring code safety is critical to prevent common bugs, memory leaks, and undefined behavior. These rules enforce modern C++ practices that lead to more robust and secure code.

## Unsafe Casts

<div class="rule-card">
<h3 class="rule-title">SAFETY_UNSAFE_CAST</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: SAFETY_UNSAFE_CAST</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Forbids dangerous C-style casts, `reinterpret_cast`, and `const_cast` in favor of safer alternatives like `static_cast`.</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect (Lint Error)</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// Use static_cast for safe type conversions
int integer_value = 42;
double float_value = static_cast<double>(integer_value);
// Use C++-style function casts for constructors
MyObject obj = MyObject(some_value);
```

</div>
<div class="code-bad">

```cpp
// Avoid reinterpret_cast for type punning
float f = 3.14f;
int* i = reinterpret_cast<int*>(&f); // Undefined behavior

// Avoid C-style casts
double d = 12.34;
int x = (int)d; // Can hide narrowing errors

// Avoid const_cast to remove constness
const int value = 10;
int* ptr = const_cast<int*>(&value);
*ptr = 20; // Undefined behavior


// Avoid dynamic_cast for safe downcasting in hierarchies
class Base { virtual ~Base() = default; };
class Derived : public Base {};
Base* b = new Derived;
Derived* d = dynamic_cast<Derived*>(b);
```

</div>
</div>
</div>
</div>

## Range-Based For Loops

<div class="rule-card">
<h3 class="rule-title">SAFETY_RANGE_LOOP_MISSING</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: SAFETY_RANGE_LOOP_MISSING</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Prefers range-based for loops over traditional index-based loops to prevent common off-by-one errors and improve readability.
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
std::vector<int> numbers = {1, 2, 3, 4, 5};

// Simple, safe, and readable
for (const auto& num : numbers) {
    std::cout << num << std::endl;
}

// Modifying elements
for (auto& num : numbers) {
    num *= 2;
}
```

</div>
<div class="code-bad">

```cpp
std::vector<int> numbers = {1, 2, 3, 4, 5};

// Prone to off-by-one errors
for (size_t i = 0; i < numbers.size(); ++i) {
    std::cout << numbers[i] << std::endl;
}

// Verbose and less clear
for (auto it = numbers.begin(); it != numbers.end(); ++it) {
    std::cout << *it << std::endl;
}
```

</div>
</div>
</div>
</div>

## Raw Pointer Return Types

<div class="rule-card">
<h3 class="rule-title">SAFETY_RAW_POINTER_RETURN</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: SAFETY_RAW_POINTER_RETURN</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Forbids returning raw pointers from functions, as they create ambiguous ownership semantics and can lead to memory leaks. Smart pointers or references should be used instead.
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
// Return a unique_ptr for exclusive ownership
std::unique_ptr<Widget> CreateWidget() {
    return std::make_unique<Widget>();
}

// Return a shared_ptr for shared ownership
std::shared_ptr<Gadget> GetSharedGadget() {
    static auto gadget = std::make_shared<Gadget>();
    return gadget;
}

// Return a reference for non-owning access
Widget& GetMainWidget() {
    static Widget w;
    return w;
}
```

</div>
<div class="code-bad">

```cpp
// Who is responsible for deleting this?
Widget* CreateWidget() {
    return new Widget(); // Memory leak waiting to happen
}

// Ambiguous ownership and lifetime
Gadget* GetSharedGadget() {
    static Gadget* g = new Gadget();
    return g;
}
```

</div>
</div>
</div>
</div>

## Raw Pointer Parameters

<div class="rule-card">
<h3 class="rule-title">SAFETY_RAW_POINTER_PARAM</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: SAFETY_RAW_POINTER_PARAM</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Discourages using raw pointers as parameters, as they create unclear ownership and lifetime semantics. Use references for non-owning access or smart pointers for ownership transfer.
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
// Use a const reference for non-owning, read-only access
void PrintWidget(const Widget& widget) {
    widget.Print();
}

// Use a non-const reference to allow modification
void UpdateWidget(Widget& widget) {
    widget.Update();
}

// Use a smart pointer to transfer ownership
void TakeOwnership(std::unique_ptr<Widget> widget) {
    // ... stores widget
}
```

</div>
<div class="code-bad">

```cpp
// Is the pointer guaranteed to be valid? Is it owned?
void PrintWidget(Widget* widget) {
    if (widget) { // Always requires a null check
        widget->Print();
    }
}

// Who manages the lifetime of this pointer?
void UpdateWidget(Widget* widget) {
    if (widget) {
        widget->Update();
    }
}
```

</div>
</div>
</div>
</div>

## Summary

By adhering to these safety rules, you can significantly reduce the risk of common C++ pitfalls:

- **Prefer safe casts**: Use `static_cast` to avoid undefined behavior.
- **Use range-based for loops**: Write cleaner and safer loops.
- **Avoid raw pointers in interfaces**: Use smart pointers and references to manage memory and ownership explicitly.

These practices lead to more reliable code that is easier to reason about and maintain.