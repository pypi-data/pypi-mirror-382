"""Unit tests for modern C++ rules."""

from test.test_utils import RuleTestCase

import pytest


@pytest.mark.unit
class TestModernMissingNoexcept(RuleTestCase):
    """Test MODERN_MISSING_NOEXCEPT rule."""

    rule_id = "modern-missing-noexcept"

    def test_detects_missing_noexcept_constructors(self):
        """Test detection of constructors without noexcept."""
        code = """
class Widget {
public:
    Widget() {}                      // Line 4: missing noexcept
    Widget(int value) : value_(value) {}  // Line 5: missing noexcept
    Widget(const Widget& other) = default;  // Line 6: copy ctor, noexcept depends on members
    Widget(Widget&& other) {}        // Line 7: move ctor should be noexcept
    
    ~Widget() {}                     // Line 9: destructor should be noexcept
    
private:
    int value_ = 0;
};
"""
        issues = self.lint_only_this_rule(code)
        # Should detect missing noexcept on default constructor, move constructor, and destructor
        self.assert_has_rule(issues, self.rule_id)
        # Specific line checks depend on implementation

    def test_detects_missing_noexcept_simple_methods(self):
        """Test detection of simple methods that could be noexcept."""
        code = """
class Counter {
public:
    int GetValue() const { return value_; }          // Line 4: Simple Getter
    bool IsZero() const { return value_ == 0; }      // Line 5: could be noexcept
    
    // These might throw
    void SetValue(int v) {
        if (v < 0) throw std::invalid_argument("negative value");
        value_ = v;
    }

private:
    int value_ = 0;
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=1)

    def test_accepts_noexcept_methods(self):
        """Test that methods with noexcept are accepted."""
        code = """
class Widget {
public:
    Widget() noexcept = default;
    Widget(Widget&& other) noexcept : data_(std::move(other.data_)) {}
    ~Widget() = default;  // Implicitly noexcept

    int GetValue() const noexcept { return value_; }
    void Reset() noexcept { value_ = 0; }

    // Correctly not noexcept
    void MightThrow() {
        data_.at(0) = 1;  // vector::at can throw
    }

private:
    int value_ = 0;
    std::vector<int> data_;
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_deleted_functions_not_flagged(self):
        """Test that deleted functions are not flagged for missing noexcept.

        Deleted functions (= delete) cannot have noexcept specifier.
        Adding noexcept to a deleted function is a C++ syntax error.
        """
        code = """
class NonMovable {
public:
    NonMovable() = default;

    // Deleted move operations - should NOT be flagged
    NonMovable(NonMovable&&) = delete;
    NonMovable& operator=(NonMovable&&) = delete;

    // Regular move operations - should be flagged if not noexcept
    // (none in this class)
};

class Movable {
public:
    Movable() = default;

    // Active move operations without noexcept - should be flagged
    Movable(Movable&& other) { data_ = std::move(other.data_); }
    Movable& operator=(Movable&& other) { data_ = std::move(other.data_); return *this; }

private:
    std::vector<int> data_;
};
"""
        issues = self.lint_only_this_rule(code)
        # Should only flag the active move operations in Movable, not the deleted ones
        self.assert_has_rule(issues, self.rule_id, count=2)
        # Lines 18 and 19 (move constructor and move assignment in Movable)

    def test_template_functions_not_flagged_as_move_operations(self):
        """Test that template functions with && are not flagged as move operations.

        Template functions like template<typename T> void func(T&&) are forwarding
        references (universal references), not move operations.
        """
        code = """
class ThreadManager {
public:
    // Template function with && - NOT a move constructor
    template <typename Func>
    void LaunchThread(const int rank, Func&& func) {
        threads_.emplace_back(std::forward<Func>(func));
    }

    // Regular function with && - NOT a move constructor (different parameter type)
    void ProcessData(std::string&& data) {
        // process data
    }

    // Actual move constructor - should be flagged if not noexcept
    ThreadManager(ThreadManager&& other) {
        threads_ = std::move(other.threads_);
    }

private:
    std::vector<std::thread> threads_;
};
"""
        issues = self.lint_only_this_rule(code)
        # Should only flag the actual move constructor on line 15
        self.assert_has_rule(issues, self.rule_id, count=1)
        self.assert_issue_at_line(issues, self.rule_id, 16)


@pytest.mark.unit
class TestModernMissingConst(RuleTestCase):
    """Test MODERN_MISSING_CONST rule."""

