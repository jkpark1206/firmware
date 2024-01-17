BOT_NAME = "firmwarecrawler"

SPIDER_MODULES = ["firmwarecrawler.firmware.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

DOWNLOAD_HANDLERS = {
    's3': None,
}

ITEM_PIPELINES = {
    "firmwarecrawler.firmware.pipelines.FirmwarePipeline": 1,
}

FILES_STORE = "output/"

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0
AUTOTHROTTLE_MAX_DELAY = 500
CONCURRENT_REQUESTS = 8

DOWNLOAD_TIMEOUT = 12000
DOWNLOAD_MAXSIZE = 0
DOWNLOAD_WARNSIZE = 0

ROBOTSTXT_OBEY = False
USER_AGENT = "FirmwareBot/1.0 (+https://github.com/firmadyne/scraper)"

#SQL_SERVER = "127.0.0.1"

LOG_FILE = "./test.log"
MEDIA_ALLOW_REDIRECTS = True
