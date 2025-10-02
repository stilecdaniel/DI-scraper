from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import os
import pandas as pd
from datetime import date

urls = ['https://tv-program.sk/dajto/', 'https://tv-program.sk/prima-sk/', 'https://tv-program.sk/markiza-krimi/']
filename = "shows.csv"


def scrape(url: str) -> pd.DataFrame:
    collected_shows = []

    html = urlopen(url)

    soup = BeautifulSoup(html, 'lxml')

    # list of tv shows
    programme_list = soup.find("div", {"class": "programme-list"})

    # tv shows time schedule
    time = programme_list.find_all("time", {"class": "programme-list__time"})

    # tv shows names
    prog_names = programme_list.find_all("a", {"class": "programme-list__title"})
    # print(time, prog_names)

    for film in zip(prog_names, time):
        # print(film[1].get_text(strip=True), " ", film[0].get_text(strip=True), end='\n')

        detail_page_html = urlopen('https://tv-program.sk' + film[0]['href'])
        detail_page = BeautifulSoup(detail_page_html, 'lxml')

        show_info = detail_page.find("div", {"class": "adspace-program-detail"})
        year = None
        for i in show_info.find_all("span", {"class": "text-muted"}):
            regex_match = re.match(r"^\d{4}$", i.get_text(strip=True))
            if regex_match:
                year = regex_match.group(0)

        collected_shows.append(
            {"channel": url.rstrip("/").split("/")[-1], "date": date.today(), "start": film[1].get_text(strip=True),
             "title": film[0].get_text(strip=True), "year": year})
    return pd.DataFrame(collected_shows)


if __name__ == "__main__":

    for url in urls:
        df = scrape(url)
        df.to_csv(filename, mode="a", header=not os.path.exists(filename), index=False, encoding="utf-8")
