# TV Monitor API
**Data Engineering Project - TV Program Monitoring System**

Komplexný systém na monitorovanie TV programov zo slovenskej televízie, poskytujúci REST API pre ostatné tímy na získavanie a analýzu TV dát.

## 🚀 Živý Server
**API Endpoint:** `http://54.172.130.65:5001`

Server beží 24/7 na Amazon EC2 a poskytuje aktuálne TV dáta pre všetky tímy.

## 📋 Obsah
- [Quick Start pre Tímy](#quick-start-pre-tímy)
- [API Endpoints](#api-endpoints)
- [Príklady Použitia](#príklady-použitia)
- [Inštalácia Lokálne](#inštalácia-lokálne)
- [Deployment na EC2](#deployment-na-ec2)
- [Monitorovanie](#monitorovanie)

## 🎯 Quick Start pre Tímy

### 1. Testovanie API Pripojenia
```python
import requests

# Test pripojenia na API
response = requests.get('http://54.172.130.65:5001/health')
print(response.json())
# Výstup: {"status": "healthy", "timestamp": "2025-10-05T20:20:06"}
```

### 2. Získanie TV Programov
```python
# Všetky programy
programs = requests.get('http://54.172.130.65:5001/programs').json()
print(f"Dostupných programov: {len(programs['programs'])}")

# Programy z konkrétneho kanála
joj_programs = requests.get('http://54.172.130.65:5001/programs?channel=JOJ').json()
```

### 3. Registrácia Webhookov
```python
# Registrácia pre notifikácie o nových programoch
webhook_data = {
    "url": "https://vasa-aplikacia.com/webhook",
    "events": ["new_program", "program_updated"]
}
response = requests.post('http://54.172.130.65:5001/subscribe', json=webhook_data)
```

## 🔌 API Endpoints

### Health Check
```http
GET /health
```
Overenie stavu API servera.

**Odpoveď:**
```json
{
    "status": "healthy",
    "timestamp": "2025-10-05T20:20:06",
    "uptime": "2 hours, 15 minutes"
}
```

### Získanie TV Programov
```http
GET /programs
GET /programs?channel=MARKIZA
GET /programs?date=2025-10-05
GET /programs?limit=50
```

**Parametre:**
- `channel` (voliteľné): Filtrovanie podľa kanála (MARKIZA, JOJ, STV1)
- `date` (voliteľné): Filtrovanie podľa dátumu (YYYY-MM-DD)
- `limit` (voliteľné): Počet výsledkov (predvolené: 100)

**Odpoveď:**
```json
{
    "programs": [
        {
            "id": "unique_id_123",
            "title": "Televízne noviny",
            "channel": "MARKIZA",
            "time": "19:00",
            "date": "2025-10-05",
            "description": "Denné spravodajstvo",
            "scraped_at": "2025-10-05T18:30:00"
        }
    ],
    "count": 79,
    "channels": ["MARKIZA", "JOJ", "STV1"]
}
```

### Registrácia Webhookov
```http
POST /subscribe
```

**Request Body:**
```json
{
    "url": "https://vasa-aplikacia.com/webhook",
    "events": ["new_program", "program_updated"],
    "team_name": "DataScience_Team_02"
}
```

### Štatistiky
```http
GET /stats
```

**Odpoveď:**
```json
{
    "total_programs": 1247,
    "channels": 3,
    "last_update": "2025-10-05T20:15:00",
    "programs_today": 79,
    "subscriptions": 5
}
```

## 💡 Príklady Použitia

### Pre Data Science Tímy
```python
import requests
import pandas as pd
from datetime import datetime, timedelta

class TVDataAnalyzer:
    def __init__(self):
        self.api_base = "http://54.172.130.65:5001"
    
    def get_weekly_programs(self):
        """Získa programy za posledný týždeň"""
        programs = requests.get(f"{self.api_base}/programs").json()
        df = pd.DataFrame(programs['programs'])
        
        # Konverzia na datetime
        df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])
        
        # Filter posledných 7 dní
        week_ago = datetime.now() - timedelta(days=7)
        return df[df['datetime'] >= week_ago]
    
    def analyze_prime_time(self):
        """Analýza prime time (19:00-22:00) programov"""
        df = self.get_weekly_programs()
        df['hour'] = pd.to_datetime(df['time'], format='%H:%M').dt.hour
        prime_time = df[(df['hour'] >= 19) & (df['hour'] <= 22)]
        
        return prime_time.groupby('channel')['title'].count().to_dict()

# Použitie
analyzer = TVDataAnalyzer()
prime_time_stats = analyzer.analyze_prime_time()
print("Prime time programy po kanáloch:", prime_time_stats)
```

### Pre Machine Learning Tímy
```python
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class TVContentClustering:
    def __init__(self):
        self.api_base = "http://54.172.130.65:5001"
    
    def cluster_programs_by_content(self, n_clusters=5):
        """Zoskupenie programov podľa obsahu pomocou ML"""
        programs = requests.get(f"{self.api_base}/programs").json()
        
        # Príprava textových dát
        texts = [p['title'] + ' ' + p.get('description', '') 
                for p in programs['programs']]
        
        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        X = vectorizer.fit_transform(texts)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X)
        
        # Pridanie cluster labels k programom
        for i, program in enumerate(programs['programs']):
            program['cluster'] = int(clusters[i])
        
        return programs['programs']

# Použitie
ml_analyzer = TVContentClustering()
clustered_programs = ml_analyzer.cluster_programs_by_content()
```

### Pre Web Development Tímy
```javascript
// JavaScript klient pre webové aplikácie
class TVMonitorAPI {
    constructor() {
        this.baseURL = 'http://54.172.130.65:5001';
    }
    
    async getPrograms(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${this.baseURL}/programs?${params}`);
        return response.json();
    }
    
    async subscribeToUpdates(webhookURL, teamName) {
        const response = await fetch(`${this.baseURL}/subscribe`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                url: webhookURL,
                events: ['new_program'],
                team_name: teamName
            })
        });
        return response.json();
    }
    
    async getStats() {
        const response = await fetch(`${this.baseURL}/stats`);
        return response.json();
    }
}

