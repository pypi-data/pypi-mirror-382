# Modern C++ Rules

Modern C++ rules promote the use of contemporary C++ features that improve code safety, performance, and readability.

## Missing noexcept

<div class="rule-card">
<h3 class="rule-title">MODERN_MISSING_NOEXCEPT</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: MODERN_MISSING_NOEXCEPT</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Suggests adding noexcept to functions that should not throw exceptions, particularly destructors, move operations, swap functions, and simple getters/setters.
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
class ResourceManager {
public:
    // Destructors should be noexcept
    ~ResourceManager() noexcept {
        cleanup();
    }
    
    // Move constructor should be noexcept
    ResourceManager(ResourceManager&& other) noexcept 
        : data_(std::move(other.data_)) {
    }
    
    // Move assignment should be noexcept
    ResourceManager& operator=(ResourceManager&& other) noexcept {
        if (this != &other) {
            data_ = std::move(other.data_);
        }
        return *this;
    }
    
    // Simple getters should be noexcept
    size_t GetSize() const noexcept {
        return data_.size();
    }
    
    // Swap functions should be noexcept
    void Swap(ResourceManager& other) noexcept {
        data_.swap(other.data_);
    }
    
private:
    std::vector<int> data_;
};
```

</div>
<div class="code-bad">

```cpp
class ResourceManager {
public:
    // Missing noexcept on destructor
    ~ResourceManager() {
        cleanup();
    }
    
    // Missing noexcept on move constructor
    ResourceManager(ResourceManager&& other) 
        : data_(std::move(other.data_)) {
    }
    
    // Missing noexcept on move assignment
    ResourceManager& operator=(ResourceManager&& other) {
        if (this != &other) {
            data_ = std::move(other.data_);
        }
        return *this;
    }
    
    // Missing noexcept on simple getter
    size_t GetSize() const {
        return data_.size();
    }
    
    // Missing noexcept on swap function
    void Swap(ResourceManager& other) {
        data_.swap(other.data_);
    }
    
private:
    std::vector<int> data_;
};
```

</div>
</div>
</div>
</div>

## Missing const

<div class="rule-card">
<h3 class="rule-title">MODERN_MISSING_CONST</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: MODERN_MISSING_CONST</span>
    <span class="severity-badge severity-error">Warning</span>
</div>
<div class="rule-description">
Detects methods that should be marked const but aren't, particularly getter methods that don't modify object state.
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
class DataContainer {
public:
    // Getters are const - don't modify state
    const std::string& GetName() const {
        return name_;
    }
    
    size_t GetSize() const {
        return data_.size();
    }
    
    bool IsEmpty() const {
        return data_.empty();
    }
    
    // Query methods are const
    bool Contains(int value) const {
        return std::find(data_.begin(), data_.end(), value) != data_.end();
    }
    
    // Status checking methods are const
    bool IsValid() const {
        return !name_.empty() && !data_.empty();
    }
    
    // Non-const methods that modify state
    void SetName(const std::string& name) {
        name_ = name;
    }
    
    void AddData(int value) {
        data_.push_back(value);
    }
    
private:
    std::string name_;
    std::vector<int> data_;
};
```

</div>
<div class="code-bad">

```cpp
class DataContainer {
public:
    // Missing const on getters
    const std::string& GetName() {
        return name_;
    }
    
    size_t GetSize() {
        return data_.size();
    }
    
    bool IsEmpty() {
        return data_.empty();
    }
    
    // Missing const on query methods
    bool Contains(int value) {
        return std::find(data_.begin(), data_.end(), value) != data_.end();
    }
    
    // Missing const on status checking
    bool IsValid() {
        return !name_.empty() && !data_.empty();
    }
    
    // Non-const methods that modify state
    void SetName(const std::string& name) {
        name_ = name;
    }
    
    void AddData(int value) {
        data_.push_back(value);
    }
    
private:
    std::string name_;
    std::vector<int> data_;
};
```

</div>
</div>
</div>
</div>

## Missing [[nodiscard]]

<div class="rule-card">
<h3 class="rule-title">MODERN_NODISCARD_MISSING</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: MODERN_NODISCARD_MISSING</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Suggests adding [[nodiscard]] to functions whose return values should not be ignored, including factory functions, getters, validation functions, and computational functions.
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
class ResourceFactory {
public:
    // Factory functions should be [[nodiscard]]
    [[nodiscard]] std::unique_ptr<Resource> CreateResource() {
        return std::make_unique<Resource>();
    }
    
    [[nodiscard]] Resource MakeResource(int id) {
        return Resource{id};
    }
    
    // Getters should be [[nodiscard]]
    [[nodiscard]] const std::string& GetName() const {
        return name_;
    }
    
    [[nodiscard]] size_t GetCount() const {
        return count_;
    }
    
    // Validation functions should be [[nodiscard]]
    [[nodiscard]] bool ValidateInput(const std::string& input) const {
        return !input.empty() && input.size() < 100;
    }
    
