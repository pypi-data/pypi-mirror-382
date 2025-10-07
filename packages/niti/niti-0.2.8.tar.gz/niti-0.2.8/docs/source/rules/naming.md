# Naming Conventions

Consistent naming conventions improve code readability and maintainability. Niti enforces various naming patterns for different C++ constructs.

## Function Names

<div class="rule-card">
<h3 class="rule-title">NAMING_FUNCTION_CASE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_FUNCTION_CASE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Functions should use PascalCase naming convention to clearly indicate their purpose and improve readability.
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
// Functions use PascalCase
void ProcessRequest(const Request& req) {
    // Implementation
}

std::string FormatOutput(const Data& data) {
    return data.ToString();
}

bool ValidateInput(const std::string& input) {
    return !input.empty();
}
```

</div>
<div class="code-bad">

```cpp
// Functions use snake_case or other formats
void process_request(const Request& req) {
    // Implementation
}

std::string formatOutput(const Data& data) {
    return data.ToString();
}

bool validate_input(const std::string& input) {
    return !input.empty();
}
```

</div>
</div>
</div>
</div>

## Function Verbs

<div class="rule-card">
<h3 class="rule-title">NAMING_FUNCTION_VERB</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_FUNCTION_VERB</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Functions should start with action verbs to clearly indicate their purpose and what they do. The Full List of action verbs supported by our linted are: 

| Category      | Verbs                                                                                                                             |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------|
| **Creation**  | `Create`, `Build`, `Generate`, `Make`, `New`, `Allocate`                                                                          |
| **Access**    | `Get`, `Set`, `Read`, `Write`, `Load`, `Save`, `Open`, `Close`                                                                    |
| **Lifecycle** | `Start`, `Stop`, `Run`, `Execute`, `Launch`, `Initialize`, `Init`, `Setup`, `Cleanup`, `Reset`, `Clear`                             |
| **State**     | `Is`, `Has`, `Can`, `Should`, `Will`, `Enable`, `Disable`, `Show`, `Hide`, `Connect`, `Disconnect`                                  |
| **Mutation**  | `Update`, `Modify`, `Change`, `Add`, `Remove`, `Insert`, `Delete`, `Transform`, `Convert`, `Format`, `Parse`                        |
| **Logic**     | `Calculate`, `Compute`, `Process`, `Handle`, `Check`, `Validate`, `Verify`, `Test`, `Compare`, `Find`, `Search`, `Filter`, `Sort` |
| **Events**    | `Send`, `Receive`, `Emit`, `Listen`, `Watch`, `Monitor`, `Track`, `Register`, `Unregister`, `Subscribe`, `Unsubscribe`, `Notify`   |
| **Invocation**| `Invoke`, `Call`, `Apply`, `Trigger`, `Fire`                                                                                      |
</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// Functions start with verbs
void CreateConnection() { }
bool ValidateCredentials() { }
std::string GetUserName() { }
void SetConfiguration() { }
void ProcessData() { }
bool IsValid() { }
bool HasPermission() { }
void UpdateCache() { }
```

</div>
<div class="code-bad">

```cpp
// Functions don't start with verbs
void Connection() { }
bool Credentials() { }
std::string UserName() { }
void Configuration() { }
void Data() { }
bool Valid() { }
bool Permission() { }
void Cache() { }
```

</div>
</div>
</div>
</div>

## Variable Names

<div class="rule-card">
<h3 class="rule-title">NAMING_VARIABLE_CASE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_VARIABLE_CASE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Variables should use snake_case naming convention for consistency and readability.
</div>

**Examples:**

<div class="code-comparison-container">
<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// Variables use snake_case
int user_count = 0;
std::string file_path = "/tmp/data.txt";
bool is_valid = true;
double max_value = 100.0;

// Local variables
for (size_t loop_index = 0; loop_index < size; ++loop_index) {
    auto current_item = container[loop_index];
    process_item(current_item);
}
```

</div>
<div class="code-bad">

```cpp
// Variables use CamelCase or other formats
int UserCount = 0;
std::string filePath = "/tmp/data.txt";
bool IsValid = true;
double maxValue = 100.0;

