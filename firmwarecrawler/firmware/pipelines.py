import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.parse
import urllib.request

from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.pipelines.files import FilesPipeline


logger = logging.getLogger(__name__)
sys.path.append(os.path.abspath(".."))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firmwarecrawler.settings')
import django
django.setup()


class FirmwarePipeline(FilesPipeline):
    def __init__(self, store_uri, download_func=None, settings=None):
        super(FirmwarePipeline, self).__init__(store_uri, download_func, settings)

    @classmethod
    def from_settings(cls, settings):
        store_uri = settings['FILES_STORE']
        cls.expires = settings.getint('FILES_EXPIRES')
        cls.files_urls_field = settings.get('FILES_URLS_FIELD')
        cls.files_result_field = settings.get('FILES_RESULT_FIELD')

        return cls(store_uri, settings=settings)

    # overrides function from FilesPipeline
    def file_path(self, request, response=None, info=None):
        filename = os.path.basename(urllib.parse.urlsplit(request.url).path)
        return "%s/%s" % (request.meta["vendor"], filename)

    # overrides function from FilesPipeline
    def get_media_requests(self, item, info):
        # check for mandatory fields
        for x in ["vendor", "url"]:
            if x not in item:
                raise DropItem(
                    "Missing required field '%s' for item: " % x)

        # resolve dynamic redirects in urls
        for x in ["mib", "sdk", "url"]:
            if x in item:
                split = urllib.parse.urlsplit(item[x])
                # remove username/password if only one provided
                if split.username or split.password and not (split.username and split.password):
                    item[x] = urllib.parse.urlunsplit(
                        (split[0], split[1][split[1].find("@") + 1:], split[2], split[3], split[4]))

                if split.scheme == "http":
                    item[x] = urllib.request.urlopen(item[x]).geturl()

        # check for filtered url types in path
        url = urllib.parse.urlparse(item["url"])
        if any(url.path.endswith(x) for x in [".pdf", ".php", ".txt", ".doc", ".rtf", ".docx", ".htm", ".html", ".md5", ".sha1", ".torrent"]):
            raise DropItem("Filtered path extension: %s" % url.path)
        elif any(x in url.path for x in ["driver", "utility", "install", "wizard", "gpl", "login"]):
            raise DropItem("Filtered path type: %s" % url.path)

        # generate list of url's to download
        item[self.files_urls_field] = [item[x].replace("ftp://FTP2.DLINK.COM/", "https://support.dlink.com/resource/").replace("ftp://ftp2.dlink.com/", "https://support.dlink.com/resource/")
                                       for x in ["mib", "url"] if x in item]
        

        # pass vendor so we can generate the correct file path and name
        return [Request(x, meta={"ftp_user": "anonymous", "ftp_password": "chrome@example.com", "vendor": item["vendor"]}) for x in item[self.files_urls_field]]

    # overrides function from FilesPipeline
    def item_completed(self, results, item, info):
        item[self.files_result_field] = []
        if isinstance(item, dict) or self.files_result_field in item.fields:
            item[self.files_result_field] = [x for ok, x in results if ok]


        status = {}
        for ok, x in results:
            for y in ["mib", "url", "sdk"]:
                # verify URL's are the same after unquoting
                if ok and y in item and urllib.parse.unquote(item[y]) == urllib.parse.unquote(x["url"]):
                    status[y] = x
                elif y not in status:
                    status[y] = {"checksum": None, "path": None}
        logger.warning(f"===============================================results:{results}, item: {item}, status:{status}")
        # if not status["url"]["path"]:
        #     logger.warning("Empty filename for image: %s!" % item)
        #     return item
        from scraper.models import Firmware
        # if not Firmware.objects.filter(url_hash=status["mib"]["checksum"]).exists():
        for file_info in item['files']:
            if not Firmware.objects.filter(file_path=file_info["path"]).exists():
                Firmware.objects.create(
                    vendor=item["vendor"],
                    url=item['url'],
                    url_hash=file_info.get('checksum') or item['url'],
                    description=item.get("description", ''),
                    product=item.get("product", ''),
                    version=item.get("version", ''),
                    file_path=file_info["path"],
                    device_class=item.get('device_class', '')
                )

        return item
