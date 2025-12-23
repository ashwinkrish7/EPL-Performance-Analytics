import soccerdata as sd

# Initialize the scraper
fbref = sd.FBref(leagues="ENG-Premier League", seasons="2324")

print("♻️ Force updating the match schedule to remove dead links...")
# This forces the library to re-download the schedule and remove the broken "Ghost Match"
fbref.read_schedule(force_cache=True)

print("✅ Schedule updated! You can now run your main script again.")