import os
import json
import logging

_logger = logging.getLogger(__name__)


def verifyDumpDir():
    if not os.path.exists("database"):
        os.mkdir("database")


def dumpData(data, filename):
    filepath = os.path.join("database", filename)
    with open(filepath, "w") as fp:
        fp.write(json.dumps(data, indent=4))
        _logger.info(f"Saved data to {filepath}")
