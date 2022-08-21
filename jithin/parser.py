from bs4 import BeautifulSoup
import logging
import itertools
import re


_logger = logging.getLogger(__name__)


def parseTableHtml(string):
    schoolData = {}
    soup = BeautifulSoup(string, "html.parser")
    rows = soup.find_all("table", attrs={"align": "center", "width": "100%", "border": "0", "cellpadding": "1", "cellspacing": "1"})

    for row in rows:
        boxLeft, boxRight, *_ = map(lambda x: x.find_all("td"), row.find_all("table", attrs={"align": "left"}))

        for field in itertools.chain(boxLeft, boxRight):
            title = field.find("b").extract().text.strip().rstrip(":")
            data = field.text.strip()
            if "Website:" in data:
                emailRegex = r'(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))'
                match = re.search(emailRegex, data)
                if match is not None:
                    schoolData["Email"] = str(match.group())
                    data = re.sub(emailRegex, '', data)
                else:
                    schoolData["Email"] = ""
                data = re.sub(r'Website:', '', data)
                data = data.strip()
                schoolData["Website"] = data
            else:
                data = re.sub(r'[\t\n]+', '', data)
                schoolData[title] = data

        yield schoolData.copy()
        schoolData.clear()


class RegionInfoParser(object):
    def __init__(self, regionName):
        self._data = []
        self._name = regionName
        _logger.info(f"Parser active for {regionName}")

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self._data

    def parseAndAppend(self, string):
        for school in parseTableHtml(string):
            self._data.append(school)

        _logger.info(f"Parsed info about {len(self._data)} schools")