    rule_id = "modern-missing-const"

    def test_detects_missing_const_methods(self):
        """Test detection of methods that should be const."""
        code = """
class DataHolder {
public:
    int GetValue() { return value_; }           // Line 4: should be const
    bool IsEmpty() { return data_.empty(); }    // Line 5: should be const
    size_t Size() { return data_.size(); }      // Line 6: should be const
    
    // These modify state, so non-const is correct
    void SetValue(int v) { value_ = v; }
    void Clear() { data_.clear(); }
    
private:
    int value_ = 0;
    std::vector<int> data_;
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)
        self.assert_issue_at_line(issues, self.rule_id, 4)
        self.assert_issue_at_line(issues, self.rule_id, 5)
        self.assert_issue_at_line(issues, self.rule_id, 6)

    def test_accepts_const_methods(self):
        """Test that const methods are accepted."""
        code = """
class DataHolder {
public:
    int GetValue() const { return value_; }
    bool IsEmpty() const { return data_.empty(); }
    size_t Size() const { return data_.size(); }
    
    // Non-const methods that modify state
    void SetValue(int v) { value_ = v; }
    void Clear() { data_.clear(); }
    
private:
    int value_ = 0;
    std::vector<int> data_;
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_const_overloads(self):
        """Test that const overloads are handled correctly."""
        code = """
class Container {
public:
    int& At(size_t index) { return data_[index]; }              // Non-const version
    const int& At(size_t index) const { return data_[index]; }  // Const version

    // Only non-const version - might be intentional
    int& operator[](size_t index) { return data_[index]; }

private:
    std::vector<int> data_;
};
"""
        self.lint_only_this_rule(code)
        # Should not flag the non-const versions when const overload exists

    def test_override_methods_not_flagged(self):
        """Test that override methods are not flagged for missing const.

        Methods marked with override must match the base class signature,
        so we cannot add const unless the base class method is also const.
        """
        code = """
class Base {
public:
    virtual void DoSomething() { }  // Not a getter, won't be flagged
    // Intentionally non-const to test override behavior
    virtual void ProcessData(int data) { }  // Not a getter (void return)
};

class Derived : public Base {
public:
    // Override method - should NOT be flagged
    // Cannot add const because base class method is not const
    void ProcessData(int data) override {
        // do something
    }

    // Non-override getter that looks like it should be const but has override keyword
    [[nodiscard]] bool IsOperationEnabled(int metric_type) override {
        return true;
    }

    // This should be flagged (no override)
    bool GetStatus() { return status_; }

private:
    bool status_ = true;
};
"""
        issues = self.lint_only_this_rule(code)
        # Should only flag GetStatus. The override methods should not be flagged.
        self.assert_has_rule(issues, self.rule_id, count=1)
        self.assert_issue_at_line(issues, self.rule_id, 23)

    def test_static_methods_not_flagged(self):
        """Test that static methods are not flagged for missing const.

        Static methods cannot have const qualifier as they don't have a 'this' pointer.
        Adding const to a static method is a compilation error.
        """
        code = """
class Registry {
public:
    // Static method - should NOT be flagged even though it looks like a getter
    [[nodiscard]] static std::shared_ptr<Base> Get(int key) {
        return registry_[key]();
    }

    [[nodiscard]] static bool IsRegistered(int key) {
        return registry_.contains(key);
    }

    // Non-static getter - should be flagged
    bool GetValue() { return value_; }

private:
    static std::map<int, std::function<std::shared_ptr<Base>()>> registry_;
    bool value_ = true;
};
"""
        issues = self.lint_only_this_rule(code)
        # Should only flag GetValue, not the static methods
        self.assert_has_rule(issues, self.rule_id, count=1)
        self.assert_issue_at_line(issues, self.rule_id, 14)


@pytest.mark.unit
class TestModernNodiscardMissing(RuleTestCase):
    """Test MODERN_NODISCARD_MISSING rule."""

    rule_id = "modern-nodiscard-missing"

