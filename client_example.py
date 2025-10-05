#!/usr/bin/env python3
"""
TV Monitor API Client Example
Demonstrates how to interact with the TV Monitor API
"""

import requests
import json
from datetime import datetime
from typing import Dict, List

class TVMonitorClient:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """Check if the API is healthy"""
        response = self.session.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()
    
    def get_current_programs(self) -> List[Dict]:
        """Get currently airing programs"""
        response = self.session.get(f"{self.base_url}/api/programs/current")
        response.raise_for_status()
        return response.json()['programs']
    
    def get_all_programs(self) -> List[Dict]:
        """Get all programs"""
        response = self.session.get(f"{self.base_url}/api/programs/all")
        response.raise_for_status()
        return response.json()['programs']
    
    def subscribe_to_program(self, program_title: str, webhook_url: str) -> Dict:
        """Subscribe to notifications for a specific program"""
        data = {
            "program_title": program_title,
            "webhook_url": webhook_url
        }
        response = self.session.post(f"{self.base_url}/api/subscribe", json=data)
        response.raise_for_status()
        return response.json()
    
    def unsubscribe_from_program(self, program_title: str, webhook_url: str) -> Dict:
        """Unsubscribe from notifications for a specific program"""
        data = {
            "program_title": program_title,
            "webhook_url": webhook_url
        }
        response = self.session.post(f"{self.base_url}/api/unsubscribe", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_subscriptions(self) -> Dict:
        """Get all active subscriptions"""
        response = self.session.get(f"{self.base_url}/api/subscriptions")
        response.raise_for_status()
        return response.json()
    
    def start_monitoring(self) -> Dict:
        """Start the monitoring service"""
        response = self.session.post(f"{self.base_url}/api/monitoring/start")
        response.raise_for_status()
        return response.json()
    
    def stop_monitoring(self) -> Dict:
        """Stop the monitoring service"""
        response = self.session.post(f"{self.base_url}/api/monitoring/stop")
        response.raise_for_status()
        return response.json()
    
    def get_monitoring_status(self) -> Dict:
        """Get monitoring status"""
        response = self.session.get(f"{self.base_url}/api/monitoring/status")
        response.raise_for_status()
        return response.json()
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get notification logs"""
        response = self.session.get(f"{self.base_url}/api/logs?limit={limit}")
        response.raise_for_status()
        return response.json()['logs']

def main():
    """Example usage of the TV Monitor API client"""
    
    # Initialize client (replace with your EC2 instance URL)
    client = TVMonitorClient("http://your-ec2-instance:5001")
    
    try:
        # Health check
        print("🏥 Health Check:")
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Monitoring: {health['monitoring_active']}")
        print()
        
        # Get current programs
        print("📺 Current Programs:")
        current_programs = client.get_current_programs()
        for program in current_programs[:5]:  # Show first 5
            print(f"   • {program['title']} ({program['channel']}) - {program['start']}")
        print(f"   Total: {len(current_programs)} programs currently airing")
        print()
        
        # Subscribe to a specific program
        print("🔔 Subscribing to notifications:")
        webhook_url = "https://your-webhook-endpoint.com/tv-notifications"
        program_to_watch = "Susedia"  # Example from the CSV
        
        subscription = client.subscribe_to_program(program_to_watch, webhook_url)
        print(f"   ✅ {subscription['message']}")
        print()
        
        # Get all subscriptions
        print("📋 Active Subscriptions:")
        subscriptions = client.get_subscriptions()
        for program, webhooks in subscriptions['subscriptions'].items():
            print(f"   • {program}: {len(webhooks)} webhook(s)")
        print()
        
        # Get monitoring status
        print("⚡ Monitoring Status:")
        status = client.get_monitoring_status()
        print(f"   Active: {status['monitoring_active']}")
        print(f"   Subscriptions: {status['active_subscriptions']}")
        print()
        
        # Get recent logs
        print("📝 Recent Notification Logs:")
        logs = client.get_logs(limit=5)
        for log in logs:
            print(f"   • {log['sent_at']}: {log['program_title']} -> {log['status']}")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def webhook_server_example():
    """Example webhook server to receive notifications"""
    from flask import Flask, request
    
    app = Flask(__name__)
    
    @app.route('/tv-notifications', methods=['POST'])
    def receive_notification():
        data = request.get_json()
        
        print("🎬 TV Program Started!")
        print(f"   Program: {data['program']['title']}")
        print(f"   Channel: {data['program']['channel']}")
        print(f"   Start Time: {data['program']['start']}")
        print(f"   Rating: {data['program']['rating']}")
        print(f"   Timestamp: {data['timestamp']}")
        print()
        
        # Here you can add your custom logic:
        # - Send email notifications
        # - Update database
        # - Send push notifications
        # - Trigger other services
        
        return {"status": "received"}, 200
    
    print("🌐 Starting webhook server on http://localhost:8000")
    print("   Use this URL as webhook_url: http://your-domain:8000/tv-notifications")
    app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "webhook":
        webhook_server_example()
    else:
        main()