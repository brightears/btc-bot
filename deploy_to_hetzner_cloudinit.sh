#!/bin/bash
set -e

API_TOKEN="USqbtSwLR4RJJBEPl0tBRMgRoT7fEdQV34hoxLRN7IguWuzhMedjaegleIO37btI"
SERVER_ID="108738914"
SERVER_IP="5.223.55.219"
SSH_KEY_ID="103010626"

echo "=== Hetzner Cloud VPS Deployment with Cloud-Init ==="
echo ""
echo "Server: $SERVER_IP (ID: $SERVER_ID)"
echo "SSH Key ID: $SSH_KEY_ID"
echo ""

# Verify cloud-init file exists
if [ ! -f "cloud-init.yaml" ]; then
    echo "✗ cloud-init.yaml not found in current directory"
    exit 1
fi

echo "✓ Cloud-init configuration found"

# Rebuild server with cloud-init
echo ""
echo "⚠️  WARNING: This will DESTROY all data on the server!"
echo "The server will be rebuilt with Ubuntu 22.04 and cloud-init will:"
echo "  - Fix DNS resolution"
echo "  - Install system packages"
echo "  - Compile and install TA-Lib (takes ~5 minutes)"
echo "  - Clone btc-bot repository"
echo "  - Install Freqtrade and dependencies"
echo "  - Create .env file with your credentials"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Read and encode cloud-init
echo ""
echo "Preparing cloud-init data..."
CLOUD_INIT_B64=$(cat cloud-init.yaml | base64)

# Rebuild server
echo "Rebuilding server..."
REBUILD_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"image\": \"ubuntu-22.04\"
  }" \
  https://api.hetzner.cloud/v1/servers/$SERVER_ID/actions/rebuild)