// Použitie v React/Vue komponente
const tvAPI = new TVMonitorAPI();
tvAPI.getPrograms({ channel: 'MARKIZA', limit: 20 })
    .then(data => console.log('Markíza programy:', data));
```

## 🔧 Inštalácia Lokálne

### Požiadavky
- Python 3.8+
- pip
- Git

### Kroky
1. **Klonovanie repozitára:**
```bash
git clone https://github.com/your-team/tv-monitor-api.git
cd tv-monitor-api
```

2. **Vytvorenie virtuálneho prostredia:**
```bash
python3 -m venv tv_monitor_env
source tv_monitor_env/bin/activate  # Linux/Mac
# alebo
tv_monitor_env\Scripts\activate  # Windows
```

3. **Inštalácia závislostí:**
```bash
pip install -r requirements.txt
```

4. **Spustenie API servera:**
```bash
python tv_monitor_api.py
```

API bude dostupné na `http://localhost:5001`

### Lokálne testovanie
```bash
# Test základnej funkčnosti
curl http://localhost:5001/health

# Test získania programov
curl http://localhost:5001/programs?limit=5
```

## ☁️ Deployment na EC2

### Automatizovaný Deployment
```bash
# Spustenie deployment skriptu
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

### Manuálny Deployment
1. **Pripojenie na EC2:**
```bash
ssh -i tv-monitor-key.pem ubuntu@54.172.130.65
```

2. **Setup na serveri:**
```bash
# Aktualizácia systému
sudo apt update && sudo apt upgrade -y

# Inštalácia Python a dependencies
sudo apt install -y python3 python3-pip python3-venv

# Upload súborov
scp -i tv-monitor-key.pem *.py *.txt ubuntu@54.172.130.65:~/

# Vytvorenie virtual environment
python3 -m venv tv_monitor_env
source tv_monitor_env/bin/activate
pip install -r requirements.txt

# Spustenie servera
python tv_monitor_api.py
```

### Systemd Service (Produkčné spustenie)
```bash
# Kopírovanie service súboru
sudo cp tv-monitor.service /etc/systemd/system/

