#!/bin/bash

# Drum Control XL - Fetch and Install Script
# Downloads the latest release and installs it automatically

set -e  # Exit on any error

REPO_URL="https://github.com/jonatan-petursson/drum-control-xl"
TEMP_DIR=$(mktemp -d)
SCRIPT_NAME="fetch-and-install.sh"

echo "Drum Control XL - Fetch and Install"
echo "==================================="
echo

# Function to cleanup temporary files
cleanup() {
    echo "🧹 Cleaning up temporary files..."
    rm -rf "$TEMP_DIR"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Function to check if required tools are available
check_dependencies() {
    echo "🔍 Checking dependencies..."

    if ! command -v curl >/dev/null 2>&1; then
        echo "❌ Error: curl is required but not installed"
        exit 1
    fi

    if ! command -v unzip >/dev/null 2>&1; then
        echo "❌ Error: unzip is required but not installed"
        exit 1
    fi

    echo "✅ Dependencies OK"
    echo
}

# Function to get latest release download URL
get_latest_release_url() {
    echo "📡 Fetching latest release information..."

    # Get the latest release info from GitHub API
    local api_url="https://api.github.com/repos/jonatan-petursson/drum-control-xl/releases/latest"
    local release_info

    release_info=$(curl -s "$api_url" 2>/dev/null)

    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to fetch release information from GitHub"
        exit 1
    fi

    # Extract download URL for the zip file
    local download_url
    download_url=$(echo "$release_info" | grep -o '"browser_download_url": "[^"]*\.zip"' | head -n 1 | cut -d '"' -f 4)

    if [ -z "$download_url" ]; then
        echo "❌ Error: No zip file found in latest release"
        exit 1
    fi

    echo "$download_url"
}

# Function to download and extract the repository
download_and_extract() {
    local download_url="$1"

    echo "⬇️  Downloading from: $download_url"

    # Download the file
    local zip_file="$TEMP_DIR/Drum_Control_XL.zip"
    curl -L -o "$zip_file" "$download_url"

    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to download the repository"
        exit 1
    fi

    echo "📦 Extracting files..."

    # Extract the zip file
    cd "$TEMP_DIR"
    unzip -q "$zip_file"

    # Find the extracted directory (it might have different names depending on source)
    local extracted_dir
    extracted_dir=$(find . -type d -name "*drum-control-xl*" -o -name "*Drum_Control_XL*" | head -n 1)

    if [ -z "$extracted_dir" ]; then
        echo "❌ Error: Could not find extracted directory"
        exit 1
    fi

    echo "✅ Files extracted to: $extracted_dir"
    echo "$TEMP_DIR/$extracted_dir"
}

# Function to run the installer
run_installer() {
    local source_dir="$1"

    echo "🚀 Running installer..."
    echo

    # Check if install_macos.sh exists
    if [ ! -f "$source_dir/scripts/install-macos.sh" ]; then
        echo "❌ Error: install-macos.sh not found in the extracted files"
        echo "   Expected location: $source_dir/scripts/install_macos.sh"
        exit 1
    fi

    # Make the installer executable
    chmod +x "$source_dir/scripts/install_macos.sh"

    # Change to the source directory and run the installer
    cd "$source_dir/Drum_Control_XL"
    ../scripts/install_macos.sh
}

# Main execution
main() {
    echo "Starting automated installation of Drum Control XL..."
    echo

    # Check dependencies
    check_dependencies

    # Get download URL
    get_latest_release_url
    download_url=$?

    # Download and extract
    source_dir=$(download_and_extract "$download_url")

    # Run the installer
    run_installer "$source_dir"

    echo
    echo "🎉 Installation completed successfully!"
    echo
    echo "The temporary files will be cleaned up automatically."
    echo "You can now configure Drum Control XL in Ableton Live:"
    echo "  1. Open Ableton Live"
    echo "  2. Go to Live > Preferences > Link/Tempo/MIDI"
    echo "  3. Select 'Drum Control XL' in Control Surface dropdown"
    echo "  4. Set Input/Output to your Launch Control XL"
}

# Check if we're running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script is designed for macOS only"
    echo "   For other platforms, please follow the manual installation instructions"
    exit 1
fi

# Run main function
main "$@"
