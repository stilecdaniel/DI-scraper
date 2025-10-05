#!/usr/bin/env python3
"""
TV Program Monitor API Server
Monitors TV schedule and sends notifications when programs start
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import pandas as pd
import threading
import time
import os
import schedule
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tv_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class TVMonitor:
    def __init__(self, csv_file: str = "shows.csv", db_file: str = "tv_monitor.db"):
        self.csv_file = csv_file
        self.db_file = db_file
        self.subscribers = {}  # Format: {program_title: [webhook_urls]}
        self.monitoring_active = False
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database for storing subscribers and logs"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Create subscribers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_title TEXT NOT NULL,
                webhook_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Create notification logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notification_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_title TEXT NOT NULL,
                channel TEXT NOT NULL,
                start_time TEXT NOT NULL,
                webhook_url TEXT NOT NULL,
                status TEXT NOT NULL,
                response_code INTEGER,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Load existing subscribers from database
        self.load_subscribers()
    
    def load_subscribers(self):
        """Load active subscribers from database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT program_title, webhook_url FROM subscribers WHERE active = 1")
        
        for program_title, webhook_url in cursor.fetchall():
            if program_title not in self.subscribers:
                self.subscribers[program_title] = []
            if webhook_url not in self.subscribers[program_title]:
                self.subscribers[program_title].append(webhook_url)
        
        conn.close()
        logger.info(f"Loaded {len(self.subscribers)} program subscriptions")
    
    def subscribe_to_program(self, program_title: str, webhook_url: str) -> bool:
        """Subscribe to notifications for a specific program"""
        try:
            # Add to database
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO subscribers (program_title, webhook_url) VALUES (?, ?)",
                (program_title, webhook_url)
            )
            conn.commit()
            conn.close()
            
            # Add to memory
            if program_title not in self.subscribers:
                self.subscribers[program_title] = []
            if webhook_url not in self.subscribers[program_title]:
                self.subscribers[program_title].append(webhook_url)
            
            logger.info(f"Subscribed {webhook_url} to program: {program_title}")
            return True
        except Exception as e:
            logger.error(f"Error subscribing to program: {e}")
            return False
    
    def unsubscribe_from_program(self, program_title: str, webhook_url: str) -> bool:
        """Unsubscribe from notifications for a specific program"""
        try:
            # Remove from database
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE subscribers SET active = 0 WHERE program_title = ? AND webhook_url = ?",
                (program_title, webhook_url)
            )
            conn.commit()
            conn.close()
            
            # Remove from memory
            if program_title in self.subscribers and webhook_url in self.subscribers[program_title]:
                self.subscribers[program_title].remove(webhook_url)
                if not self.subscribers[program_title]:
                    del self.subscribers[program_title]
            
            logger.info(f"Unsubscribed {webhook_url} from program: {program_title}")
            return True
        except Exception as e:
            logger.error(f"Error unsubscribing from program: {e}")
            return False
    
    def get_current_programs(self) -> List[Dict]:
        """Get programs that are currently airing"""
        if not os.path.exists(self.csv_file):
            logger.warning(f"CSV file {self.csv_file} not found")
            return []
        
        try:
            df = pd.read_csv(self.csv_file)
            current_time = datetime.now()
            current_programs = []
            
            for _, row in df.iterrows():
                # Parse the start time
                start_time_str = f"{row['date']} {row['start']}"
                try:
                    start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
                    
                    # Check if program is currently airing (within the current hour)
                    if (start_time <= current_time <= start_time + timedelta(hours=1)):
                        current_programs.append({
                            'title': row['title'],
                            'channel': row['channel'],
                            'start': row['start'],
                            'rating': row['rating'],
                            'year': row['year'] if pd.notna(row['year']) else None
                        })
                except ValueError as e:
                    logger.warning(f"Error parsing time for row: {row}, error: {e}")
                    continue
            
            return current_programs
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return []
    
    def send_notification(self, program_data: Dict, webhook_url: str) -> bool:
        """Send notification to webhook URL"""
        try:
            payload = {
                "event": "program_started",
                "timestamp": datetime.now().isoformat(),
                "program": program_data
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            # Log the notification
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notification_logs 
                (program_title, channel, start_time, webhook_url, status, response_code)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                program_data['title'],
                program_data['channel'],
                program_data['start'],
                webhook_url,
                'success' if response.status_code == 200 else 'failed',
                response.status_code
            ))
            conn.commit()
            conn.close()
            
            if response.status_code == 200:
                logger.info(f"Notification sent successfully to {webhook_url} for program: {program_data['title']}")
                return True
            else:
                logger.warning(f"Webhook returned status {response.status_code} for {webhook_url}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification to {webhook_url}: {e}")
            
            # Log the failed notification
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notification_logs 
                (program_title, channel, start_time, webhook_url, status, response_code)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                program_data['title'],
                program_data['channel'],
                program_data['start'],
                webhook_url,
                'error',
                0
            ))
            conn.commit()
            conn.close()
            
            return False
    
    def check_programs(self):
        """Check for programs starting now and send notifications"""
        logger.info("Checking for starting programs...")
        current_programs = self.get_current_programs()
        
        for program in current_programs:
            program_title = program['title']
            
            # Check if anyone is subscribed to this program
            if program_title in self.subscribers:
                for webhook_url in self.subscribers[program_title]:
                    self.send_notification(program, webhook_url)
    
    def start_monitoring(self):
        """Start the monitoring service"""
        if self.monitoring_active:
            logger.info("Monitoring is already active")
            return
        
        self.monitoring_active = True
        logger.info("Starting TV program monitoring...")
        
        # Schedule checks every minute
        schedule.every(1).minutes.do(self.check_programs)
        
        def run_scheduler():
            while self.monitoring_active:
                schedule.run_pending()
                time.sleep(1)
        
        # Start scheduler in a separate thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("TV program monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring service"""
        self.monitoring_active = False
        schedule.clear()
        logger.info("TV program monitoring stopped")

