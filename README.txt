# ⚽ EPL Star Player Impact Analysis (2023-2024)

## 📊 Project Overview
Does a team actually perform better when their star player starts? This project scrapes data for the 2023/24 English Premier League season to quantify the "Win Rate Differential" of Top 10 attackers (e.g., Haaland, Salah, Palmer).

**Key Finding:** Ollie Watkins (Aston Villa) had the highest impact (+54% Win Rate Increase), while Man City stars showed negative differentials due to squad rotation in easier fixtures.

## 🛠️ Tech Stack
* **Python:** `soccerdata`, `pandas` for scraping & cleaning.
* **Data Processing:** Custom pipeline to merge Player Logs with Team Schedule (handling 380+ matches).
* **Visualization:** Tableau (Dashboarding) & Matplotlib.

## 📊 Visualization
Here is the final impact analysis dashboard generated from the data:

![Win Rate Impact Chart](dashboard_screenshot.png)

*Figure 1: Diverging bar chart showing the Win Rate Differential for top EPL scorers. Blue indicates positive impact; Orange indicates the team wins more often when the player is absent (often due to rotation in easier games).*

## 🚀 How to Run
1. Install dependencies: `pip install soccerdata pandas matplotlib seaborn`
2. Run scraper: `python scraper.py`

3. Run analysis: `python analysis.py`
