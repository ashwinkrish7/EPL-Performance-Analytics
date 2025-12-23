# ⚽ EPL Star Player Impact Analysis (2023-2024)

## 📊 Project Overview
Does a team actually perform better when their star player starts? This project scrapes data for the 2023/24 English Premier League season to quantify the "Win Rate Differential" of Top 10 attackers (e.g., Haaland, Salah, Palmer).

**Key Finding:** Ollie Watkins (Aston Villa) had the highest impact (+54% Win Rate Increase), while Man City stars showed negative differentials due to squad rotation in easier fixtures.

## 🛠️ Tech Stack
* **Python:** `soccerdata`, `pandas` for scraping & cleaning.
* **Data Processing:** Custom pipeline to merge Player Logs with Team Schedule (handling 380+ matches).
* **Visualization:** Tableau (Dashboarding) & Matplotlib.

## 📈 Results
![Dashboard Analysis](Dashboard.png)
*Visualizing the Win Rate Difference (Starters vs. Absentees)*

## 🚀 How to Run
1. Install dependencies: `pip install soccerdata pandas matplotlib seaborn`
2. Run scraper: `python scraper.py`
3. Run analysis: `python analysis.py`

