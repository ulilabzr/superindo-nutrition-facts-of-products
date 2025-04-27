from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

def setup_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    return webdriver.Chrome(options=options)

def get_top_movies_with_synopsis(driver, jumlah=5):
    driver.get("https://www.imdb.com/chart/top/")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item"))
    )
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    movie_elements = soup.select('li.ipc-metadata-list-summary-item')
    
    data_list = []

    for i, movie in enumerate(movie_elements[:jumlah]):
        title = movie.select_one('h3.ipc-title__text').text
        year = movie.select_one('span.sc-5179a348-7').text
        rating = movie.select_one('span.ipc-rating-star').text
        link = movie.select_one('a.ipc-title-link-wrapper')['href']
        full_url = "https://www.imdb.com" + link

        driver.get(full_url)
        time.sleep(2)
        
        synopsis = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.sc-865706aa-3'))
        ).text

        data_list.append({
            'Title': title,
            'Year': year,
            'Rating': rating,
            'URL': full_url,
            'Synopsis': synopsis
        })

        driver.back()
        time.sleep(1)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item"))
        )

    return data_list

def main():
    driver = setup_driver()
    print("Mengambil daftar film Top 250 beserta sinopsis...")
    movies_data = get_top_movies_with_synopsis(driver, jumlah=5)
    df = pd.DataFrame(movies_data)
    print("\nHasil:")
    print(df[['Title', 'Year', 'Rating', 'Synopsis']])
    driver.quit()
    print("\nScraping selesai.")

main()