# Initialize TV Monitor
tv_monitor = TVMonitor()

# API Endpoints
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'monitoring_active': tv_monitor.monitoring_active,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/programs/current', methods=['GET'])
def get_current_programs():
    """Get currently airing programs"""
    programs = tv_monitor.get_current_programs()
    return jsonify({
        'programs': programs,
        'count': len(programs),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/programs/all', methods=['GET'])
def get_all_programs():
    """Get all programs from CSV"""
    try:
        if not os.path.exists(tv_monitor.csv_file):
            return jsonify({'error': 'CSV file not found'}), 404
        
        df = pd.read_csv(tv_monitor.csv_file)
        programs = df.to_dict('records')
        
        return jsonify({
            'programs': programs,
            'count': len(programs),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/subscribe', methods=['POST'])
def subscribe():
    """Subscribe to program notifications"""
    data = request.get_json()
    
    if not data or 'program_title' not in data or 'webhook_url' not in data:
        return jsonify({'error': 'program_title and webhook_url are required'}), 400
    
    success = tv_monitor.subscribe_to_program(data['program_title'], data['webhook_url'])
    
    if success:
        return jsonify({
            'message': f"Successfully subscribed to '{data['program_title']}'",
            'program_title': data['program_title'],
            'webhook_url': data['webhook_url']
        })
    else:
        return jsonify({'error': 'Failed to subscribe'}), 500

@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe():
    """Unsubscribe from program notifications"""
    data = request.get_json()
    
    if not data or 'program_title' not in data or 'webhook_url' not in data:
        return jsonify({'error': 'program_title and webhook_url are required'}), 400
    
    success = tv_monitor.unsubscribe_from_program(data['program_title'], data['webhook_url'])
    
    if success:
        return jsonify({
            'message': f"Successfully unsubscribed from '{data['program_title']}'",
            'program_title': data['program_title'],
            'webhook_url': data['webhook_url']
        })
    else:
        return jsonify({'error': 'Failed to unsubscribe'}), 500

@app.route('/api/subscriptions', methods=['GET'])
def get_subscriptions():
    """Get all active subscriptions"""
    return jsonify({
        'subscriptions': tv_monitor.subscribers,
        'count': sum(len(urls) for urls in tv_monitor.subscribers.values()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/monitoring/start', methods=['POST'])
def start_monitoring():
    """Start the monitoring service"""
    tv_monitor.start_monitoring()
    return jsonify({
        'message': 'Monitoring started',
        'status': 'active'
    })

@app.route('/api/monitoring/stop', methods=['POST'])
def stop_monitoring():
    """Stop the monitoring service"""
    tv_monitor.stop_monitoring()
    return jsonify({
        'message': 'Monitoring stopped',
        'status': 'inactive'
    })

@app.route('/api/monitoring/status', methods=['GET'])
def monitoring_status():
    """Get monitoring status"""
    return jsonify({
        'monitoring_active': tv_monitor.monitoring_active,
        'active_subscriptions': len(tv_monitor.subscribers),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get notification logs"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        conn = sqlite3.connect(tv_monitor.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM notification_logs 
            ORDER BY sent_at DESC 
            LIMIT ?
        ''', (limit,))
        
        columns = [description[0] for description in cursor.description]
        logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'logs': logs,
            'count': len(logs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Start monitoring automatically
    tv_monitor.start_monitoring()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=False)