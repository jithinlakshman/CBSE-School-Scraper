from jithin.driver import Driver
from jithin.parser import RegionInfoParser
from jithin.dump import verifyDumpDir, dumpData

import logging
logging.basicConfig(level=logging.INFO, format='[%(name)s] [%(levelname)s] %(message)s')


CHROMEDRIVER_PATH = "./chromedriver"


class Scraper(object):
    def __init__(self):
        self._driver = Driver(CHROMEDRIVER_PATH)
        verifyDumpDir()

    def run(self):
        self._driver.configureOpts()
        self._driver.launch()
        self._driver.reset()

        for region in self._driver.getRegions():
            parser = RegionInfoParser(region)
            self._driver.selectRegion(region)
            for page in self._driver.iterateOverPages():
                parser.parseAndAppend(page)

            dumpData(parser.data, f"{region.lower()}.json")
            self._driver.reset()


def main():
    s = Scraper()
    s.run()


if __name__ == "__main__":
    main()
