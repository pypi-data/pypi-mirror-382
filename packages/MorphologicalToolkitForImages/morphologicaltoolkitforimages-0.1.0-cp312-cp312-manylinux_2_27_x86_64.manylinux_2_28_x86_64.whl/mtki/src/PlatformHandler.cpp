#include "../include/PlatformHandler.hpp"

#if defined(__linux__)
    #include <malloc.h>
#endif

namespace platform{
    void free_unused_memory(){
        #if defined(__linux__)
            malloc_trim(0);
        #else
        #endif
    }

    void print_platform() {
        std::cout << "PLATFORM: ";
        #if defined(__linux__)
            std::cout << "Linux: 1\nMacOS: 0\nWindows: 0\n";
        #elif defined(__APPLE__)
            std::cout << "Linux: 0\nMacOS: 1\nWindows: 0\n";
        #elif defined(_WIN32)
            std::cout << "Linux: 0\nMacOS: 0\nWindows: 1\n";
        #else
            std::cout << "Linux: 0\nMacOS: 0\nWindows: 0\n";
        #endif
    }
}