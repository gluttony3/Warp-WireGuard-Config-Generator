# Warp WireGuard Config Generator

A script to generate WireGuard configuration files for Cloudflare Warp VPN.

## Requirements

- Python 3.7+
- WireGuard tools (`wg`, `wg-quick`)
- Internet connection

### Installing WireGuard

```bash
# Debian/Ubuntu
sudo apt install wireguard

# Void Linux
sudo xbps-install -S wireguard-tools

# Windows
# Download from https://www.wireguard.com/install/
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

```bash
python generatewrp.py
```

The script will ask you to enter a name for the configuration (e.g., `phone` or `pc`).

The file will be saved as `warp_<name>.conf`.

## Running the VPN

### Linux

```bash
sudo wg-quick up ./warp_phone.conf    # Start
sudo wg-quick down ./warp_phone.conf  # Stop
```

### Windows

1. Open WireGuard
2. Click "Add Tunnel" -> "Add empty tunnel..."
3. Paste the contents of the `.conf` file
4. Click "Activate"

### macOS

```bash
brew install --cask wireguard
```

Import the config and click "Activate".

## Troubleshooting

- If the Cloudflare API is not responding — check your internet connection
- If `wg` is not found — install WireGuard tools
- Endpoint is auto-fixed if the API returns the format `x.x.x.x:0:2408`
