from time import asctime
from pyppeteer import launch
import asyncio


class ScrapperClass:
    
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.__create__())
        super().__init__()

    async def __create__(self):
        self.browser = await launch(
            args=[
                '--no-sandbox'
            ],
            handleSIGINT=False, 
            handleSIGTERM=False, 
            handleSIGHUP=False, )
        self.page = await self.browser.newPage()
            

    async def goToPage(self, link):
        await self.page.goto(
            link,
            {
                "waitUntil": "load",
                "timeout": 0
            }  
        )
    
    async def runCommand(self, command):
        self.data = await self.page.evaluate(command)


    async def __closeDriver__(self):
        await self.browser.close()

    def closeDriver(self):
        self.loop.run_until_complete(self.browser.close())

    def getDataWithLink(self, link, command):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.goToPage(link))
        self.loop.run_until_complete(self.runCommand(command))
