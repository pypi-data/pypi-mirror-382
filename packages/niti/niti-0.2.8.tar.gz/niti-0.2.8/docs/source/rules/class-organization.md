# Class Organization Rules

A well-organized class is easier to read, understand, and maintain. These rules enforce a consistent structure for the members of a class, including access specifiers and the order of different member types.

## Access Specifier Order

<div class="rule-card">
<h3 class="rule-title">CLASS_ACCESS_SPECIFIER_ORDER</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: CLASS_ACCESS_SPECIFIER_ORDER</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Enforces a standard order for access specifiers within a class definition: `public` members should come first, followed by `protected`, and then `private`. This convention prioritizes the public API. The Class functions should still be documented according to the `[Documentation rules](./documentation.md)`
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
class MyWidget {
public:
    // Public API is declared first for clarity.
    MyWidget();
    void Update();

protected:
    // Protected members for derived classes.
    void OnUpdate();

private:
    // Private implementation details are last.
    void Recalculate();
    int value_;
};
```

</div>
<div class="code-bad">

```cpp
class MyWidget {
private:
    // Private members are declared first, hiding the public API.
    void Recalculate();
    int value_;

public:
    MyWidget();
    void Update();

protected:
    // Order is inconsistent.
    void OnUpdate();
};
```

</div>
</div>
</div>
</div>

## Member Organization

<div class="rule-card">
<h3 class="rule-title">CLASS_MEMBER_ORGANIZATION</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: CLASS_MEMBER_ORGANIZATION</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Enforces a logical ordering of class members within each access section: types (like `using` or `enum`), constructors/destructor, public methods, and finally member variables.
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
class DataManager {
public:
    // 1. Type aliases and enums (When Used)
    using DataMap = std::map<std::string, int>;

    // 2. Constructors and destructor
    DataManager();
    ~DataManager();

    // 3. Public methods
    void LoadData();
    const DataMap& GetData() const;

private:
    // 4. Member variables
    DataMap data_;
    bool is_loaded_;
};
```

</div>
<div class="code-bad">

```cpp
class DataManager {
public:
    // Member variables mixed with methods
    DataMap data_;

    // Constructor after methods
    void LoadData();
    DataManager();

    // Type alias at the end
    using DataMap = std::map<std::string, int>;
};
```

</div>
</div>
</div>
</div>

## Summary

A consistent class structure makes your code predictable and easy to navigate:

- **API First**: Always put the `public` interface at the top.
- **Logical Grouping**: Order members by type, constructors, methods, and variables.

This organization helps developers quickly understand a class's purpose and how to use it.