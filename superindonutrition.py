from webdriver_manager.chrome import ChromeDriverManager
from scrapy import Selector
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import random

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
    driver = getdriver()
    driver.maximize_window()
    
    item_links = []
    total_pages = 12  # We know there are 12 pages
    
    # Process each page sequentially
    for page_num in range(total_pages):
        # For first page, use base URL
        if page_num == 0:
            page_url = 'https://www.fatsecret.co.id/kalori-gizi/search?q=SuperIndo'
        else:
            # For subsequent pages, use pg parameter
            page_url = f'https://www.fatsecret.co.id/kalori-gizi/search?q=SuperIndo&pg={page_num}'
        
        print(f"Processing page {page_num + 1}/{total_pages}: {page_url}")
        driver.get(page_url)
        time.sleep(3)  # Wait for the page to load
        
        # Process current page and extract product links
        response = Selector(text=driver.page_source)
        links = response.xpath("//a[contains(@href, '/kalori-gizi/superindo/')]/@href").getall()
        
        # Filter links to ensure they are product links
        product_links = [link for link in links if '/100g' in link or '/buah' in link or '/takaran' in link or '/porsi' in link]
        
        # Process each product on the current page immediately
        page_links_processed = 0
        for link in product_links:
            if link not in item_links:  # Avoid duplicates
                item_links.append(link)
                
                # Process this product immediately
                item_url = 'https://www.fatsecret.co.id' + link
                print(f"  Scraping product: {item_url}")
                
                driver.get(item_url)
                time.sleep(2)  # Wait for product page to load
                
                item_response = Selector(text=driver.page_source)
                
                # Extract item name
                item_name = item_response.xpath("//h1/text()").get()
                if item_name:
                    item_name = item_name.strip()
                else:
                    item_name = 'Unknown'
                
                # Extract nutrition values
                cal = item_response.xpath("//div[contains(text(),'Kalori')]/following-sibling::div/text()").get()
                if not cal:
                    cal = item_response.xpath("//div[contains(text(),'Kal')]/following-sibling::div/text()").get()
                
                fat = item_response.xpath("//div[contains(text(),'Lemak')]/following-sibling::div/text()").get()
                carb = item_response.xpath("//div[contains(text(),'Karbohidrat')]/following-sibling::div/text()").get()
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
                
                # Get serving size info
                serving_info = item_response.xpath("//div[@class='serving_size black serving_size_value']/text()").get()
                if not serving_info:
                    serving_info = ""
                else:
                    serving_info = clean_value(serving_info)
                
                data = {
                    'item_name': item_name,
                    'serving_info': serving_info,
                    'calories': cal,
                    'fat': fat,
                    'carbohydrates': carb,
                    'protein': protein,
                    'url': item_url,
                    'page': page_num + 1  # Record which page this item was found on
                }
                
                print(f"    Scraped: {item_name}")
                exporter(data)
                page_links_processed += 1
        
        print(f"Completed page {page_num + 1}: processed {page_links_processed} products")
        # Return to the search results page for the next iteration
        
    print(f"Scraping completed. Total unique products found: {len(item_links)}")
    driver.quit()

if __name__ == "__main__":
    scrape_superindo_nutrition()