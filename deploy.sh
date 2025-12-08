#!/bin/bash
# Deployment script for lunar-calendar to Netcup

set -e

REMOTE_HOST="netcup"
REMOTE_DIR="/opt/websites/lunar-calendar"
TUNNEL_ID="a838e9dc-0af5-4212-8af2-6864eb15e1b5"

echo "=== Deploying lunar-calendar to Netcup ==="

# 1. Create directory and copy files
echo "[1/4] Copying files to Netcup..."
ssh $REMOTE_HOST "mkdir -p $REMOTE_DIR"
scp -r index.html ifc.py Dockerfile docker-compose.yml $REMOTE_HOST:$REMOTE_DIR/

# 2. Build and start container
echo "[2/4] Building and starting Docker container..."
ssh $REMOTE_HOST "cd $REMOTE_DIR && docker compose up -d --build"

# 3. Add hostname to Cloudflare tunnel config
echo "[3/4] Updating Cloudflare tunnel config..."
ssh $REMOTE_HOST "cat /root/cloudflared/config.yml" | grep -q "lunarcal.jeffemmett.com" || {
    ssh $REMOTE_HOST "cat >> /root/cloudflared/config.yml << 'EOF'
  - hostname: lunarcal.jeffemmett.com
    service: http://localhost:80
EOF"
    ssh $REMOTE_HOST "docker restart cloudflared"
}

echo "[4/4] Done!"
echo ""
echo "=== Next Steps ==="
echo "Add DNS CNAME in Cloudflare Dashboard:"
echo "  Type:   CNAME"
echo "  Name:   lunarcal"
echo "  Target: $TUNNEL_ID.cfargotunnel.com"
echo "  Proxy:  Proxied (orange cloud)"
echo ""
echo "Site will be live at: https://lunarcal.jeffemmett.com"
