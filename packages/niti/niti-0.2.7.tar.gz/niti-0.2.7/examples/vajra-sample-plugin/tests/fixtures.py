"""Test fixtures for Vajra plugin tests."""


class CppCodeSamples:
    """C++ code samples for testing."""
    
    # PCH Rule Test Cases
    PCH_MISSING = """
#include <vector>
#include <string>
#include "MyClass.h"

namespace vajra {
    void Function() {
        std::vector<int> data;
    }
}
"""
    
    PCH_CORRECT = """
#include "commons/PrecompiledHeaders.h"

#include <vector>
#include <string>
#include "MyClass.h"

namespace vajra {
    void Function() {
        std::vector<int> data;
    }
}
"""
    
    PCH_WRONG_ORDER = """
#include <vector>
#include "commons/PrecompiledHeaders.h"  // Should be first
#include <string>

void Function() {}
"""
    
    PCH_HEADER_FILE = """
#pragma once

#include <vector>
#include <memory>

namespace vajra {
    class Widget {
        std::vector<int> data_;
    };
}
"""
    
    # Forward Declaration Test Cases
    FD_UNNECESSARY_INCLUDES = """
#pragma once

#include "Widget.h"      // Only used as pointer - could forward declare
#include "Component.h"   // Only used as reference - could forward declare  
#include "Data.h"        // Used as member - needs full definition

namespace vajra {
    class Manager {
        Widget* widget_;
        Component& GetComponent();
        Data data_;
    };
}
"""
    
    FD_NECESSARY_INCLUDES = """
#pragma once

#include "Base.h"        // Base class - needs full definition
#include "Member.h"      // Member variable - needs full definition
#include <vector>        // Template instantiation - needs full definition

namespace vajra {
    class Derived : public Base {
        Member member_;
        std::vector<int> data_;
        
        void InlineFunc() {
            member_.Process();  // Inline usage
        }
    };
}
"""
    
    FD_SMART_POINTERS = """
#pragma once

#include <memory>
#include "Resource.h"    // Only in smart pointers - could forward declare
#include "Heavy.h"       // Only in smart pointers - could forward declare

namespace vajra {
    class ResourceManager {
        std::shared_ptr<Resource> resource_;
        std::unique_ptr<Heavy> heavy_;
        
        std::shared_ptr<Resource> GetResource();
    };
}
"""
    
    FD_MIXED_USAGE = """
#pragma once

#include "Used.h"        // Used as value
#include "Pointed.h"     // Only as pointer - could forward declare
#include "Referenced.h"  // Only as reference - could forward declare

namespace vajra {
    class Container {
        Used used_;
        Pointed* ptr_;
        
        const Referenced& GetRef() const;
        void SetRef(const Referenced& ref);
    };
}
"""
    
    # Complex test cases
    COMPLEX_FILE = """
#pragma once

// Missing PCH (if this were a .cpp file)
#include <memory>
#include <vector>

// These could use forward declarations
#include "Manager.h"     // Only pointer usage
#include "Service.h"     // Only reference usage

// These need full definitions
#include "BaseClass.h"   // Inheritance
#include "Member.h"      // Member variable

namespace vajra {

class Component : public BaseClass {
private:
    Member member_;
    Manager* manager_;
    
public:
    Service& GetService();
    void SetManager(Manager* mgr) { manager_ = mgr; }
};

} // namespace vajra
"""