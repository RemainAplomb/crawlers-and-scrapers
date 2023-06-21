# Install selenium:
#       pip install selenium
# Install pandas:
#       pip install pandas
# Install PIL:
#       pip install Pillow
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import requests
import io
from PIL import Image
import time

class ImageScraper:
    def __init__(self):
        self.driver = None
    
    def driver_mount(self):
        self.driver = webdriver.Chrome()
    
    def driver_unmount(self):
        self.driver.quit()

    def scroll_down(self, delay):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay)

    def scrape_images(self, url, max_images=10, delay=3):
        self.url = url
        # print("URL: ", self.url)
        self.driver.get(self.url)

        image_details = []
        image_urls = set()
        skips = 0

        while len(image_urls) + skips < max_images:
            self.scroll_down(delay)

            thumbnails = self.driver.find_elements(By.CLASS_NAME, "Q4LuWd")

            for img in thumbnails[len(image_urls) + skips:max_images]:
                try:
                    img.click()
                    time.sleep(delay)
                except:
                    continue

                images = self.driver.find_elements(By.CLASS_NAME, "iPVvYb")
                for image in images:
                    image_url = image.get_attribute('src')
                    if image_url in image_urls:
                        max_images += 1
                        skips += 1
                        break

                    if image_url and ('http' in image_url) and (('jpeg' in image_url) or ('jpg' in image_url) or ('png' in image_url)):
                        image_urls.add(image_url)
                        image_details.append({'URL': image_url, 'Saved': False})
                        print(f"Found {len(image_urls)}: {image_url}")
                
            # Check if "See more" button is available
            see_more_button = self.driver.find_element(By.LINK_TEXT, 'See more')
            if see_more_button:
                actions = ActionChains(self.driver)
                actions.move_to_element(see_more_button).click().perform()
                time.sleep(delay)
            else:
                break

        df = pd.DataFrame(image_details)
        return image_urls, df
        
    
    def download_image(self, url, file_name, download_path="./downloads/"):
        try:
            image_content = requests.get(url).content
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file)
            file_path = download_path + file_name

            with open(file_path, "wb") as f:
                image.save(f, "JPEG")

            print(f"Downloaded: {url}")
            return True
        except Exception as e:
            print('Error: ', e)
            return False


if __name__ == "__main__":
    # Usage
    DOWNLOAD_FOLDER = "./downloads/"
    IMAGE_FORMAT = "jpg"
    url = "https://www.google.com/search?q=library+of+the+heaven%27s+path&tbm=isch&ved=2ahUKEwiWwM-7-NP_AhX6MbcAHd48DngQ2-cCegQIABAA&oq=library+of+the+heaven%27s+path&gs_lcp=CgNpbWcQAzIHCAAQGBCABDoECCMQJzoFCAAQgAQ6BggAEAcQHjoICAAQgAQQsQM6BwgAEIoFEEM6CggAEIoFELEDEEM6CwgAEIAEELEDEIMBOgYIABAIEB46CQgAEBgQgAQQClD2ZViskAFgpJEBaAFwAHgAgAGXAogBii6SAQcwLjEzLjE2mAEAoAEBqgELZ3dzLXdpei1pbWfAAQE&sclient=img&ei=SbSSZNb3E_rj3LUP3vm4wAc&bih=817&biw=1707&rlz=1C1CHBF_enCA918CA918"
    scraper = ImageScraper()
    scraper.driver_mount()
    image_urls, image_df = scraper.scrape_images(url)
    print(image_urls)
    print(image_df)
    # for i, url in enumerate(image_urls):
    #     scraper.download_image(url, f"image_{str(i)}.{IMAGE_FORMAT}",DOWNLOAD_FOLDER)
    # scraper.driver_unmount()
    for i, row in image_df.iterrows():
        url = row['URL']
        file_name = f"image_{str(i)}.{IMAGE_FORMAT}"
        saved = scraper.download_image(url, file_name, DOWNLOAD_FOLDER)
        image_df.loc[i, 'Filename'] = file_name
        image_df.loc[i, 'Saved'] = saved
    scraper.driver_unmount()
    image_df.to_csv(f'{DOWNLOAD_FOLDER}image_details.csv', index=False)
