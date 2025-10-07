"""Common C++ code samples for testing."""


class CppSamples:
    """Collection of C++ code samples for testing various rules."""

    # === Type System Samples ===
    TYPE_FORBIDDEN_INT_BAD = """
int count = 0;
unsigned int flags = 1;
long value = 42;
short small_value = 10;
unsigned long large_value = 100;

void ProcessData(int data) {
    int result = data * 2;
}
"""

    TYPE_FORBIDDEN_INT_GOOD = """
std::int32_t count = 0;
std::uint32_t flags = 1;
std::int64_t value = 42;
std::int16_t small_value = 10;
std::uint64_t large_value = 100;

void ProcessData(std::int32_t data) {
    std::int32_t result = data * 2;
}
"""

    TYPE_PAIR_TUPLE_BAD = """
std::pair<int, string> GetUserInfo() {
    return std::make_pair(123, "John");
}

std::tuple<int, string, bool> GetExtendedInfo() {
    return std::make_tuple(123, "John", true);
}
"""

    TYPE_PAIR_TUPLE_GOOD = """
struct UserInfo {
    std::int32_t id;
    std::string name;
};

UserInfo GetUserInfo() {
    return {123, "John"};
}

struct ExtendedInfo {
    std::int32_t id;
    std::string name;
    bool active;
};

ExtendedInfo GetExtendedInfo() {
    return {123, "John", true};
}
"""

    # === Naming Convention Samples ===
    NAMING_FUNCTION_CASE_BAD = """
void process_data() {}  // Bad: snake_case
void processdata() {}   // Bad: all lowercase
void PROCESSDATA() {}   // Bad: all uppercase
"""

    NAMING_FUNCTION_CASE_GOOD = """
void ProcessData() {}   // Good: CamelCase
void GetUserInfo() {}   // Good: CamelCase
void CalculateSum() {}  // Good: CamelCase
"""

    NAMING_VARIABLE_CASE_BAD = """
int CountItems = 0;     // Bad: CamelCase
int countitems = 0;     // Bad: no separators
int COUNTITEMS = 0;     // Bad: all uppercase
"""

    NAMING_VARIABLE_CASE_GOOD = """
int count_items = 0;    // Good: snake_case
int user_count = 0;     // Good: snake_case
int max_value = 100;    // Good: snake_case
"""

    NAMING_CLASS_CASE_BAD = """
class user_manager {};  // Bad: snake_case
class usermanager {};   // Bad: all lowercase
class USERMANAGER {};   // Bad: all uppercase
"""

    NAMING_CLASS_CASE_GOOD = """
class UserManager {};   // Good: CamelCase
class DataProcessor {}; // Good: CamelCase
class FileHandler {};   // Good: CamelCase
"""

    NAMING_MEMBER_CASE_BAD = """
class Example {
private:
    int memberVariable;    // Bad: no trailing underscore
    int member_variable;   // Bad: no trailing underscore
    int m_memberVariable;  // Bad: Hungarian notation
};
"""

    NAMING_MEMBER_CASE_GOOD = """
class Example {
private:
    int member_variable_;   // Good: snake_case with trailing underscore
    int count_;            // Good: snake_case with trailing underscore
    std::string name_;     // Good: snake_case with trailing underscore
};
"""

    # === Safety Rules Samples ===
    SAFETY_UNSAFE_CAST_BAD = """
void UnsafeCasts() {
    int* ptr = (int*)malloc(sizeof(int));  // C-style cast
    void* vptr = ptr;
    char* cptr = reinterpret_cast<char*>(ptr);  // reinterpret_cast
}
"""

    SAFETY_UNSAFE_CAST_GOOD = """
void SafeCasts() {
    int* ptr = static_cast<int*>(malloc(sizeof(int)));
    void* vptr = static_cast<void*>(ptr);
    // Use proper type conversion instead of reinterpret_cast
}
"""

    SAFETY_RAW_POINTER_BAD = """
int* GetData() {
    return new int(42);
}

void ProcessData(int* data) {
    *data = 100;
}
"""

    SAFETY_RAW_POINTER_GOOD = """
std::unique_ptr<int> GetData() {
    return std::make_unique<int>(42);
}

void ProcessData(const std::unique_ptr<int>& data) {
    *data = 100;
}
"""

    # === Modern C++ Samples ===
    MODERN_MISSING_NOEXCEPT_BAD = """
class Example {
public:
    Example() {}  // Missing noexcept
    ~Example() {} // Missing noexcept (defaulted)
    
    int GetValue() const { return value_; }  // Could be noexcept
    
private:
    int value_ = 0;
};
"""

    MODERN_MISSING_NOEXCEPT_GOOD = """
class Example {
public:
    Example() noexcept = default;
    ~Example() = default;  // Implicitly noexcept
    
    int GetValue() const noexcept { return value_; }
    
private:
    int value_ = 0;
};
"""

    MODERN_NODISCARD_MISSING_BAD = """
int CalculateSum(int a, int b) {
    return a + b;
}

bool IsValid() const {
    return true;
}
"""

    MODERN_NODISCARD_MISSING_GOOD = """
[[nodiscard]] int CalculateSum(int a, int b) {
    return a + b;
}

[[nodiscard]] bool IsValid() const {
    return true;
}
"""

    # === Documentation Samples ===
    DOC_FUNCTION_MISSING_BAD = """
public:
    void ProcessData(const std::vector<int>& data);
    int CalculateSum(int a, int b);
    bool ValidateInput(const std::string& input);
"""

    DOC_FUNCTION_MISSING_GOOD = """
public:
    /**
     * @brief Process the given data vector
     * @param data Input data to process (in)
     */
    void ProcessData(const std::vector<int>& data);
    
    /**
     * @brief Calculate sum of two integers
     * @param a First integer (in)
     * @param b Second integer (in)
     * @return Sum of a and b
     */
    int CalculateSum(int a, int b);
    
    /**
     * @brief Validate the input string
     * @param input String to validate (in)
     * @return True if valid, false otherwise
     */
    bool ValidateInput(const std::string& input);
"""

    DOC_CLASS_MISSING_BAD = """
class DataProcessor {
public:
    void Process();
};

struct Point {
    int x, y;
};

enum class Status {
    Running,
    Stopped
};
"""

    DOC_CLASS_MISSING_GOOD = """
/**
 * @brief Processes data in batches
 */
class DataProcessor {
public:
    void Process();
};

/**
 * @brief Represents a 2D point
 */
struct Point {
    int x, y;
};

/**
 * @brief System status enumeration
 */
enum class Status {
    Running,
    Stopped
};
"""

    # === Class Trait Samples ===
    CLASS_TRAIT_MISSING_BAD = """
class UserManager {
public:
    void AddUser(const std::string& name);
};

class DataProcessor {
public:
    void Process();
};
"""

    CLASS_TRAIT_MISSING_GOOD = """
class UserManager : public NonCopyableNonMovable {
public:
    void AddUser(const std::string& name);
};

class DataProcessor : public NonCopyable {
public:
    void Process();
};
"""

    # === Include Order Samples ===
    INCLUDE_ORDER_WRONG_BAD = """
#include <vector>
#include "MyClass.h"
#include <string>
#include "commons/PrecompiledHeaders.h"
#include <iostream>
"""

    INCLUDE_ORDER_WRONG_GOOD = """
#include "commons/PrecompiledHeaders.h"

#include <iostream>
#include <string>
#include <vector>

#include "MyClass.h"
"""
