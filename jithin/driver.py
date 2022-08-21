from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException

import logging
import re

_logger = logging.getLogger(__name__)

URL = "http://saras.cbse.gov.in/cbse_aff/schdir_Report/userview.aspx"


class Driver(object):
    def __init__(self, execPath="bin/chromedriver"):
        self._opts = ChromeOptions()
        self._driver = None
        self._execPath = execPath
        self._totalSchools = None

    def configureOpts(self):
        _logger.info("Configuring driver")
        self._opts.add_argument("--headless")

    def launch(self):
        _logger.info("Starting")
        self._driver = Chrome(executable_path=self._execPath, options=self._opts)

    def reset(self):
        self._driver.get(URL)
        self._totalSchools = None

    def getRegions(self):
        radioButton = WebDriverWait(self._driver, 10).until(EC.visibility_of_element_located((By.ID, "optlist_3")))
        radioButton.click()
        dropDown = WebDriverWait(self._driver, 10).until(EC.visibility_of_element_located((By.ID, "ddlitem")))

        regions = []
        for option in dropDown.find_elements_by_tag_name("option"):
            regionName = option.text.strip()
            if re.match(r'^([A-Za-z])+$', regionName):
                regions.append(regionName)
        return regions

    def selectRegion(self, name):
        _logger.info("Selecting region")
        radioButton = WebDriverWait(self._driver, 10).until(EC.visibility_of_element_located((By.ID, "optlist_3")))
        radioButton.click()
        WebDriverWait(self._driver, 10).until(EC.visibility_of_element_located((By.ID, "ddlitem")))

        WebDriverWait(self._driver, 10).until(EC.visibility_of_element_located((By.ID, "ddlitem")))
        self._driver.find_element_by_xpath(f"//select[@id='ddlitem']/option[text()='{name}']").click()
        self._driver.find_element_by_xpath("//input[@id='search']").click()

    def iterateOverPages(self):
        _logger.info("Starting to scrape data")
        pageNo = 0
        # Scrape every page till end
        while True:
            try:
                # Wait for table to load
                page = WebDriverWait(self._driver, 10).until(EC.visibility_of_element_located((By.ID, "p1")))

                # Get number of total schools
                if self._totalSchools is None:
                    self._totalSchools = int(self._driver.find_element_by_id("tot").text)
                    _logger.info(f"Total schools found: {self._totalSchools}")

                yield page.get_attribute('innerHTML')

                # Try to go to next page
                nextButton = WebDriverWait(self._driver, 10).until(EC.visibility_of_element_located((By.ID, "Button1")))
                nextButton.send_keys(Keys.ENTER)

            except ElementNotInteractableException:
                _logger.warning("Button not clickable. Abort scraping")
                break
            except TimeoutException:
                _logger.error("Took too much time ( > 10s)", exc_info=True)
                break
            except Exception as e:
                _logger.error("Uncaught exception", exc_info=True)
            else:
                pageNo += 1
                _logger.info(f"Scraped page {pageNo}")

        _logger.info("Done scraping")

    def __del__(self):
        if self._driver.session_id:
            self._driver.close()
            self._driver.quit()
