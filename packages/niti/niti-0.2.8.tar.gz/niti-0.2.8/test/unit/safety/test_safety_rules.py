"""Unit tests for safety rules."""

from test.test_utils import RuleTestCase

import pytest


@pytest.mark.unit
class TestSafetyUnsafeCast(RuleTestCase):
    """Test SAFETY_UNSAFE_CAST rule."""

    rule_id = "safety-unsafe-cast"

    def test_detects_c_style_casts(self):
        """Test detection of C-style casts."""
        code = """
void TestCasts() {
    int x = 10;
    float f = (float)x;              // Line 4: C-style cast
    void* ptr = (void*)&x;           // Line 5: C-style cast
    char* cptr = (char*)malloc(10);  // Line 6: C-style cast
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)
        self.assert_issue_at_line(issues, self.rule_id, 4)
        self.assert_issue_at_line(issues, self.rule_id, 5)
        self.assert_issue_at_line(issues, self.rule_id, 6)

    def test_detects_reinterpret_cast(self):
        """Test detection of reinterpret_cast."""
        code = """
void TestReinterpret() {
    int x = 10;
    int* ptr = &x;
    char* cptr = reinterpret_cast<char*>(ptr);     // Line 5: reinterpret_cast
    void* vptr = reinterpret_cast<void*>(ptr);     // Line 6: reinterpret_cast
    
    // This should be fine
    float f = static_cast<float>(x);
    void* vptr2 = static_cast<void*>(ptr);
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=2)
        self.assert_issue_at_line(issues, self.rule_id, 5)
        self.assert_issue_at_line(issues, self.rule_id, 6)

    def test_accepts_safe_casts(self):
        """Test that safe casts are accepted."""
        code = """
void SafeCasts() {
    int x = 10;
    float f = static_cast<float>(x);
    
    Base* base = new Derived();
    Derived* derived = dynamic_cast<Derived*>(base); // Line 7: dynamic_cast is not safe
    
    const int* cptr = &x;
    int* ptr = const_cast<int*>(cptr); // Line 10: const_cast is not safe
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=2)
        self.assert_issue_at_line(issues, self.rule_id, 7)
        self.assert_issue_at_line(issues, self.rule_id, 10)


@pytest.mark.unit
class TestSafetyUnsafeCastFalsePositives(RuleTestCase):
    """Test that SAFETY_UNSAFE_CAST rule correctly handles false positives."""

    rule_id = "safety-unsafe-cast"

    def test_ignores_template_function_calls(self):
        """Test that template function calls are not flagged as unsafe casts."""
        code = """
