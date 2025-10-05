#!/bin/bash

# TV Monitor Deployment Script for Amazon EC2
# This script sets up the TV monitoring service on a fresh EC2 instance

set -e

echo "Starting TV Monitor deployment on EC2..."

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and pip if not present
echo "Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv git

# Create application directory
APP_DIR="/home/ubuntu/tv-monitor"
echo "Creating application directory at $APP_DIR..."
mkdir -p $APP_DIR
cd $APP_DIR

# Copy application files (assuming they're in current directory)
echo "Setting up application files..."
cp tv_monitor_api.py $APP_DIR/
cp scraper.py $APP_DIR/
cp requirements.txt $APP_DIR/
cp shows.csv $APP_DIR/ 2>/dev/null || echo "shows.csv not found, will be created by scraper"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create log directory
mkdir -p $APP_DIR/logs

# Set up systemd service
echo "Setting up systemd service..."
sudo cp tv-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tv-monitor
sudo systemctl start tv-monitor

# Set up cron job for scraper (runs every hour)
echo "Setting up cron job for TV program scraping..."
(crontab -l 2>/dev/null || true; echo "0 * * * * cd $APP_DIR && ./venv/bin/python scraper.py >> logs/scraper.log 2>&1") | crontab -

# Configure firewall to allow API access
echo "Configuring firewall..."
sudo ufw allow 5001/tcp

# Create a simple nginx configuration for reverse proxy (optional)
if command -v nginx &> /dev/null; then
    echo "Setting up nginx reverse proxy..."
    sudo tee /etc/nginx/sites-available/tv-monitor > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/tv-monitor /etc/nginx/sites-enabled/
    sudo systemctl restart nginx
    echo "Nginx configured. API accessible on port 80."
else
    echo "Nginx not installed. API accessible on port 5000."
fi

# Check service status
echo "Checking service status..."
sudo systemctl status tv-monitor --no-pager

echo ""
echo "======================================"
echo "TV Monitor deployment completed!"
echo "======================================"
echo ""
echo "Service status: $(sudo systemctl is-active tv-monitor)"
echo "API endpoint: http://$(curl -s ifconfig.me):5001 (or port 80 if nginx is configured)"
echo ""
echo "Available API endpoints:"
echo "  GET  /api/health                    - Health check"
echo "  GET  /api/programs/current          - Get currently airing programs"
echo "  GET  /api/programs/all              - Get all programs"
echo "  POST /api/subscribe                 - Subscribe to program notifications"
echo "  POST /api/unsubscribe               - Unsubscribe from notifications"
echo "  GET  /api/subscriptions             - Get all subscriptions"
echo "  POST /api/monitoring/start          - Start monitoring"
echo "  POST /api/monitoring/stop           - Stop monitoring"
echo "  GET  /api/monitoring/status         - Get monitoring status"
echo "  GET  /api/logs                      - Get notification logs"
echo ""
echo "Logs:"
echo "  Service logs: sudo journalctl -u tv-monitor -f"
echo "  Scraper logs: tail -f $APP_DIR/logs/scraper.log"
echo "  API logs: tail -f $APP_DIR/tv_monitor.log"
echo ""
echo "Management commands:"
echo "  sudo systemctl start tv-monitor     - Start service"
echo "  sudo systemctl stop tv-monitor      - Stop service"
echo "  sudo systemctl restart tv-monitor   - Restart service"
echo "  sudo systemctl status tv-monitor    - Check status"
echo ""