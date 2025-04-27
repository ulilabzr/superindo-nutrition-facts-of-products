from webdriver_manager.chrome import ChromeDriverManager
from scrapy import Selector
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

def getdriver():
    options = Options()
    # options.headless = True
    options.page_load_strategy = 'normal'
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    return driver

switch = True
def exporter(row):
    file_name = 'datanutrition.csv'
    global switch 
    if switch:
        switch = False
        pd.DataFrame(row,index=[0]).to_csv(file_name,index=False,mode='w')
    else:
        pd.DataFrame(row,index=[0]).to_csv(file_name,index=False,mode='a',header=False)

def scrape_superindo_nutrition():
    base_search_url = 'https://www.fatsecret.co.id/kalori-gizi/search?q=SuperIndo'
    driver = getdriver()
    driver.get(base_search_url)
    driver.maximize_window()
    time.sleep(3)

    item_links = []
    while len(item_links) < 119:
        response = Selector(text=driver.page_source)
        # Extract item links from current page
        links = response.xpath("//a[contains(@href, '/kalori-gizi/superindo/') and contains(@href, '/100g')]/@href").getall()
        # Add new unique links
        for link in links:
            if link not in item_links:
                item_links.append(link)
                if len(item_links) >= 119:
                    break

        # Try to click the "next" button if exists and more items needed
        if len(item_links) < 119:
            try:
                next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'next')]")
                if next_button.is_enabled():
                    next_button.click()
                    time.sleep(3)
                else:
                    break
            except:
                break
        else:
            break

    print(f"Found {len(item_links)} item links.")

    for link in item_links:
        item_url = 'https://www.fatsecret.co.id' + link
        driver.get(item_url)
        time.sleep(3)
        item_response = Selector(text=driver.page_source)

        # Extract item name
        item_name = item_response.xpath("//h1/text()").get()
        if item_name:
            item_name = item_name.strip()
        else:
            item_name = 'Unknown'

        # Extract nutrition summary values
        # Calories - fix extraction by checking the correct xpath or text
        cal = item_response.xpath("//div[contains(text(),'Kalori')]/following-sibling::div/text()").get()
        if not cal:
            # Alternative xpath if above fails
            cal = item_response.xpath("//div[contains(text(),'Kal')]/following-sibling::div/text()").get()

        # Fat (Lemak)
        fat = item_response.xpath("//div[contains(text(),'Lemak')]/following-sibling::div/text()").get()
        # Carbohydrates (Karbohidrat)
        carb = item_response.xpath("//div[contains(text(),'Karbohidrat')]/following-sibling::div/text()").get()
        # Protein
        protein = item_response.xpath("//div[contains(text(),'Protein')]/following-sibling::div/text()").get()

        # Clean extracted data
        def clean_value(val):
            if val:
                return val.strip()
            return ''

        cal = clean_value(cal)
        fat = clean_value(fat)
        carb = clean_value(carb)
        protein = clean_value(protein)

        data = {
            'item_name': item_name,
            'calories': cal,
            'fat': fat,
            'carbohydrates': carb,
            'protein': protein
        }

        print(f"Scraped: {data}")
        exporter(data)

    driver.quit()

if __name__ == "__main__":
    scrape_superindo_nutrition()
