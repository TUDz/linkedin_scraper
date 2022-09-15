from re import X
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from scrapy.selector import Selector
import pandas as pd
from utils import SIGNIN_BUTTON, USERNAME, PASS
from utils import LOGGING_BUTTON, USERNAME_INPUT, PASSWORD_INPUT
from utils import save_db_to_gsheets
from time import sleep
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

KEY_WORDS = ["Busco proveedor Nom-035"] # "BUSCO PROVEEDOR RH", "BUSCO PROVEEDOR NOMINA"
DEFAULT_URL = "https://www.linkedin.com/feed/?trk=guest_homepage-basic_nav-header-signin"
NON_INTEREST_WORDS = ["BÚSQUEDA ACTIVA DE EMPLEO", "BÚSQUEDA ACTIVA DE EMPLEO", "BUSCO EMPLEO", "BUSCO TRABAJO", "ESTOY DESEMPLEADO"]

names = []
titles = []
contents = []
urls = []

def scrap_key_words(driver: webdriver.Firefox, word: str):
    driver.get(DEFAULT_URL)
    sleep(7)
    driver.find_element(By.XPATH, '//input[@placeholder="Search"]').click()
    sleep(5)
    driver.find_element(By.XPATH, '//input[@placeholder="Search"]').send_keys(word)
    sleep(5)
    driver.find_element(By.XPATH, '//div[@id="triggered-expanded-ember14"]').click()
    sleep(5)
    driver.find_elements(By.XPATH, '//ul[contains(@class, "reusable-search__entity-result-list")]/li')[0]
    sleep(5)
    sel = Selector(text=driver.page_source)
    posts = sel.xpath('//div[contains(@class, "entity-result__content-container")]')

    if posts:
        i = 1
        for post in posts:
            print(f'Post {i}')
            # Name
            names.append(post.xpath('.//span[@dir="ltr"]/span[not(contains(@class,"visually-hidden"))]/text()').extract_first())
            # Content
            contents.append((' '.join(post.xpath('.//p[contains(@class, "result__content-summary")]/text()').extract())).strip())
            # Puesto
            titles.append(''.join(post.xpath('.//div[contains(@class, "entity-result__primary-subtitle")]/text()').extract()).strip())
            # Raw URL
            urls.append(post.xpath('.//a[@class="app-aware-link"]/@href').extract_first())
            i += 1
    else:
        print(f"No posts found for -> {word}")

def create_final_set():
    final_set = pd.DataFrame({"Nombre": names,
                              "Empresa": '',
                              "Puesto": titles,
                              "Contenido_post": contents,
                              "Raw URL": urls,
                              "Fecha_creacion": pd.to_datetime('today')
                    })
    return final_set

def clean_set(db: pd.DataFrame):
    for non_word in NON_INTEREST_WORDS:
        db = db.drop(db[db['Contenido_post'].str.upper().str.contains(non_word)].index)

    return db

def navigate_RAW_url(driver: webdriver.Firefox, url: str):
    driver.get('url')
    sel = Selector(text=driver.page_source)
    experience_list = sel.xpath("//ul[contains(@class, 'pvs-list')]").extract_first()

    if experience_list:
        print(experience_list)

def run():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')  # Last I checked this was necessary.

    binary = FirefoxBinary('C:\Program Files\Mozilla Firefox\Firefox.exe')
    driver = webdriver.Firefox()
    driver.get('https://www.linkedin.com')
    sleep(8)

    logging_button = driver.find_elements(By.XPATH, '//a[contains(@class, "nav__button-secondary")]')[0]
    sleep(10)

    if logging_button:
        logging_button.click()
        sleep(10)

        driver.find_element(By.XPATH, USERNAME_INPUT).send_keys(USERNAME)
        driver.find_element(By.XPATH, PASSWORD_INPUT).send_keys(PASS)

        if driver.find_element(By.XPATH, SIGNIN_BUTTON):
            driver.find_element(By.XPATH, SIGNIN_BUTTON).click()
            sleep(10)

            for word in KEY_WORDS:
                scrap_key_words(driver, word)
        else:
            pass # sigin button not found
    else:
        pass # log button not found


    db = create_final_set()
    db = clean_set(db)
    ##### Final dataset with the data
    #for url in db['Raw URL'].values:
    #    navigate_RAW_url(driver, url)     

    #### -> Mandar a Excel
    ###save_db_to_gsheets(db)
    db.to_excel('RESULTS.xlsx')
    
    driver.quit()



if __name__ =="__main__":
    run()