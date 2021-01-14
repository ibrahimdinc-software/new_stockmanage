from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class ScrapperClass:

    def __init__(self) -> None:
        options = Options()
        options.headless = True

        self.driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options)
        super().__init__()

    def closeDriver(self):
        self.driver.close()