# Aktivácia služby
sudo systemctl daemon-reload
sudo systemctl enable tv-monitor
sudo systemctl start tv-monitor

# Kontrola stavu
sudo systemctl status tv-monitor
```

## 📊 Monitorovanie

### Logy
```bash
# API logy
tail -f /var/log/tv-monitor.log

# Systemd logy
sudo journalctl -u tv-monitor -f
```

### Health Check
```bash
# Automatický health check script
#!/bin/bash
response=$(curl -s http://localhost:5001/health)
if [[ $? -eq 0 ]]; then
    echo "API is healthy: $response"
else
    echo "API is down, restarting service..."
    sudo systemctl restart tv-monitor
fi
```

### Výkon API
```python
import requests
import time

def monitor_api_performance():
    start_time = time.time()
    response = requests.get('http://54.172.130.65:5001/programs?limit=100')
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f}s")
    print(f"Status code: {response.status_code}")
    print(f"Data size: {len(response.text)} bytes")

monitor_api_performance()
```

## 🤝 Spolupráca Tímov

### Pre Tím Leaders
1. **Registrácia tímu:**
   - Zaregistrujte svoj webhook endpoint
   - Špecifikujte aké typy udalostí chcete dostávať
   - Nastavte `team_name` pre identifikáciu

2. **Limity a Fair Use:**
   - Maximálne 1000 requestov za hodinu na tím
   - Webhook notifikácie sú throttled (max 1 za minútu)
   - Pre veľké dáta použite pagination (`limit` parameter)

### Príklady Webhook Payloadov
```json
{
    "event": "new_program",
    "timestamp": "2025-10-05T20:30:00",
    "data": {
        "title": "Nový program",
        "channel": "MARKIZA",
        "time": "21:00",
        "date": "2025-10-05"
    },
    "team_name": "DataScience_Team_02"
}
```

## 📝 API Response Formáty

### Štandardná Chyba
```json
{
    "error": "Invalid channel name",
    "message": "Supported channels: MARKIZA, JOJ, STV1",
    "timestamp": "2025-10-05T20:30:00"
}
```

### Rate Limiting
```json
{
    "error": "Rate limit exceeded",
    "message": "Maximum 1000 requests per hour",
    "retry_after": 3600,
    "timestamp": "2025-10-05T20:30:00"
}
```

## 🆘 Troubleshooting

### Časté Problémy

**1. Connection Refused**
```bash
# Skontrolujte či server beží
curl http://54.172.130.65:5001/health

# Ak nie, reštartujte service
sudo systemctl restart tv-monitor
```

**2. Empty Response**
```python
# Možno nie sú dáta pre daný filter
response = requests.get('http://54.172.130.65:5001/programs?channel=INVALID')
# Skúste bez filtrov
response = requests.get('http://54.172.130.65:5001/programs')
```

**3. Webhook Nedostávate**
```python
# Skontrolujte registráciu
response = requests.get('http://54.172.130.65:5001/subscriptions')
print(response.json())
```

### Kontakt
- **Maintainer:** TV Monitor Team
- **GitHub Issues:** Pre bug reporty a feature requesty
- **API Status:** http://54.172.130.65:5001/health

## 📊 Dátová Štruktúra

### Program Object
```json
{
    "id": "unique_identifier",
    "title": "Názov programu",
    "channel": "MARKIZA|JOJ|STV1",
    "time": "HH:MM",
    "date": "YYYY-MM-DD",
    "description": "Popis programu (voliteľné)",
    "scraped_at": "ISO timestamp",
    "duration": "Dĺžka v minútach (voliteľné)",
    "genre": "Žáner (voliteľné)"
}
```

### Subscription Object
```json
{
    "id": "subscription_id",
    "url": "webhook_endpoint",
    "events": ["new_program", "program_updated"],
    "team_name": "Názov tímu",
    "created_at": "ISO timestamp",
    "active": true
}
```

---

**🎯 Ready to use? Start with the Quick Start section and integrate TV data into your project within minutes!**

**📈 Questions or need custom endpoints? Open an issue or contact the TV Monitor Team.**
