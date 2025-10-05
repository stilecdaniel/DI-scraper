#!/usr/bin/env python3
"""
Príklad klienta iného tímu - Team DataScience_02
Ukážka ako používať TV Monitor API na zbieranie a analýzu dát
"""

import requests
import json
import time
from datetime import datetime
import pandas as pd

class TeamDataScienceClient:
    def __init__(self, api_url="http://54.172.130.65:5001", team_name="Team_DataScience_02"):
        self.api_url = api_url
        self.team_name = team_name
        self.collected_data = []
        
    def test_api_connection(self):
        """Test pripojenia na API"""
        print(f"🔗 Testing connection to TV Monitor API...")
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is healthy!")
                print(f"   Status: {data['status']}")
                print(f"   Monitoring: {data['monitoring_active']}")
                print(f"   Timestamp: {data['timestamp']}")
                return True
            else:
                print(f"❌ API returned status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def collect_all_programs(self):
        """Zbieranie všetkých TV programov"""
        print(f"\n📺 Collecting all TV programs for {self.team_name}...")
        try:
            response = requests.get(f"{self.api_url}/api/programs/all", timeout=15)
            if response.status_code == 200:
                data = response.json()
                programs = data['programs']
                
                print(f"✅ Collected {data['count']} programs from {len(set(p['channel'] for p in programs))} channels")
                
                # Uloženie dát
                self.collected_data = programs
                
                # Zobrazenie vzorky dát
                print(f"\n📋 Sample programs:")
                for i, program in enumerate(programs[:5]):
                    print(f"   {i+1}. {program['title']} ({program['channel']}) - {program['start']} | Rating: {program['rating']}")
                
                return programs
            else:
                print(f"❌ Failed to collect programs: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error collecting programs: {e}")
            return []
    
    def get_current_programs(self):
        """Získanie aktuálne bežiacich programov"""
        print(f"\n🎬 Getting currently airing programs...")
        try:
            response = requests.get(f"{self.api_url}/api/programs/current", timeout=10)
            if response.status_code == 200:
                data = response.json()
                current_programs = data['programs']
                
                print(f"✅ Found {data['count']} currently airing programs:")
                for program in current_programs:
                    print(f"   📺 {program['title']} on {program['channel']} (started at {program['start']}) - Rating: {program['rating']}")
                
                return current_programs
            else:
                print(f"❌ Failed to get current programs: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting current programs: {e}")
            return []
    
    def subscribe_to_interesting_programs(self):
        """Prihlásenie na zaujímavé programy"""
        print(f"\n🔔 Subscribing to interesting programs for {self.team_name}...")
        
        # Programy, ktoré tím chce sledovať
        interesting_programs = ["Susedia", "Polda", "Priatelia", "Teória veľkého tresku"]
        webhook_url = f"https://team-datascience-02.herokuapp.com/notifications"
        
        subscribed = []
        failed = []
        
        for program in interesting_programs:
            try:
                response = requests.post(f"{self.api_url}/api/subscribe", 
                                       json={
                                           "program_title": program,
                                           "webhook_url": webhook_url
                                       }, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Subscribed to: {program}")
                    subscribed.append(program)
                else:
                    print(f"   ❌ Failed to subscribe to: {program}")
                    failed.append(program)
                    
            except Exception as e:
                print(f"   ❌ Error subscribing to {program}: {e}")
                failed.append(program)
        
        print(f"\n📊 Subscription Summary:")
        print(f"   Successful: {len(subscribed)} programs")
        print(f"   Failed: {len(failed)} programs")
        
        return {"subscribed": subscribed, "failed": failed}
    
    def analyze_collected_data(self):
        """Analýza zozbieraných dát"""
        if not self.collected_data:
            print("❌ No data to analyze. Run collect_all_programs() first.")
            return
        
        print(f"\n📊 Analyzing collected data for {self.team_name}...")
        
        # Konverzia na DataFrame
        df = pd.DataFrame(self.collected_data)
        
        # Základné štatistiky
        print(f"\n📈 Basic Statistics:")
        print(f"   Total programs: {len(df)}")
        print(f"   Unique channels: {df['channel'].nunique()}")
        print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
        
        # Analýza kanálov
        print(f"\n📺 Channel Analysis:")
        channel_counts = df['channel'].value_counts()
        for channel, count in channel_counts.items():
            print(f"   {channel}: {count} programs")
        
        # Analýza ratingu
        df['rating_numeric'] = df['rating'].str.replace('%', '').astype(float)
        
        print(f"\n⭐ Rating Analysis:")
        print(f"   Average rating: {df['rating_numeric'].mean():.1f}%")
        print(f"   Highest rating: {df['rating_numeric'].max():.1f}%")
        print(f"   Lowest rating: {df['rating_numeric'].min():.1f}%")
        
        # Top programy podľa ratingu
        print(f"\n🏆 Top 5 Programs by Rating:")
        top_programs = df.nlargest(5, 'rating_numeric')
        for idx, program in top_programs.iterrows():
            print(f"   {program['title']} ({program['channel']}) - {program['rating']}")
        
        # Analýza času
        print(f"\n⏰ Time Slot Analysis:")
        df['hour'] = pd.to_datetime(df['start'], format='%H:%M').dt.hour
        popular_hours = df['hour'].value_counts().head(5)
        for hour, count in popular_hours.items():
            print(f"   {hour:02d}:00 - {count} programs")
        
        return df
    
    def export_data_for_team(self):
        """Export dát pre tím"""
        if not self.collected_data:
            print("❌ No data to export. Run collect_all_programs() first.")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.team_name}_tv_data_{timestamp}.json"
        
        export_data = {
            "team_info": {
                "team_name": self.team_name,
                "exported_at": datetime.now().isoformat(),
                "api_source": self.api_url,
                "total_programs": len(self.collected_data)
            },
            "programs": self.collected_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Data exported to: {filename}")
        return filename
    
    def monitoring_dashboard(self):
        """Jednoduchý monitoring dashboard"""
        print(f"\n🖥️  {self.team_name} Monitoring Dashboard")
        print("="*60)
        
        try:
            # API Health
            health = requests.get(f"{self.api_url}/api/health", timeout=5).json()
            print(f"🔗 API Status: {health['status'].upper()}")
            print(f"📡 Monitoring Active: {health['monitoring_active']}")
            
            # Current programs
            current = requests.get(f"{self.api_url}/api/programs/current", timeout=5).json()
            print(f"🎬 Currently Airing: {current['count']} programs")
            
            # Subscriptions
            subs = requests.get(f"{self.api_url}/api/subscriptions", timeout=5).json()
            print(f"🔔 Active Subscriptions: {subs['count']}")
            
            # Show subscriptions
            if subs['subscriptions']:
                print(f"\n📋 Subscribed Programs:")
                for program, webhooks in subs['subscriptions'].items():
                    print(f"   • {program} ({len(webhooks)} webhook(s))")
            
            print(f"\n⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"❌ Dashboard Error: {e}")
        
        print("="*60)

def demo_workflow():
    """Ukážka celého workflow pre iný tím"""
    print("🚀 TEAM DATASCIENCE_02 - TV DATA COLLECTION DEMO")
    print("="*70)
    
    # Inicializácia klienta
    client = TeamDataScienceClient()
    
    # 1. Test pripojenia
    if not client.test_api_connection():
        print("❌ Cannot connect to API. Please check if the server is running.")
        return
    
    # 2. Zobrazenie dashboard-u
    client.monitoring_dashboard()
    
    # 3. Zbieranie všetkých programov
    programs = client.collect_all_programs()
    
    if programs:
        # 4. Analýza dát
        df = client.analyze_collected_data()
        
        # 5. Export dát
        exported_file = client.export_data_for_team()
    
    # 6. Získanie aktuálnych programov
    current_programs = client.get_current_programs()
    
    # 7. Prihlásenie na programy
    subscription_result = client.subscribe_to_interesting_programs()
    
    # 8. Finálny dashboard
    print(f"\n🎯 FINAL RESULTS FOR {client.team_name}:")
    print("="*50)
    print(f"✅ API Connection: Working")
    print(f"✅ Programs Collected: {len(programs) if programs else 0}")
    print(f"✅ Current Programs: {len(current_programs)}")
    print(f"✅ Subscriptions: {len(subscription_result['subscribed'])} successful")
    if 'exported_file' in locals():
        print(f"✅ Data Exported: {exported_file}")
    
    print(f"\n🎬 {client.team_name} is now ready to monitor TV programs!")
    print("="*70)

if __name__ == "__main__":
    demo_workflow()