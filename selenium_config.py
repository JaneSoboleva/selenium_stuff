from selenium import webdriver
from selenium.webdriver.chrome.options import Options

local_folder = 'C:/download/test_downloader/fanbox/stuff_downloads_here/'
simultaneous_tasks = 5
chrome_options = Options()
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox") # linux only
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
