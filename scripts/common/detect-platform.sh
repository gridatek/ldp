#!/bin/bash
# Platform detection utility for cross-platform support

detect_platform() {
    case "$(uname -s)" in
        Darwin*)
            echo "macos"
            ;;
        Linux*)
            echo "linux"
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "windows"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

detect_arch() {
    case "$(uname -m)" in
        x86_64|amd64)
            echo "amd64"
            ;;
        arm64|aarch64)
            echo "arm64"
            ;;
        *)
            echo "$(uname -m)"
            ;;
    esac
}

# Export functions
export -f detect_platform
export -f detect_arch

# If script is run directly, print platform info
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    PLATFORM=$(detect_platform)
    ARCH=$(detect_arch)
    echo "Platform: $PLATFORM"
    echo "Architecture: $ARCH"
fi
