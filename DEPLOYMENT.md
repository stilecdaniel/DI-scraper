# TV Program Monitor API

Automatický monitoring TV programu s REST API pre Amazon EC2. Služba sleduje TV program zo súboru `shows.csv` a posiela notifikácie cez webhooky, keď sa začína konkrétny program.

## 🚀 Vlastnosti

- **REST API** pre správu subscriptions a monitoring
- **Webhook notifikácie** keď sa program začína
- **Automatický scraping** TV programu každú hodinu
- **SQLite databáza** pre uchovanie subscriptions a logov
- **Systemd service** pre automatické spustenie
- **Nginx reverse proxy** podpora

## 📋 Požiadavky

- Amazon EC2 instance (Ubuntu 20.04+ odporúčané)
- Python 3.8+
- Nginx (voliteľné, pre reverse proxy)

## 🛠️ Inštalácia na EC2

### 1. Príprava súborov

Nahrajte všetky súbory na váš EC2 server:
```bash
scp -i your-key.pem *.py *.txt *.sh *.service ubuntu@your-ec2-ip:~/
```

### 2. Spustenie deployment scriptu

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

Script automaticky:
- Nainštaluje potrebné závislosti
- Vytvorí virtual environment
- Nastaví systemd service
- Nakonfiguruje cron job pre scraping
- Nastaví firewall
- Voliteľne nakonfiguruje nginx

### 3. Overenie inštalácie

```bash
# Skontrolujte stav služby
sudo systemctl status tv-monitor

# Skontrolujte logy
sudo journalctl -u tv-monitor -f

# Test API
curl http://localhost:5001/api/health
```

## 📡 API Endpoints

### Health Check
```bash
GET /api/health
```

### Programy
```bash
# Aktuálne vysielané programy
GET /api/programs/current

# Všetky programy
GET /api/programs/all
```

### Subscriptions
```bash
# Prihlásiť sa na notifikácie
POST /api/subscribe
{
  "program_title": "Susedia",
  "webhook_url": "https://your-webhook.com/notifications"
}

# Odhlásiť sa z notifikácií
POST /api/unsubscribe
{
  "program_title": "Susedia", 
  "webhook_url": "https://your-webhook.com/notifications"
}

# Zobraziť všetky subscriptions
GET /api/subscriptions
```

### Monitoring
```bash
# Spustiť monitoring
POST /api/monitoring/start

# Zastaviť monitoring
POST /api/monitoring/stop

# Stav monitoringu
GET /api/monitoring/status
```

### Logy
```bash
# Získať logy notifikácií
GET /api/logs?limit=100
```

## 🎯 Použitie

### 1. Prihlásiť sa na notifikácie

```python
import requests

# Prihlásiť sa na program "Susedia"
response = requests.post('http://your-ec2-ip:5001/api/subscribe', json={
    "program_title": "Susedia",
    "webhook_url": "https://your-webhook.com/tv-notifications"
})
```

### 2. Webhook endpoint

Vytvorte webhook endpoint, ktorý bude prijímať notifikácie:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/tv-notifications', methods=['POST'])
def receive_notification():
    data = request.get_json()
    
    program = data['program']
    print(f"Program {program['title']} začína na {program['channel']} o {program['start']}")
    
    # Vaša logika - email, SMS, push notifikácie, atď.
    
    return {"status": "received"}, 200

app.run(host='0.0.0.0', port=8000)
```

### 3. Automatické spustenie scraper-a

Scraper sa spúšťa automaticky každú hodinu cez cron job:
```bash
# Skontrolovať cron job
crontab -l

# Manuálne spustenie
cd /home/ubuntu/tv-monitor && ./venv/bin/python scraper.py
```

## 🔧 Konfigurácia

### Zmena portu API
Upravte `tv_monitor_api.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=False)
```

### Zmena frekvencie monitoringu
Upravte `tv_monitor_api.py`:
```python
# Namiesto každú minútu, každých 5 minút
schedule.every(5).minutes.do(self.check_programs)
```

### Zmena frekvencie scrapingu
Upravte cron job:
```bash
crontab -e
# Namiesto každú hodinu, každých 30 minút
*/30 * * * * cd /home/ubuntu/tv-monitor && ./venv/bin/python scraper.py
```

## 🛡️ Bezpečnosť

### Firewall
```bash
# Povoliť len potrebné porty
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp   # nginx
sudo ufw allow 5001/tcp # API (ak nginx nie je používaný)
```

### SSL/HTTPS s Let's Encrypt
```bash
# Nainštalovať certbot
sudo apt install certbot python3-certbot-nginx

# Získať SSL certifikát
sudo certbot --nginx -d your-domain.com

# Automatické obnovenie
sudo crontab -e
# Pridať: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring a logy

### Service logy
```bash
# Real-time logy
sudo journalctl -u tv-monitor -f

# Posledných 100 riadkov
sudo journalctl -u tv-monitor -n 100
```

### API logy
```bash
# API logy
tail -f /home/ubuntu/tv-monitor/tv_monitor.log

# Scraper logy
tail -f /home/ubuntu/tv-monitor/logs/scraper.log
```

### Databáza
```bash
# Pripojiť sa k SQLite databáze
sqlite3 /home/ubuntu/tv-monitor/tv_monitor.db

# Zobraziť subscriptions
SELECT * FROM subscribers WHERE active = 1;

# Zobraziť notification logs
SELECT * FROM notification_logs ORDER BY sent_at DESC LIMIT 10;
```

## 🔄 Údržba

### Reštart služby
```bash
sudo systemctl restart tv-monitor
```

### Update kódu
```bash
cd /home/ubuntu/tv-monitor
git pull  # ak používate git
sudo systemctl restart tv-monitor
```

### Zálohovanie databázy
```bash
# Vytvorenie zálohy
cp tv_monitor.db tv_monitor.db.backup

# Automatická záloha (pridať do cron)
0 2 * * * cp /home/ubuntu/tv-monitor/tv_monitor.db /home/ubuntu/tv-monitor/backups/tv_monitor_$(date +\%Y\%m\%d).db
```

## 🐛 Riešenie problémov

### Služba sa nespúšťa
```bash
# Skontrolovať logy
sudo journalctl -u tv-monitor -f

# Skontrolovať konfiguráciu
sudo systemctl status tv-monitor

# Manuálne spustenie pre debuggovanie
cd /home/ubuntu/tv-monitor
./venv/bin/python tv_monitor_api.py
```

### API neodpovedá
```bash
# Skontrolovať či beží na porte
sudo netstat -tlnp | grep :5001

# Skontrolovať firewall
sudo ufw status

# Test lokálne
curl http://localhost:5001/api/health
```

### Scraper nezíska dáta
```bash
# Manuálne spustenie
cd /home/ubuntu/tv-monitor
./venv/bin/python scraper.py

# Skontrolovať internet pripojenie
ping tv-program.sk

# Skontrolovať logy
tail -f logs/scraper.log
```

## 📞 Podpora

Pre otázky a problémy:
1. Skontrolujte logy služby
2. Overte internet pripojenie
3. Skontrolujte firewall nastavenia
4. Manuálne otestujte API endpoints

## 📄 Licencia

MIT License - použiteľné pre komerčné aj nekomerčné účely.