// Local variables
for (size_t LoopIndex = 0; LoopIndex < size; ++LoopIndex) {
    auto CurrentItem = container[LoopIndex];
    process_item(CurrentItem);
}
```

</div>
</div>
</div>
</div>

## Class Names

<div class="rule-card">
<h3 class="rule-title">NAMING_CLASS_CASE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_CLASS_CASE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Classes should use PascalCase naming convention to distinguish them from variables and functions.
</div>

**Examples:**

<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// Classes use PascalCase
class DatabaseConnection {
public:
    void Connect();
    void Disconnect();
};

class HttpServer {
private:
    int port_;
    std::string address_;
};

class ConfigurationManager {
public:
    void LoadConfig();
    void SaveConfig();
};
```

</div>
<div class="code-bad">

```cpp
// Classes use snake_case or other formats
class database_connection {
public:
    void Connect();
    void Disconnect();
};

class http_server {
private:
    int port_;
    std::string address_;
};

class configurationmanager {
public:
    void LoadConfig();
    void SaveConfig();
};
```

</div>
</div>
</div>

## Struct Names

<div class="rule-card">
<h3 class="rule-title">NAMING_STRUCT_CASE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_STRUCT_CASE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Structs should use PascalCase naming convention, similar to classes.
</div>

**Examples:**

<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// Structs use PascalCase
struct Point {
    double x;
    double y;
};

struct UserData {
    std::string name;
    int age;
    std::string email;
};

struct ConfigOption {
    std::string key;
    std::string value;
    bool is_required;
};
```

</div>
<div class="code-bad">

```cpp
// Structs use snake_case or other formats
struct point {
    double x;
    double y;
};

struct user_data {
    std::string name;
    int age;
    std::string email;
};

struct config_option {
    std::string key;
    std::string value;
    bool is_required;
};
```

</div>
</div>
</div>

## Member Variables

<div class="rule-card">
<h3 class="rule-title">NAMING_MEMBER_CASE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_MEMBER_CASE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Private and protected member variables should use snake_case with a trailing underscore to distinguish them from local variables.
</div>

**Examples:**

<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
class HttpServer {
private:
    // Member variables with trailing underscore
    int port_;
    std::string server_address_;
    bool is_running_;
    std::vector<Connection> active_connections_;
    
public:
    void SetPort(int port) {
        port_ = port;  // Clear distinction
    }
};
```

</div>
<div class="code-bad">

```cpp
class HttpServer {
private:
    // Member variables without trailing underscore
    int port;
    std::string serverAddress;
    bool isRunning;
    std::vector<Connection> activeConnections;
    
public:
    void SetPort(int port) {
        this->port = port;  // Requires 'this->'
    }
};
```

</div>
</div>
</div>

## Constants

<div class="rule-card">
<h3 class="rule-title">NAMING_CONSTANT_CASE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_CONSTANT_CASE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Constants should use kPascalCase naming convention to clearly identify them as compile-time constants.
</div>

**Examples:**

<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// Constants use kPascalCase
const int kMaxConnections = 100;
const std::string kDefaultHost = "localhost";
const double kTimeoutSeconds = 30.0;

constexpr size_t kBufferSize = 4096;
constexpr int kRetryCount = 3;
```

</div>
<div class="code-bad">

```cpp
// Constants use other naming conventions
const int MAX_CONNECTIONS = 100;
const std::string default_host = "localhost";
const double timeoutSeconds = 30.0;

constexpr size_t BUFFER_SIZE = 4096;
constexpr int retryCount = 3;

// In class context
class Config {
public:
    static const int DEFAULT_PORT = 8080;
    static const std::string config_file = "config.yml";
};
```

</div>
</div>
</div>


## Enums

<div class="rule-card">
<h3 class="rule-title">NAMING_ENUM_CASE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_ENUM_CASE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Enum class names should use PascalCase, while C-style enum names should use snake_case.
</div>

**Examples:**

<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// enum class uses PascalCase
enum class ConnectionStatus {
    Disconnected,
    Connecting,
    Connected,
    Failed
};

enum class LogLevel {
    Debug,
    Info,
    Warning,
    Error
};

// C-style enum uses snake_case (NOT RECOMMENDED)
enum connection_type {
    TCP_CONNECTION,
    UDP_CONNECTION,
    WEBSOCKET_CONNECTION
};
```

