#!/usr/bin/env python3
"""
Local test script for TV Monitor API
Run this to test the API functionality locally before deploying to EC2
"""

import subprocess
import time
import sys
import signal
import requests
from threading import Thread

class LocalTestRunner:
    def __init__(self):
        self.api_process = None
        self.base_url = "http://localhost:5001"
    
    def start_api_server(self):
        """Start the API server in background"""
        print("🚀 Starting TV Monitor API server...")
        try:
            self.api_process = subprocess.Popen(
                [sys.executable, "tv_monitor_api.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            # Check if server is running
            try:
                response = requests.get(f"{self.base_url}/api/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API server started successfully")
                    return True
            except:
                pass
            
            print("❌ Failed to start API server")
            return False
            
        except Exception as e:
            print(f"❌ Error starting API server: {e}")
            return False
    
    def stop_api_server(self):
        """Stop the API server"""
        if self.api_process:
            print("🛑 Stopping API server...")
            self.api_process.terminate()
            self.api_process.wait()
            print("✅ API server stopped")
    
    def test_health_check(self):
        """Test health check endpoint"""
        print("\n🏥 Testing health check...")
        try:
            response = requests.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   ✅ Monitoring: {data['monitoring_active']}")
                return True
            else:
                print(f"   ❌ HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_programs_endpoints(self):
        """Test program-related endpoints"""
        print("\n📺 Testing programs endpoints...")
        
        # Test current programs
        try:
            response = requests.get(f"{self.base_url}/api/programs/current")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Current programs: {data['count']} found")
            else:
                print(f"   ❌ Current programs: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Current programs error: {e}")
        
        # Test all programs
        try:
            response = requests.get(f"{self.base_url}/api/programs/all")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ All programs: {data['count']} found")
                return data['programs'][:5] if data['programs'] else []
            else:
                print(f"   ❌ All programs: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"   ❌ All programs error: {e}")
            return []
    
    def test_subscription_flow(self, programs):
        """Test subscription and notification flow"""
        print("\n🔔 Testing subscription flow...")
        
        if not programs:
            print("   ⚠️  No programs available for testing")
            return
        
        test_program = programs[0]['title']
        webhook_url = "http://localhost:8888/test-webhook"
        
        # Test subscription
        try:
            response = requests.post(f"{self.base_url}/api/subscribe", json={
                "program_title": test_program,
                "webhook_url": webhook_url
            })
            if response.status_code == 200:
                print(f"   ✅ Subscribed to: {test_program}")
            else:
                print(f"   ❌ Subscription failed: HTTP {response.status_code}")
                return
        except Exception as e:
            print(f"   ❌ Subscription error: {e}")
            return
        
        # Test getting subscriptions
        try:
            response = requests.get(f"{self.base_url}/api/subscriptions")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Active subscriptions: {data['count']}")
            else:
                print(f"   ❌ Get subscriptions failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Get subscriptions error: {e}")
        
        # Test unsubscription
        try:
            response = requests.post(f"{self.base_url}/api/unsubscribe", json={
                "program_title": test_program,
                "webhook_url": webhook_url
            })
            if response.status_code == 200:
                print(f"   ✅ Unsubscribed from: {test_program}")
            else:
                print(f"   ❌ Unsubscription failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Unsubscription error: {e}")
    
    def test_monitoring_controls(self):
        """Test monitoring start/stop controls"""
        print("\n⚡ Testing monitoring controls...")
        
        # Test monitoring status
        try:
            response = requests.get(f"{self.base_url}/api/monitoring/status")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Monitoring status: {data['monitoring_active']}")
            else:
                print(f"   ❌ Status check failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
        
        # Test stop monitoring
        try:
            response = requests.post(f"{self.base_url}/api/monitoring/stop")
            if response.status_code == 200:
                print("   ✅ Monitoring stopped")
            else:
                print(f"   ❌ Stop failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Stop error: {e}")
        
        # Test start monitoring
        try:
            response = requests.post(f"{self.base_url}/api/monitoring/start")
            if response.status_code == 200:
                print("   ✅ Monitoring started")
            else:
                print(f"   ❌ Start failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Start error: {e}")
    
    def test_logs_endpoint(self):
        """Test logs endpoint"""
        print("\n📝 Testing logs endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/logs?limit=5")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Retrieved {data['count']} log entries")
            else:
                print(f"   ❌ Logs failed: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ Logs error: {e}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting TV Monitor API tests...\n")
        
        # Start API server
        if not self.start_api_server():
            return False
        
        try:
            # Run tests
            success = True
            
            if not self.test_health_check():
                success = False
            
            programs = self.test_programs_endpoints()
            
            self.test_subscription_flow(programs)
            self.test_monitoring_controls()
            self.test_logs_endpoint()
            
            print("\n" + "="*50)
            if success:
                print("🎉 All basic tests passed!")
                print("\n📋 Next steps:")
                print("1. Deploy to EC2 using deploy-ec2.sh")
                print("2. Update security groups to allow port 5001")
                print("3. Configure your domain/DNS")
                print("4. Set up SSL certificate")
                print("5. Create webhook endpoints for notifications")
            else:
                print("⚠️  Some tests failed. Check the logs above.")
            
            print("\n🔗 API Documentation:")
            print("   Health: GET /api/health")
            print("   Programs: GET /api/programs/current")
            print("   Subscribe: POST /api/subscribe")
            print("   Status: GET /api/monitoring/status")
            
        finally:
            self.stop_api_server()
        
        return success

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Test interrupted by user")
    sys.exit(0)

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check if required files exist
    required_files = ['tv_monitor_api.py', 'shows.csv']
    missing_files = [f for f in required_files if not subprocess.run(['test', '-f', f]).returncode == 0]
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all files are in the current directory.")
        return 1
    
    # Install dependencies if needed
    print("📦 Checking dependencies...")
    try:
        import flask, pandas, requests, schedule
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return 1
    
    # Run tests
    runner = LocalTestRunner()
    success = runner.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())