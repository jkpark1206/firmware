from scrapy import Spider
from scrapy.http import Request

from ..items import FirmwareImage
from ..loader import FirmwareLoader

import json
import urllib.request, urllib.parse, urllib.error


class UbiquitiSpider(Spider):
    name = "ubiquiti"
    allowed_domains = ["ubnt.com", "ui.com"]
    # start_urls = ["http://www.ubnt.com/download/"]
    start_urls = [f"https://download.svc.ui.com/v1/downloads?page={i}" for i in range(1,26)]
    header = {"Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Referer": "https://www.ui.com/download/",
                "Host": "www.ui.com",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0",
                "TE": "Trailers",
                "x-amz-cf-id": "zmyqngir36zKfndolQkvlfQpTBENCZRCen-sHHMsxoA4eZ56MSO8Cw==",
                "x-amz-cf-pop": "NRT57-C1",
                "x-request-id": "2a11ba5e-d053-49ed-9de0-6ff3496cdbcd",
                "set-cookie": "AWSALB=+w5eIAOKHCUBA4OshpZFde9tKx+jyTjjJ46vXgyWu5UHuDWMGn1xXoUiO6dVUf4BFkpvK/dI8HKpvS0/HSyOT8RJZIbz38OKH+29RwHUJKnnayY9prqabPeWqRuu; Expires=Fri, 19 Jan 2024 12:37:32 GMT; Path=/",
                "X-Requested-With": "XMLHttpRequest"}

    def parse(self, response):
        # self.logger.debug(response.body)
        if hasattr(response, 'body_as_unicode'):
            json_response = json.loads(response.body_as_unicode())
        else:
            json_response = json.loads(response.body)
        s1 = json.dumps(json_response)
        data = json.loads(s1)
        for it in data["downloads"]:
            if "firmware" in it["slug"]:
                date = it["date_published"]
                product = it["name"]
                version = it["version"]
                url = it["file_path"]
                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_value("url", url)
                item.add_value("product", product)
                item.add_value("date", date)
                item.add_value("version", version)
                item.add_value("vendor", self.name)
                yield item.load_item()
        '''
        if "products" in json_response:
            for product in json_response["products"]:
                yield Request(
                    url=urllib.parse.urljoin(
                        response.url, "?product=%s" % (product["slug"])),
                    headers={"Referer": response.url,
                             "X-Requested-With": "XMLHttpRequest"},
                    meta={"product": product["slug"]},
                    callback=self.parse_json)

        if "url" in response.meta:
            item.add_value("url", response.meta["url"])
            item.add_value("product", response.meta["product"])
            item.add_value("date", response.meta["date"])
            item.add_value("description", response.meta["description"])
            item.add_value("build", response.meta["build"])
            item.add_value("version", response.meta["version"])
            item.add_value("sdk", json_response["download_url"])
            item.add_value("vendor", self.name)
            #yield item.load_item()

        elif "product" in response.meta:
            for entry in json_response["downloads"]:
                if entry["category__slug"] == "firmware":

                    if entry["sdk__id"]:
                        yield Request(
                            url=urllib.parse.urljoin(
                                response.url, "?gpl=%s&eula=True" % (entry["sdk__id"])),
                            headers={"Referer": response.url,
                                     "X-Requested-With": "XMLHttpRequest"},
                            meta={"product": response.meta["product"], "date": entry["date_published"], "build": entry[
                                "build"], "url": entry["file_path"], "version": entry["version"], "description": entry["name"]},
                            callback=self.parse_json)
                    else:
                        item = FirmwareLoader(
                            item=FirmwareImage(), response=response, date_fmt=["%Y-%m-%d"])
                        item.add_value("url", entry["file_path"])
                        item.add_value("product", response.meta["product"])
                        item.add_value("date", entry["date_published"])
                        item.add_value("description", entry["name"])
                        item.add_value("build", entry["build"])
                        item.add_value("version", entry["version"])
                        item.add_value("vendor", self.name)
                        #yield item.load_item()
        '''