    [[nodiscard]] bool IsReady() const {
        return initialized_;
    }
    
    // Computational functions should be [[nodiscard]]
    [[nodiscard]] int Calculate(int x, int y) const {
        return x * y + 42;
    }
    
    [[nodiscard]] std::string ProcessData(const Data& data) const {
        return data.ToString();
    }
    
private:
    std::string name_;
    size_t count_;
    bool initialized_;
};
```

</div>
<div class="code-bad">

```cpp
class ResourceFactory {
public:
    // Missing [[nodiscard]] on factory functions
    std::unique_ptr<Resource> CreateResource() {
        return std::make_unique<Resource>();
    }
    
    Resource MakeResource(int id) {
        return Resource{id};
    }
    
    // Missing [[nodiscard]] on getters
    const std::string& GetName() const {
        return name_;
    }
    
    size_t GetCount() const {
        return count_;
    }
    
    // Missing [[nodiscard]] on validation functions
    bool ValidateInput(const std::string& input) const {
        return !input.empty() && input.size() < 100;
    }
    
    bool IsReady() const {
        return initialized_;
    }
    
    // Missing [[nodiscard]] on computational functions
    int Calculate(int x, int y) const {
        return x * y + 42;
    }
    
    std::string ProcessData(const Data& data) const {
        return data.ToString();
    }
    
private:
    std::string name_;
    size_t count_;
    bool initialized_;
};
```

</div>
</div>
</div>
</div>

## Smart Pointer by Reference

<div class="rule-card">
<h3 class="rule-title">MODERN_SMART_PTR_BY_REF</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: MODERN_SMART_PTR_BY_REF</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Enforces passing smart pointers by value for ownership transfer rather than by reference, which provides clearer ownership semantics.
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
class ResourceManager {
public:
    // Pass unique_ptr by value for ownership transfer
    void StoreResource(std::unique_ptr<Resource> resource) {
        stored_resource_ = std::move(resource);
    }
    
    // Pass shared_ptr by value for shared ownership
    void AddObserver(std::shared_ptr<Observer> observer) {
        observers_.push_back(observer);
    }
    
    // Move semantics for ownership transfer
    void TransferData(std::unique_ptr<Data>&& data) {
        current_data_ = std::move(data);
    }
    
    // Use raw reference for non-owning access
    void ProcessResource(const Resource& resource) {
        // Function doesn't take ownership
        resource.Process();
    }
    
    // Factory functions return by value
    std::unique_ptr<Resource> CreateResource() {
        return std::make_unique<Resource>();
    }
    
    std::shared_ptr<Cache> GetSharedCache() {
        if (!cache_) {
            cache_ = std::make_shared<Cache>();
        }
        return cache_;
    }
    
private:
    std::unique_ptr<Resource> stored_resource_;
    std::unique_ptr<Data> current_data_;
    std::vector<std::shared_ptr<Observer>> observers_;
    std::shared_ptr<Cache> cache_;
};
```

</div>
<div class="code-bad">

```cpp
class ResourceManager {
public:
    // Don't pass smart pointers by reference
    void StoreResource(const std::unique_ptr<Resource>& resource) {
        // Unclear: does this function take ownership?
        stored_resource_ = resource;  // Won't compile!
    }
    
    // Passing shared_ptr by reference is confusing
    void AddObserver(const std::shared_ptr<Observer>& observer) {
        observers_.push_back(observer);  // Creates a copy anyway
    }
    
    // Reference to unique_ptr is problematic
    void TransferData(std::unique_ptr<Data>& data) {
        current_data_ = std::move(data);  // Modifies caller's pointer
    }
    
    // Inconsistent ownership semantics
    void ProcessResource(std::unique_ptr<Resource>& resource) {
        // Does this function own the resource or just use it?
        resource->Process();
    }
    
    // Returning references to smart pointers
    const std::unique_ptr<Resource>& GetResource() const {
        return stored_resource_;  // Exposes internal implementation
    }
    
    std::shared_ptr<Cache>& GetCache() {
        if (!cache_) {
            cache_ = std::make_shared<Cache>();
        }
        return cache_;  // Allows external modification
    }
    
private:
    std::unique_ptr<Resource> stored_resource_;
    std::unique_ptr<Data> current_data_;
    std::vector<std::shared_ptr<Observer>> observers_;
    std::shared_ptr<Cache> cache_;
};
```

</div>
</div>
</div>
</div>

## Summary

Modern C++ rules promote contemporary best practices:

- **Use noexcept**: Mark functions that don't throw exceptions, especially destructors and move operations
- **Const Correctness**: Mark methods const when they don't modify object state
- **[[nodiscard]]**: Prevent accidental ignoring of important return values
- **Smart Pointer Semantics**: Pass smart pointers by value for clear ownership transfer

These practices lead to more efficient, safer, and more expressive C++ code that takes advantage of modern language features.