ACTION_ID=$(echo $REBUILD_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$ACTION_ID" ]; then
    echo "✗ Rebuild failed. Response:"
    echo $REBUILD_RESPONSE | python3 -m json.tool 2>/dev/null || echo $REBUILD_RESPONSE
    exit 1
fi

echo "✓ Rebuild initiated (Action ID: $ACTION_ID)"

# Wait for server to be running
echo ""
echo "Waiting for server to rebuild..."
for i in {1..60}; do
    STATUS=$(curl -s -H "Authorization: Bearer $API_TOKEN" \
      https://api.hetzner.cloud/v1/servers/$SERVER_ID | \
      grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ "$STATUS" = "running" ]; then
        echo "✓ Server is running"
        break
    fi

    echo -n "."
    sleep 5
done
echo ""

# Wait a moment for SSH to be available
echo "Waiting for SSH service to start..."
sleep 30

# Now manually run cloud-init via SSH (since rebuild doesn't support user_data parameter)
echo ""
echo "Uploading and executing cloud-init configuration..."

# Upload cloud-init file
scp -i ~/.ssh/hetzner_btc_bot -o StrictHostKeyChecking=no -o ConnectTimeout=10 cloud-init.yaml root@$SERVER_IP:/tmp/cloud-init.yaml

if [ $? -ne 0 ]; then
    echo "✗ Failed to upload cloud-init file"
    echo "You can manually connect with: ssh -i ~/.ssh/hetzner_btc_bot root@$SERVER_IP"
    exit 1
fi

echo "✓ Cloud-init file uploaded"

# Execute cloud-init commands
echo "Executing cloud-init setup (this will take 10-15 minutes)..."
echo "Progress will be shown below:"
echo ""

ssh -i ~/.ssh/hetzner_btc_bot -o StrictHostKeyChecking=no root@$SERVER_IP << 'ENDSSH'
set -e

echo "Starting setup..."

# Fix DNS
cat > /etc/systemd/resolved.conf << 'EOF'
[Resolve]
DNS=8.8.8.8 8.8.4.4
FallbackDNS=1.1.1.1 1.0.0.1
DNSStubListener=yes
EOF

systemctl restart systemd-resolved
sleep 5

echo "✓ DNS configured"

# Enable password auth
mkdir -p /etc/ssh/sshd_config.d
cat > /etc/ssh/sshd_config.d/99-enable-password-auth.conf << 'EOF'
PasswordAuthentication yes
PermitRootLogin yes
EOF

systemctl restart sshd
echo "✓ SSH password auth enabled"

# Update packages
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y
apt-get install -y git python3 python3-pip python3-venv build-essential wget curl htop screen

echo "✓ Packages installed"

# Install TA-Lib
echo "Installing TA-Lib (this takes ~5 minutes)..."
cd /tmp
wget --timeout=120 http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz || \
  wget --timeout=120 https://downloads.sourceforge.net/project/ta-lib/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
make install
ldconfig

echo "✓ TA-Lib installed"

# Clone repository
cd /root
git clone https://github.com/brightears/btc-bot.git
cd btc-bot

echo "✓ Repository cloned"

# Setup Python environment
python3 -m venv .venv
/root/btc-bot/.venv/bin/pip install --upgrade pip
/root/btc-bot/.venv/bin/pip install freqtrade python-dotenv ccxt pyyaml tenacity

echo "✓ Python dependencies installed"

# Create .env file
cat > /root/btc-bot/.env << 'ENVEOF'
LIVE_TRADING=NO
KILL=0
BINANCE_KEY=7oLIWbKlJmDnEx7Ja9FDW4vBhkkZtw8EjklmYV1MQCDnoyV8KGcoVfcGaAHksjIs
BINANCE_SECRET=WuoEGtzcfiMiE1xwChZdMIq3H6ujhqkCy2M6FZaYWXw1Qc58a1GFc4lf2J9HfVoj
BINANCE_USDM_API_KEY=YOUR_BINANCE_USDM_KEY
BINANCE_USDM_API_SECRET=YOUR_BINANCE_USDM_SECRET
TELEGRAM_TOKEN=8476508713:AAFhMSVEQ_rgG9qTL-LpVTtFSqDA0DPbzUI
TELEGRAM_CHAT_ID=8352324945
GEMINI_API_KEY=AIzaSyB7-SLqrE0hYdtszqDXmxvcC-4XioY_Zz0
VPS_HOST=5.223.55.219
VPS_USER=root
VPS_PASSWORD=d4FM9j4evXW7
HETZNER_API_TOKEN=USqbtSwLR4RJJBEPl0tBRMgRoT7fEdQV34hoxLRN7IguWuzhMedjaegleIO37btI
ENVEOF

echo "✓ .env file created"

# Update config
if [ -f "update_config_from_env.py" ]; then
    /root/btc-bot/.venv/bin/python update_config_from_env.py
    echo "✓ Config updated from .env"
fi

# Log completion
echo "Setup complete at $(date)" > /root/setup.log
echo "TA-Lib version:" >> /root/setup.log
ldconfig -p | grep talib >> /root/setup.log
echo "Freqtrade version:" >> /root/setup.log
/root/btc-bot/.venv/bin/freqtrade --version >> /root/setup.log 2>&1

echo ""
echo "=== Setup Complete ==="
cat /root/setup.log

ENDSSH

if [ $? -eq 0 ]; then
    echo ""
    echo "=== Deployment Successful! ==="
    echo ""
    echo "To connect to your server:"
    echo "  ssh -i ~/.ssh/hetzner_btc_bot root@$SERVER_IP"
    echo ""
    echo "To start Freqtrade:"
    echo "  cd /root/btc-bot"
    echo "  source .venv/bin/activate"
    echo "  freqtrade trade --config config.json"
    echo ""
    echo "To run strategy rotation:"
    echo "  python strategy_rotator.py"
    echo ""
else
    echo ""
    echo "✗ Deployment encountered errors"
    echo "Connect manually to investigate:"
    echo "  ssh -i ~/.ssh/hetzner_btc_bot root@$SERVER_IP"
fi
