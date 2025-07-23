#!/bin/bash
set -e

echo "Drum Control XL Installer for macOS"
echo "==================================="

# Check if we're in the scripts/ folder or scripts/.. folder
if [ -d "Drum_Control_XL" ]; then
    # We're in the parent directory containing Drum_Control_XL
    SOURCE_DIR="Drum_Control_XL"
elif [ -d "../Drum_Control_XL" ]; then
    # We're in a subdirectory, Drum_Control_XL is one level up
    SOURCE_DIR="../Drum_Control_XL"
else
    echo "Error: Please run this script from either the directory containing the Drum_Control_XL folder or from a subdirectory within it"
    exit 1
fi

ABLETON_DIRS=$(find /Applications -name "Ableton Live*" -type d -maxdepth 1 2>/dev/null | sort -r)

if [ -z "$ABLETON_DIRS" ]; then
    echo "Error: No Ableton Live installations found in /Applications"
    exit 1
fi

echo "📁 Found Ableton Live installations:"
echo "$ABLETON_DIRS"
echo

ABLETON_DIR=$(echo "$ABLETON_DIRS" | head -n 1)
SCRIPTS_DIR="$ABLETON_DIR/Contents/App-Resources/MIDI Remote Scripts"

# Check if scripts directory exists
if [ ! -d "$SCRIPTS_DIR" ]; then
    echo "❌ Error: MIDI Remote Scripts directory not found at:"
    echo "   $SCRIPTS_DIR"
    exit 1
fi

echo "🎯 Installing to: $SCRIPTS_DIR"

echo "📋 Preparing installation..."
DEST_DIR="$SCRIPTS_DIR/Drum_Control_XL"

# Check versions
if [ -f "$SOURCE_DIR/VERSION" ]; then
    NEW_VERSION=$(cat "$SOURCE_DIR/VERSION")
    echo "📦 New version: $NEW_VERSION"
else
    echo "⚠️  Warning: No VERSION file found in source directory"
    NEW_VERSION="unknown"
fi

if [ -d "$DEST_DIR" ]; then
    if [ -f "$DEST_DIR/VERSION" ]; then
        CURRENT_VERSION=$(cat "$DEST_DIR/VERSION")
        echo "📍 Current version: $CURRENT_VERSION"
    else
        echo "📍 Current version: unknown (no VERSION file)"
        CURRENT_VERSION="unknown"
    fi

    echo
    echo "🔄 This will replace the existing installation."
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled."
        exit 0
    fi

    echo "🗑️  Removing existing installation..."
    rm -rf "$DEST_DIR"
else
    echo "📍 No existing installation found."
    echo
    read -p "Do you want to install Drum Control XL $NEW_VERSION? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled."
        exit 0
    fi
fi

echo "📋 Copying files..."
cp -r "$SOURCE_DIR" "$SCRIPTS_DIR"

echo "✅ Installation complete!"
echo
echo "Next steps:"
echo "1. Open Ableton Live"
echo "2. Go to Live > Preferences > Link/Tempo/MIDI"
echo "3. Select 'Drum Control XL' in Control Surface dropdown"
echo "4. Set Input/Output to your Launch Control XL"