    def test_detects_missing_nodiscard(self):
        """Test detection of functions that should have [[nodiscard]]."""
        code = """
class Calculator {
public:
    int Add(int a, int b) { return a + b; }         // Line 4: should have [[nodiscard]]
    bool IsValid() const { return valid_; }         // Line 5: should have [[nodiscard]]
    size_t GetSize() const { return size_; }        // Line 6: should have [[nodiscard]]
    
    // These don't need [[nodiscard]]
    void Reset() { size_ = 0; valid_ = false; }
    void Process() { /* side effects */ }
    
private:
    size_t size_ = 0;
    bool valid_ = true;
};

// Free functions
int ComputeHash(const std::string& str) { return 0; }  // Line 17: should have [[nodiscard]]
bool CheckCondition() { return true; }                 // Line 18: should have [[nodiscard]]
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=5)

    def test_accepts_nodiscard_functions(self):
        """Test that functions with [[nodiscard]] are accepted."""
        code = """
class Calculator {
public:
    [[nodiscard]] int Add(int a, int b) { return a + b; }
    [[nodiscard]] bool IsValid() const { return valid_; }
    [[nodiscard]] size_t GetSize() const { return size_; }
    
    void Reset() { size_ = 0; valid_ = false; }
    
private:
    size_t size_ = 0;
    bool valid_ = true;
};

[[nodiscard]] int ComputeHash(const std::string& str) { return 0; }
[[nodiscard("Check this condition"]] bool CheckCondition() { return true; }
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_nodiscard_with_output_params(self):
        """Test that functions with output parameters might not need [[nodiscard]]."""
        code = """
// Function returns error code and modifies output parameter
int ProcessData(const std::vector<int>& input, std::vector<int>& output) {
    output = input;
    return 0;  // Error code
}

// Function returns bool for success/failure
bool LoadFile(const std::string& path, std::string& content) {
    // Load file into content
    return true;
}
"""
        self.lint_only_this_rule(code)
        # These might still benefit from [[nodiscard]] for the error code/status


@pytest.mark.unit
class TestModernSmartPtrByRef(RuleTestCase):
    """Test MODERN_SMART_PTR_BY_REF rule."""

    rule_id = "modern-smart-ptr-by-ref"

    def test_accepts_smart_ptr_by_value(self):
        """Test that smart pointers passed by value are accepted (modern C++ best practice)."""
        code = """
void ProcessObject(std::shared_ptr<Widget> widget) {      // Line 2: by value (good)
    widget->DoSomething();
}

void HandleData(std::unique_ptr<Data> data) {             // Line 6: by value (ownership transfer)
    // Takes ownership - this is the correct pattern
}

class Manager {
public:
    void SetWidget(std::shared_ptr<Widget> w) {           // Line 12: by value (good)
        widget_ = w;
    }
    
private:
    std::shared_ptr<Widget> widget_;
};
"""
        issues = self.lint_only_this_rule(code)
        # By-value parameters are what we want (modern C++ best practice)
        self.assert_no_issues(issues)

    def test_detects_smart_ptr_by_const_ref(self):
        """Test detection of smart pointers passed by const reference."""
        code = """
void ProcessObject(const std::shared_ptr<Widget>& widget) {    // Line 2: should be by value
    widget->DoSomething();
}

void UseData(const std::unique_ptr<Data>& data) {              // Line 6: should be by value  
    data->Process();
}

class Manager {
public:
    void SetWidget(const std::shared_ptr<Widget>& w) {         // Line 12: should be by value
        widget_ = w;
    }
    
    const std::shared_ptr<Widget>& GetWidget() const {         // Line 16: returning reference is fine
        return widget_;
    }
    
private:
    std::shared_ptr<Widget> widget_;
};
"""
        issues = self.lint_only_this_rule(code)
        # Should detect const reference parameters that should be passed by value instead
        self.assert_has_rule(issues, self.rule_id, count=3)  # Lines 2, 6, 12

    def test_ownership_transfer_patterns(self):
        """Test patterns where by-value is appropriate for ownership transfer."""
        code = """
// Taking ownership - unique_ptr by value is correct
void TakeOwnership(std::unique_ptr<Resource> resource) {
    owned_resources_.push_back(std::move(resource));
}

// Sink parameter - shared_ptr by value then move
void StoreShared(std::shared_ptr<Widget> widget) {
    widgets_.emplace_back(std::move(widget));
}

// Returning smart pointers - by value is correct
std::unique_ptr<Resource> CreateResource() {
    return std::make_unique<Resource>();
}

std::shared_ptr<Widget> GetSharedWidget() {
    return std::make_shared<Widget>();
}
"""
        issues = self.lint_only_this_rule(code)
        # These by-value patterns are correct for ownership transfer
        self.assert_no_issues(issues)
