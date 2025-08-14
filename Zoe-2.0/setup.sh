#!/bin/bash

# --- Setup Script for Zoe-2.0 on Linux/macOS ---

echo "Starting Zoe-2.0 Native Host Setup..."

# Get the absolute path to the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
HOST_WRAPPER_PATH="$SCRIPT_DIR/code/python/zoe_native_host_wrapper.sh"
MANIFEST_NAME="com.zoe.native_host.json"

# --- Step 1: Install Python Dependencies ---
echo ""
echo "[1/3] Installing Python dependencies..."
if command -v python3 &> /dev/null && command -v pip &> /dev/null; then
    pip install -r "$SCRIPT_DIR/code/python/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install Python dependencies. Please check your pip and Python installation."
        exit 1
    fi
    echo "Dependencies installed successfully."
else
    echo "WARNING: python3 or pip not found. Please install them and run this script again, or install the dependencies manually from requirements.txt."
fi

# --- Step 2: Determine Native Messaging Host Path ---
echo ""
echo "[2/3] Detecting browser and OS for Native Host installation..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    TARGET_DIR_CHROME="$HOME/.config/google-chrome/NativeMessagingHosts"
    TARGET_DIR_CHROMIUM="$HOME/.config/chromium/NativeMessagingHosts"
    TARGET_DIR=$TARGET_DIR_CHROME # Default to Chrome
    if [ -d "$TARGET_DIR_CHROMIUM" ]; then
        echo "Found Chromium directory. You can also manually copy the manifest there if needed."
        # If chrome is not present, use chromium
        if [ ! -d "$TARGET_DIR_CHROME" ]; then
            TARGET_DIR=$TARGET_DIR_CHROMIUM
        fi
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    TARGET_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
else
    echo "ERROR: Unsupported OS '$OSTYPE'. This script is for Linux and macOS."
    exit 1
fi

echo "Target directory for manifest: $TARGET_DIR"

# --- Step 3: Create and Install the Manifest ---
echo ""
echo "[3/3] Creating and installing the Native Host manifest..."
mkdir -p "$TARGET_DIR"

# Create the manifest content, replacing the path placeholder
MANIFEST_CONTENT="{
  \"name\": \"com.zoe.native_host\",
  \"description\": \"Zoe Native Messaging Host\",
  \"path\": \"$HOST_WRAPPER_PATH\",
  \"type\": \"stdio\",
  \"allowed_origins\": [
    \"chrome-extension://SEU_ID_DA_EXTENSAO_AQUI/\"
  ]
}"

# Write the manifest to the target directory
echo "$MANIFEST_CONTENT" > "$TARGET_DIR/$MANIFEST_NAME"
chmod 644 "$TARGET_DIR/$MANIFEST_NAME"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to write the manifest file to $TARGET_DIR."
    echo "You may need to run this script with sudo, or create the directory and file manually."
    exit 1
fi

echo "Manifest file created successfully!"
echo ""
echo "--- SETUP COMPLETE ---"
echo ""
echo "IMPORTANT FINAL STEP:"
echo "1. Load the extension from the 'Zoe-2.0/code/extension' directory in Chrome/Chromium (use 'Load unpacked')."
echo "2. After loading, Chrome will assign it an ID. Copy this ID."
echo "3. Open the file: $TARGET_DIR/$MANIFEST_NAME"
echo "4. Replace 'SEU_ID_DA_EXTENSAO_AQUI' with the ID you copied."
echo "5. Restart Chrome for the changes to take effect."
echo ""
echo "Zoe is now ready to be used!"
