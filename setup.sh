#!/bin/bash

# Function to generate hashed control password
generate_hashed_password() {
    read -sp "Enter your control password: " control_password
    echo
    hashed_password=$(tor --hash-password "$control_password" | tail -n 1)
    echo "Generated hashed password: $hashed_password"
    echo $hashed_password
}

# Check if Tor is installed
if ! command -v tor &> /dev/null
then
    echo "Tor is not installed. Installing Tor..."
    # Update package list and install Tor
    sudo apt-get update
    sudo apt-get install -y tor
else
    echo "Tor is already installed."
fi

# Start the Tor service
echo "Starting Tor service..."
sudo service tor start

# Check the status of the Tor service
echo "Checking Tor service status..."
sudo service tor status

# Configure the torrc file
TORRC_PATH="/etc/tor/torrc"
CONTROL_PORT_LINE="ControlPort 9051"
COOKIE_AUTH_LINE="CookieAuthentication 1"

# Add ControlPort configuration if not already present
if ! grep -q "$CONTROL_PORT_LINE" "$TORRC_PATH"; then
    echo "Adding ControlPort configuration to torrc..."
    echo "$CONTROL_PORT_LINE" | sudo tee -a "$TORRC_PATH" > /dev/null
fi

# Add CookieAuthentication configuration if not already present
if ! grep -q "$COOKIE_AUTH_LINE" "$TORRC_PATH"; then
    echo "Adding CookieAuthentication configuration to torrc..."
    echo "$COOKIE_AUTH_LINE" | sudo tee -a "$TORRC_PATH" > /dev/null
fi

# Restart the Tor service to apply new configurations
echo "Restarting Tor service to apply new configurations..."
sudo service tor restart

# Check the status of the Tor service again
echo "Checking Tor service status..."
sudo service tor status
echo "Tor setup completed."
