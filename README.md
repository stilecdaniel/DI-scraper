# Slovak TV Scraper

This project scrapes daily TV programs from [tv-program.sk](https://tv-program.sk) for Slovak TV channels like **Dajto**, **Prima SK**, and **Markíza Krimi**.  

The scraper collects:

- Channel name  
- Date  
- Start time  
- Show title  
- Year of production (if available)  

and saves it into a CSV file for further analysis or use in APIs.

## ⚡ Setup

1. Make sure Python 3.10+ is installed.  
2. Install dependencies:

```bash
pip install -r requirements.txt
```
3. Run the scraper manually:
```bash
python scraper.py
```
## 📄 Example CSV output
| channel | date       | start | title         | year |
| ------- | ---------- | ----- | ------------- | ---- |
| dajto   | 2025-10-02 | 05:05 | Oggy a šváby  | 2021 |
| dajto   | 2025-10-02 | 06:00 | Je to možné?! |      |
| dajto   | 2025-10-02 | 06:55 | Susedia       | 2019 |

## 🤖 GitHub Actions Automation

The scraper is fully automated with GitHub Actions:

- Workflow file: .github/workflows/scraper.yml

- Schedule: Daily at 06:00 Slovakia time
