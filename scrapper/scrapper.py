from selenium import webdriver
from selenium.webdriver.firefox.options import Options

class ScrapperClass:

    def __init__(self) -> None:
        options = Options()
        options.headless = True

        driverPath = ""

        from sys import platform
        if platform == "linux" or platform == "linux2":
            driverPath = "geckodriver"
        elif platform == "win32":
            driverPath = "geckodriver.exe"

        self.driver = webdriver.Firefox(executable_path=driverPath, options=options)
        super().__init__()

    def closeDriver(self):
        self.driver.close()