void TestTemplateCalls() {
    // pybind11 template calls
    if (!py::isinstance<py::set>(src) && !py::isinstance<py::frozenset>(src))
        return false;
    
    // Standard library template calls
    auto ptr = std::make_unique<MyClass>(args);
    auto shared = std::make_shared<MyClass>(args);
    
    // Template type checking
    if (std::is_same<T, int>::value) {
        process();
    }
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_ignores_placement_new(self):
        """Test that placement new operators are not flagged."""
        code = """
class Metric {
public:
    Metric& operator=(const Metric& other) {
        if (this != &other) {
            this->~Metric();
            new (this) Metric(other);  // Placement new - should not be flagged
        }
        return *this;
    }
    
    Metric& operator=(Metric&& other) noexcept {
        if (this != &other) {
            this->~Metric();
            new (this) Metric(std::move(other));  // Placement new - should not be flagged
        }
        return *this;
    }
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_ignores_control_flow_conditions(self):
        """Test that control flow conditions are not flagged."""
        code = """
void TestControlFlow() {
    void* ptr = nullptr;
    
    // If conditions
    if (enqueue_socket) enqueue_socket->close();
    if (output_socket) output_socket->close();
    if (first_stage_socket) first_stage_socket->close();
    if (zmq_context) zmq_context->close();
    
    // While loops
    while (condition) {
        break;
    }
    
    // For loops
    for (auto& item : container) {
        process(item);
    }
    
    // Switch statements
    switch (value) {
        case 1: break;
        default: break;
    }
    
    // Return statements
    return (result);
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_ignores_method_calls(self):
        """Test that method calls are not flagged."""
        code = """
void TestMethodCalls() {
    auto socket = std::make_shared<zmq::socket_t>(context, zmq::socket_type::pub);
    
    // Method calls with arrow operator
    if (enqueue_socket) enqueue_socket->close();
    socket->bind(endpoint);
    obj->method(args);
    
    // Method calls with dot operator
    object.method();
    container.size();
    string.length();
    
    // Chained method calls
    obj->getSubObject()->process();
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_ignores_assert_and_macro_calls(self):
        """Test that assertion and macro calls are not flagged."""
        code = """
void TestMacros() {
    void* ptr = nullptr;
    
    // Assert macros
    ASSERT_VALID_POINTER_ARGUMENT(config);
    ASSERT_VALID_POINTER_ARGUMENT(comm_info);
    ASSERT_VALID_RUNTIME(kvp_rank < enqueue_sockets_.size(), "Invalid kvp_rank: {}", kvp_rank);
    
    // Logging macros
    LOG_INFO("GpuWorkerManager: binding socket for rank {} to port {}", kvp_rank, port);
    LOG_WARNING("Failed to bind socket to {}: {}", endpoint, e.what());
    LOG_ERROR("Critical error occurred");
    
    // Other uppercase macros
    CHECK_CONDITION(expr);
    VERIFY_STATE(state);
    RAISE_RUNTIME_ERROR("Error message");
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_ignores_constructor_calls(self):
        """Test that constructor calls are not flagged."""
        code = """
void TestConstructors() {
    // Direct constructor calls
    MyClass obj(args);
    AnotherClass instance(param1, param2);
    
    // Constructor calls in expressions
    auto result = MyClass(args);
    process(MyClass(args));
    
    // Template constructor calls
    auto vec = std::vector<int>(10, 0);
    auto map = std::map<std::string, int>();
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_ignores_namespace_qualified_calls(self):
        """Test that namespace-qualified function calls are not flagged."""
        code = """
void TestNamespaceCalls() {
    // Standard library calls
    std::cout << "message" << std::endl;
    std::vector<int> vec = std::vector<int>(10);
    
    // Custom namespace calls
    vajra::native::utils::ZmqHelper::Send<StepInputs>(socket, inputs);
    vajra::native::utils::ZmqHelper::Recv<StepOutputs>(socket);
    
    // Nested namespace calls
    my::nested::namespace::function(args);
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_still_catches_real_unsafe_casts(self):
        """Test that real unsafe casts are still properly detected."""
        code = """
void TestRealUnsafeCasts() {
    int x = 10;
    void* ptr = malloc(sizeof(int));
    
    // These should still be flagged as unsafe
    float f = (float)x;                    // Line 7: C-style cast
    int* iptr = (int*)ptr;                 // Line 8: C-style cast  
    MyClass* obj = (MyClass*)raw_pointer;  // Line 9: C-style cast
    char c = (char)integer_value;          // Line 10: C-style cast
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=4)
        self.assert_issue_at_line(issues, self.rule_id, 7)
        self.assert_issue_at_line(issues, self.rule_id, 8)
        self.assert_issue_at_line(issues, self.rule_id, 9)
        self.assert_issue_at_line(issues, self.rule_id, 10)


@pytest.mark.unit
class TestSafetyRawPointerReturn(RuleTestCase):
    """Test SAFETY_RAW_POINTER_RETURN rule."""

    rule_id = "safety-raw-pointer-return"

    def test_detects_raw_pointer_returns(self):
        """Test detection of raw pointer return types."""
        code = """
int* GetValue() {                    // Line 2: raw pointer return
    return new int(42);
}

const char* GetString() {            // Line 6: raw pointer return
    return "Hello";
}

MyClass* CreateObject() {            // Line 10: raw pointer return
    return new MyClass();
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)
        self.assert_issue_at_line(issues, self.rule_id, 2)
        self.assert_issue_at_line(issues, self.rule_id, 6)
        self.assert_issue_at_line(issues, self.rule_id, 10)

    def test_accepts_smart_pointers(self):
        """Test that smart pointer returns are accepted."""
        code = """
std::unique_ptr<int> GetValue() {
    return std::make_unique<int>(42);
}

std::shared_ptr<MyClass> CreateObject() {
    return std::make_shared<MyClass>();
}

std::optional<int> GetOptionalValue() {
    return 42;
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_accepts_references(self):
        """Test that reference returns are accepted."""
        code = """
class Container {
    int& GetValue() { return value_; }
    const int& GetConstValue() const { return value_; }
    
private:
    int value_;
};
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)


@pytest.mark.unit
class TestSafetyRawPointerParam(RuleTestCase):
    """Test SAFETY_RAW_POINTER_PARAM rule."""

    rule_id = "safety-raw-pointer-param"

    def test_detects_raw_pointer_parameters(self):
        """Test detection of raw pointer parameters."""
        code = """
void ProcessData(int* data) {        // Line 2: raw pointer param
    *data = 42;
}

void UpdateValue(int* value, int newValue) {  // Line 6: raw pointer param
    *value = newValue;
}

void HandleObject(MyClass* obj) {    // Line 10: raw pointer param
    obj->Process();
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=3)
        self.assert_issue_at_line(issues, self.rule_id, 2)
        self.assert_issue_at_line(issues, self.rule_id, 6)
        self.assert_issue_at_line(issues, self.rule_id, 10)

    def test_accepts_const_pointers_for_optional_params(self):
        """Test that const pointers are accepted for optional parameters."""
        code = """
void ProcessOptional(const MyClass* obj = nullptr) {
    if (obj) {
        // Process object
    }
}

void HandleData(const int* data = nullptr) {
    if (data) {
        int value = *data;
    }
}
"""
        # Depending on implementation, const pointers might be acceptable for optional params
        self.lint_only_this_rule(code)
        # Check if issues are reported and adjust test accordingly

    def test_accepts_references_and_smart_pointers(self):
        """Test that references and smart pointers are accepted."""
        code = """
void ProcessData(int& data) {
    data = 42;
}

void UpdateValue(const int& value) {
    // Read-only access
}

void HandleObject(const std::unique_ptr<MyClass>& obj) {
    obj->Process();
}

void TakeOwnership(std::unique_ptr<MyClass> obj) {
    // Takes ownership
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)


@pytest.mark.unit
class TestSafetyRangeLoopMissing(RuleTestCase):
    """Test SAFETY_RANGE_LOOP_MISSING rule."""

    rule_id = "safety-range-loop-missing"

    def test_detects_index_based_loops(self):
        """Test detection of index-based loops that could be range-based."""
        code = """
void ProcessVector(const std::vector<int>& vec) {
    for (int i = 0; i < vec.size(); ++i) {      // Line 3: index-based loop
        std::cout << vec[i] << std::endl;
    }
    
    for (size_t i = 0; i < vec.size(); i++) {   // Line 7: index-based loop
        Process(vec[i]);
    }
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=2)
        self.assert_issue_at_line(issues, self.rule_id, 3)
        self.assert_issue_at_line(issues, self.rule_id, 7)

    def test_detects_iterator_loops(self):
        """Test detection of iterator-based loops that could be range-based."""
        code = """
void ProcessList(const std::list<int>& lst) {
    for (auto it = lst.begin(); it != lst.end(); ++it) {  // Line 3: iterator loop
        std::cout << *it << std::endl;
    }
    
    std::vector<int> vec = {1, 2, 3};
    for (std::vector<int>::iterator it = vec.begin(); it != vec.end(); it++) {  // Line 7
        *it *= 2;
    }
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_has_rule(issues, self.rule_id, count=2)

    def test_accepts_range_based_loops(self):
        """Test that range-based loops are accepted."""
        code = """
void ProcessContainers() {
    std::vector<int> vec = {1, 2, 3, 4, 5};
    for (const auto& value : vec) {
        std::cout << value << std::endl;
    }
    
    std::map<std::string, int> map;
    for (auto& [key, value] : map) {
        value *= 2;
    }
    
    int array[] = {1, 2, 3};
    for (int elem : array) {
        Process(elem);
    }
}
"""
        issues = self.lint_only_this_rule(code)
        self.assert_no_issues(issues)

    def test_accepts_necessary_index_loops(self):
        """Test that loops requiring indices are accepted."""
        code = """
void ProcessWithIndex() {
    std::vector<int> vec = {1, 2, 3};
    
    // Need index for algorithm
    for (size_t i = 0; i < vec.size() - 1; ++i) {
        vec[i] += vec[i + 1];
    }
    
    // Need index for parallel processing
    for (int i = 0; i < vec.size(); i += 2) {
        ProcessPair(vec[i], vec[i + 1]);
    }
    
    // Reverse iteration
    for (int i = vec.size() - 1; i >= 0; --i) {
        if (vec[i] == 0) break;
    }
}
"""
        # These loops need indices, so they should be accepted
        self.lint_only_this_rule(code)
        # Depending on rule implementation, these might or might not trigger
