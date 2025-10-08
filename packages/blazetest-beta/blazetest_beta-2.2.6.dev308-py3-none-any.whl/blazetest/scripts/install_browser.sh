#!/bin/bash
# Browser Installation Script for BlazeTest
# Supports Chrome and Firefox installation with version control

set -e

BROWSER_TYPE="${1:-chrome}"
BROWSER_VERSION="${2:-latest}"

echo "Installing $BROWSER_TYPE browser (version: $BROWSER_VERSION)"

install_chrome() {
    local version=$1
    
    echo "Installing Chrome dependencies..."
    yum install -y wget unzip gtk3 libXScrnSaver GConf2 alsa-lib xorg-x11-server-Xvfb \
        liberation-fonts nss atk at-spi2-atk cups-libs libdrm libXcomposite \
        libXdamage libXrandr mesa-libgbm
    
    if [ "$version" = "latest" ]; then
        echo "Installing latest Chrome..."
        wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        yum install -y ./google-chrome-stable_current_x86_64.rpm
        rm google-chrome-stable_current_x86_64.rpm
    else
        echo "Installing Chrome version $version..."
        # For specific versions, use the versioned RPM
        wget -q "https://dl.google.com/linux/chrome/rpm/stable/x86_64/google-chrome-stable-${version}-1.x86_64.rpm" || \
        wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
        yum install -y ./google-chrome-stable*.rpm
        rm ./google-chrome-stable*.rpm
    fi
    
    # Verify installation
    if command -v google-chrome &> /dev/null; then
        echo "Chrome installed successfully:"
        google-chrome --version
    else
        echo "Chrome installation failed!"
        exit 1
    fi
    
    # Clean up
    yum clean all
}

install_firefox() {
    local version=$1
    
    echo "Installing Firefox dependencies..."
    yum install -y gtk3 dbus-x11 libXt xorg-x11-server-Xvfb liberation-fonts
    
    if [ "$version" = "latest" ]; then
        echo "Installing latest Firefox..."
        yum install -y firefox
    else
        echo "Installing Firefox version $version..."
        # Try to install specific version, fall back to latest if not available
        yum install -y "firefox-${version}" || yum install -y firefox
    fi
    
    # Verify installation
    if command -v firefox &> /dev/null; then
        echo "Firefox installed successfully:"
        firefox --version
    else
        echo "Firefox installation failed!"
        exit 1
    fi
    
    # Clean up
    yum clean all
}

# Main installation logic
case "$BROWSER_TYPE" in
    chrome)
        install_chrome "$BROWSER_VERSION"
        ;;
    firefox)
        install_firefox "$BROWSER_VERSION"
        ;;
    none)
        echo "Skipping browser installation (none specified)"
        ;;
    *)
        echo "Error: Unsupported browser type '$BROWSER_TYPE'"
        echo "Supported browsers: chrome, firefox, none"
        exit 1
        ;;
esac

echo "Browser installation complete!"