</div>
<div class="code-bad">

```cpp
// enum class uses snake_case
enum class connection_status {
    Disconnected,
    Connecting,
    Connected,
    Failed
};

// enum class uses inconsistent naming
enum class loglevel {
    Debug,
    Info,
    Warning,
    Error
};

// C-style enum uses CamelCase
enum ConnectionType {
    TCP_CONNECTION,
    UDP_CONNECTION,
    WEBSOCKET_CONNECTION
};
```

</div>
</div>
</div>

## Enum Values

<div class="rule-card">
<h3 class="rule-title">NAMING_ENUM_VALUE_CASE</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_ENUM_VALUE_CASE</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Enum class values should use kPascalCase, while C-style enum (NOT RECOMMENDED) values should use UPPER_CASE.
</div>

**Examples:**

<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// enum class values use PascalCase
enum class Status {
    kWaiting,
    kProcessing,
    kCompleted,
    kFailed
};

enum class NetworkState {
    kOffline,
    kConnecting,
    kOnline,
    kDisconnecting
};

// C-style enum values use UPPER_CASE
enum error_code {
    SUCCESS = 0,
    INVALID_INPUT = 1,
    NETWORK_ERROR = 2,
    TIMEOUT_ERROR = 3
};
```

</div>
<div class="code-bad">

```cpp
// enum class values use UPPER_CASE
enum class Status {
    WAITING,
    PROCESSING,
    COMPLETED,
    FAILED
};

// enum class values use snake_case
enum class NetworkState {
    offline,
    connecting,
    online,
    disconnecting
};

// C-style enum values use PascalCase
enum error_code {
    Success = 0,
    InvalidInput = 1,
    NetworkError = 2,
    TimeoutError = 3
};
```

</div>
</div>
</div>

## Hungarian Notation

<div class="rule-card">
<h3 class="rule-title">NAMING_HUNGARIAN_NOTATION</h3>
<div class="rule-metadata">
    <span class="rule-id">Rule ID: NAMING_HUNGARIAN_NOTATION</span>
    <span class="severity-badge severity-error">Error</span>
</div>
<div class="rule-description">
Hungarian notation is forbidden as it reduces code readability and is unnecessary in modern C++ with strong typing.
</div>

**Examples:**

<div class="code-comparison-header">
<div class="good-header">✅ Correct</div>
<div class="bad-header">❌ Incorrect</div>
</div>
<div class="code-comparison">
<div class="code-good">

```cpp
// Clean variable names without type prefixes
std::string name = "John";
int count = 10;
bool is_valid = true;
std::vector<int> numbers;
User* user = nullptr;

// Function parameters
void ProcessData(const std::string& input, 
                 int buffer_size,
                 bool should_validate) {
    // Implementation
}
```

</div>
<div class="code-bad">

```cpp
// Hungarian notation with type prefixes
std::string strName = "John";
int nCount = 10;
bool bIsValid = true;
std::vector<int> arrNumbers;
User* pUser = nullptr;

// Function parameters with prefixes
void ProcessData(const std::string& szInput,
                 int nBufferSize,
                 bool bShouldValidate) {
    // Implementation
}
```

</div>
</div>
</div>

## Summary

Following consistent naming conventions helps create maintainable and readable code. The key principles are:

- **Functions**: PascalCase and start with verbs
- **Variables**: snake_case for locals, snake_case_ for members
- **Classes/Structs**: CamelCase
- **Constants**: kPascalCase or UPPER_CASE
- **Enums**: CamelCase for enum class, snake_case for C-style
- **Enum Values**: PascalCase for enum class, UPPER_CASE for C-style
- **Avoid**: Hungarian notation and inconsistent patterns

These conventions improve code clarity and make it easier for teams to collaborate effectively.