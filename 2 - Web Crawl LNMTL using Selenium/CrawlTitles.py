# Install selenium:
#       pip install selenium
# Install pandas:
#       pip install pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

class NovelScraper:
    def __init__(self):
        self.driver = None
    
    def driver_mount(self):
        self.driver = webdriver.Chrome()
    
    def driver_unmount(self):
        self.driver.quit()

    def scrape_novels(self, url, df=None):
        self.url = url
        print("URL: ", self.url)
        self.driver.get(self.url)

        novels = self.driver.find_elements(By.CLASS_NAME, "media")

        if df is None:
            self.novel_df = pd.DataFrame(columns=['Author', 'Title', 'Number of Bookmarks', 'Date Started'])
        else:
            self.novel_df = df
        
        for novel in novels:
            author = novel.find_element(By.XPATH, './/h4/a').text
            title = novel.find_element(By.XPATH, './/p/a/span').text
            bookmarks = novel.find_element(By.XPATH, './/p/span[1]').text
            date_started = novel.find_element(By.XPATH, './/p/span[2]').text

            novel_details = {
                "Author": author,
                "Title": title,
                "Number of Bookmarks": bookmarks,
                "Date Started": date_started
            }

            self.novel_df = pd.concat([self.novel_df, pd.DataFrame([novel_details])], ignore_index=True)
        return self.novel_df
    
    def scrape_novels_in_range(self, url="https://lnmtl.com/novel", suffix= "?page=", num_of_pages=4):
        self.novel_df = pd.DataFrame(columns=['Author', 'Title', 'Number of Bookmarks', 'Date Started'])
        for i in range(num_of_pages):
            temp_url = f"{url}{suffix}{i+1}"
            self.novel_df = self.scrape_novels(temp_url, self.novel_df)
        return self.novel_df


if __name__ == "__main__":
    # Usage
    url = "https://lnmtl.com/novel"
    scraper = NovelScraper()
    scraper.driver_mount()
    # novel_data = scraper.scrape_novels(url)
    # print(novel_data)
    novel_data2 = scraper.scrape_novels_in_range(url, "?page=")
    print(novel_data2)
    scraper.driver_unmount()
