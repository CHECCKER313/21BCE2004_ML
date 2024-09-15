import threading
import requests
import time

def scrape_data():
    while True:
        # Example scraping function (replace the URL with your target)
        response = requests.get("https://newsapi.org/v2/top-headlines?apiKey=YOUR_API_KEY")
        if response.status_code == 200:
            data = response.json()
            # Process and store the data (you can add your logic here)
            print("Scraped Data:", data)
        else:
            print("Failed to scrape data")

        # Sleep for 1 hour (3600 seconds) before scraping again
        time.sleep(3600)

def start_scraping_thread():
    thread = threading.Thread(target=scrape_data)
    thread.daemon = True
    thread.start()
